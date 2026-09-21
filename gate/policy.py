# -*- coding: utf-8 -*-
"""The lane is decided here, in code, by explicit conditions.

The model's own lane answer is collected in the same request and kept, but it
is advisory. Two reasons. Failed, skipped or missing evidence never counts as
a pass - that is a hard condition, not a weight that something else can
compensate for. And a model agreeing with itself is not an approval.

Every decision reports which conditions were VERIFIED by code and which were
INFERRED by the model, because those are different kinds of claim.
"""
from __future__ import annotations
from dataclasses import dataclass, field

READY, EVIDENCE, DEEP, HOLD = ("ready_for_manual_approval", "request_evidence",
                               "deep_review", "hold")


@dataclass
class Decision:
    lane: str
    rule: str
    model_lane: str
    confidence: float
    verified: list[str] = field(default_factory=list)
    inferred: list[str] = field(default_factory=list)
    unevidenced: list[str] = field(default_factory=list)

    @property
    def agreed(self) -> bool:
        return self.lane == self.model_lane


def _noul(a, key, default=0.0):
    x = a.get(key)
    return x["noul"] if x else default


def _score(a, key, default=0.0):
    x = a.get(key)
    return x["score"] if x else default


def _certainty(a, key):
    """How sure is this one judgement of its own answer? For a yes/no that is
    distance from the coin flip; for a score the concentration of the levels."""
    x = a.get(key)
    if not x:
        return 1.0
    if "noul" in x:
        return max(x["noul"], 1.0 - x["noul"])
    return x.get("confidence", 1.0)


def decide(pr, claims, call, t_artifact=0.5, t_flag=0.5, gate=0.70) -> Decision:
    a = call.answers
    verified, inferred = [], []

    # ---- deterministic, from code. These outrank anything the model said. ----
    pending = [k for k, v in (pr.checks or {}).items() if v.upper() in ("PENDING", "QUEUED", "IN_PROGRESS")]
    failing = [k for k, v in (pr.checks or {}).items() if v.upper() in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT")]
    if not pr.checks:
        verified.append("no checks reported at all")
    if pending:
        verified.append(f"checks not finished: {', '.join(pending)}")
    if failing:
        verified.append(f"checks failing: {', '.join(failing)}")

    mk = lambda lane, rule: Decision(lane, rule, call.name, call.confidence,
                                     verified, inferred, unevidenced)

    unevidenced = [c for i, c in enumerate(claims)
                   if _noul(a, f"claim{i}.artifact") < t_artifact]
    contradicted = [c for i, c in enumerate(claims)
                    if _noul(a, f"claim{i}.scope", 1.0) < t_artifact]

    if pending:
        return mk(HOLD, "VERIFIED: checks have not reported yet")
    if failing:
        return mk(EVIDENCE, "VERIFIED: a reported check is failing")
    if not pr.checks and claims:
        return mk(EVIDENCE, "VERIFIED: claims are made but no check reported at all")

    # ---- model judgements, still applied as hard conditions ----
    if unevidenced:
        inferred.append(f"{len(unevidenced)} claim(s) carry no checkable artifact")
        return mk(EVIDENCE, "INFERRED: a claim has no artifact a reviewer could open")
    if contradicted:
        inferred.append(f"{len(contradicted)} claim(s) are not accounted for by the changed paths")
        return mk(HOLD, "INFERRED: a claim and the changed paths disagree")
    if _noul(a, "overclaim") > t_flag:
        inferred.append("the body asserts more than the evidence shows")
        return mk(EVIDENCE, "INFERRED: the body overclaims")

    sec, irr = _noul(a, "touches_security"), _noul(a, "touches_irreversible")
    if sec > t_flag or irr > t_flag:
        inferred.append(f"security {sec:.2f}, irreversible {irr:.2f}")
        return mk(DEEP, "INFERRED: the change touches security or something irreversible")

    blast, tests = _score(a, "blast_radius"), _score(a, "tests_proportionate")
    if blast >= 1.5 and tests <= 1.0:
        inferred.append(f"blast radius {blast:.2f} with verification at {tests:.2f}")
        return mk(DEEP, "INFERRED: wide reach with verification that leaves the main risk untested")

    # ---- every hard condition passed; approval is now the code's to give ----
    # Gate on the judgements the rules actually consulted, not on the model's
    # own lane answer. Asking it to synthesise a policy in one question is
    # asking for the indirection it is worst at: on a clean documentation
    # change every atomic signal came back decisive while the lane question
    # sat at 0.51. The atomic answers are the reusable part; the policy is
    # ours. Uncertainty on a branch nothing rests on is ignored.
    consulted = ([f"claim{i}.artifact" for i in range(len(claims))] +
                 [f"claim{i}.scope" for i in range(len(claims))] +
                 ["overclaim", "touches_security", "touches_irreversible",
                  "blast_radius", "tests_proportionate"])
    weak = {k: _certainty(a, k) for k in consulted if _certainty(a, k) < gate}
    if weak:
        worst = min(weak, key=weak.get)
        inferred.append(f"{worst} is only {weak[worst]:.2f} certain")
        return mk(HOLD, f"a judgement the decision rests on is below the {gate:.2f} gate")

    floor = min(_certainty(a, k) for k in consulted) if consulted else 1.0
    inferred.append(f"every consulted judgement is at least {floor:.2f} certain")
    return mk(READY, "no hard condition fired and every consulted judgement is decisive")


def report(d: Decision, call) -> str:
    L = [f"  lane      {d.lane}",
         f"  rule      {d.rule}",
         f"  model     {d.model_lane}  ({'agrees' if d.agreed else 'DIFFERS'})  "
         f"confidence {d.confidence:.2f}",
         f"  call      {call}"]
    if d.verified:
        L.append("  VERIFIED  " + "; ".join(d.verified))
    if d.inferred:
        L.append("  INFERRED  " + "; ".join(d.inferred))
    for c in d.unevidenced:
        L.append(f"  unproven  {c[:88]}")
    w = call.weakest()
    if w:
        L.append(f"  weakest   {w.name} p={w.probability:.2f}")
    return "\n".join(L)
