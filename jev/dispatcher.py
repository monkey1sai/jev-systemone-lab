"""spec + typed functions -> one batched request -> a typed call.

Every command is a single request carrying the route question and every
function's arguments. Only the chosen function's answers are read; the
rest were speculative and cost almost nothing in latency.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

from .closed_sets import closed_sets, CHOICE, SET, FLAG

ROUTE = "__tool__"
STATED = "?"          # suffix of the presence question


@dataclass
class Argument:
    name: str
    value: Any
    probability: float                  # probability of the decision ACTUALLY taken
    distribution: dict[str, float] = field(default_factory=dict)
    omitted: bool = False


@dataclass
class Call:
    name: str
    tool_probability: float
    arguments: dict[str, Argument] = field(default_factory=dict)
    fn: Callable | None = None
    ms: int = 0
    answers: dict = field(default_factory=dict)   # every answer, including per-request extras

    @property
    def kwargs(self) -> dict[str, Any]:
        return {a.name: a.value for a in self.arguments.values() if not a.omitted}

    @property
    def confidence(self) -> float:
        """The least certain judgement, not the product of all of them.
        One wrong argument spoils the call; a product answers a different
        question and decays as the argument count grows."""
        return min([self.tool_probability] + [a.probability for a in self.arguments.values()])

    def weakest(self) -> Argument | None:
        return min(self.arguments.values(), key=lambda a: a.probability) if self.arguments else None

    def run(self):
        if self.fn is None:
            raise RuntimeError(f"no callable bound to {self.name!r}")
        return self.fn(**self.kwargs)

    def __str__(self):
        return f"{self.name}(" + ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items()) + ")"


class Dispatcher:
    def __init__(self, spec: dict, tools: dict[str, Callable], client, stated_threshold: float = 0.5):
        self.spec, self.tools, self.client = spec, tools, client
        self.stated_threshold = stated_threshold
        self.questions = self._build()

    # ---------- build once ----------
    def _build(self) -> dict:
        fns = self.spec.get("functions", {})
        q = {ROUTE: {"type": "choice",
                     "instructions": self.spec.get("route", "What is the user asking for?"),
                     "criteria": {n: fns[n]["description"] for n in self.tools if n in fns}}}
        for fname, fn in self.tools.items():
            argspec = fns.get(fname, {}).get("arguments", {})
            for arg, (shape, options) in closed_sets(fn).items():
                s = argspec.get(arg)
                if not s:
                    continue                      # unspecced -> no question -> default stands
                qid = f"{fname}.{arg}"
                if shape == CHOICE:
                    q[qid] = {"type": "choice", "instructions": s["question"],
                              "criteria": {k: v for k, v in s["options"].items() if k in options}}
                elif shape == FLAG:
                    q[qid] = {"type": "noul", "instructions": s["question"]}
                elif shape == SET:
                    for m in options:
                        q[f"{qid}.{m}"] = {"type": "noul", "instructions": s["question"].format(m)}
                if s.get("stated"):
                    q[qid + STATED] = {"type": "noul", "instructions": s["stated"]}
        return q

    # ---------- one request per command ----------
    def __call__(self, state, extra: dict | None = None) -> Call:
        """`extra` carries questions that only exist for this one request -
        a claim found in this PR body, a control found on this screen. They
        ride along in the same call, so they cost tokens but not a round trip."""
        questions = {**self.questions, **(extra or {})}
        return self.read(self.client.system_one(state, questions))

    def read(self, response: dict) -> Call:
        a = response["answers"]
        route = a[ROUTE]
        name = route["choice"]
        fn = self.tools.get(name)
        args: dict[str, Argument] = {}
        for arg, (shape, options) in (closed_sets(fn).items() if fn else []):
            qid = f"{name}.{arg}"
            presence = a.get(qid + STATED)
            if presence is not None and presence["noul"] <= self.stated_threshold:
                args[arg] = Argument(arg, None, 1.0 - presence["noul"], {}, omitted=True)
                continue
            if shape == CHOICE and qid in a:
                ans = a[qid]
                p = ans.get("probabilities", {})
                args[arg] = Argument(arg, ans["choice"], p.get(ans["choice"], ans.get("confidence", 0.0)), p)
            elif shape == FLAG and qid in a:
                p = a[qid]["noul"]
                args[arg] = Argument(arg, p > 0.5, max(p, 1 - p), {"true": p, "false": 1 - p})
            elif shape == SET:
                chosen, probs, worst = [], {}, 1.0
                for m in options:
                    mq = a.get(f"{qid}.{m}")
                    if mq is None:
                        continue
                    probs[m] = mq["noul"]
                    if mq["noul"] > 0.5:
                        chosen.append(m)
                    worst = min(worst, max(mq["noul"], 1 - mq["noul"]))
                if chosen:
                    args[arg] = Argument(arg, chosen, worst, probs)
        return Call(name, route.get("probabilities", {}).get(name, 1.0), args, fn,
                    response.get("_ms", 0), a)


# ---------- dynamic action space (DOM refs, game moves, ...) ----------
NO_MATCH = "__none__"

def decide(client, state, actions: dict[str, str], instructions: str,
           extra: dict | None = None,
           no_match: str = "None of the available controls is appropriate right now"):
    """Actions are discovered at runtime, so criteria are built per tick.
    A no-match outcome is always added: without it the model is forced to
    pick something from a list where nothing fits."""
    questions = {"action": {"type": "choice", "instructions": instructions,
                            "criteria": {**actions, NO_MATCH: no_match}}}
    questions.update(extra or {})
    r = client.system_one(state, questions)
    a = r["answers"]["action"]
    return a["choice"], a.get("probabilities", {}).get(a["choice"], 0.0), r
