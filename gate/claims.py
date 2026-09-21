# -*- coding: utf-8 -*-
"""What code does before Jev is asked anything.

Exact lookups stay here: which artifacts exist, which paths changed, what the
checks reported. Jev is only asked the part that needs reading comprehension -
whether a particular artifact actually backs a particular claim.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

ARTIFACT = {
    "link":   re.compile(r"https?://\S+"),
    "fenced": re.compile(r"```[\s\S]{20,}?```"),
    "sha":    re.compile(r"\b[0-9a-f]{7,40}\b"),
    "run_id": re.compile(r"\b(?:run|job|build)[ _#-]?\d{3,}\b", re.I),
}

CLAIMY = re.compile(
    r"(pass|passed|passing|green|verified|confirm|tested|works|fixed|resolved|no regression|"
    r"covered|complete|succeeds?|benchmark|faster|通過|驗證|已測|修正|完成|無回歸|實測)", re.I)


@dataclass
class PR:
    number: int
    title: str
    body: str
    files: list[str]
    additions: int = 0
    deletions: int = 0
    checks: dict[str, str] = field(default_factory=dict)   # name -> SUCCESS / FAILURE / PENDING


def find_artifacts(body: str) -> dict[str, int]:
    return {k: len(p.findall(body)) for k, p in ARTIFACT.items()}


def extract_claims(body: str, limit: int = 6) -> list[str]:
    """Split the body into the statements a reviewer would want proof of.
    Code does the splitting so the model never judges an undifferentiated blob."""
    out: list[str] = []
    for raw in body.splitlines():
        line = re.sub(r"^\[[ xX]\]\s*", "", raw.strip().lstrip("-*+ ").strip())
        if len(line) < 12 or line.startswith(("#", "```", "|")):
            continue
        if CLAIMY.search(line):
            out.append(line[:280])
        if len(out) >= limit:
            break
    return out


# Judgements that are not lane arguments: independent signals the policy reads.
RISK_QUESTIONS = {
    "overclaim": {"type": "noul",
        "instructions": "Does the body assert a broader outcome than the changed paths and the reported checks can support?",
        "criteria": {"true": "the body claims more than what is shown",
                     "false": "the body stays within what is shown"}},
    "scope_drift": {"type": "noul",
        "instructions": "Do the changed paths include work that the title and body do not describe?",
        "criteria": {"true": "paths were changed that the description does not cover",
                     "false": "the changed paths stay inside the stated scope"}},
    "touches_security": {"type": "noul",
        "instructions": "Do the changed paths touch authentication, authorisation, secrets, credentials, permissions or cryptography?"},
    "touches_irreversible": {"type": "noul",
        "instructions": "Do the changed paths touch stored data, migrations, deployment or anything that acts outside this repository?"},
    "blast_radius": {"type": "score",
        "instructions": "How far do the changed paths reach into the running system?",
        "criteria": ["one isolated file or document that nothing depends on",
                     "a module with local callers, contained within one area",
                     "a shared interface, schema or entry point that many things depend on"]},
    "tests_proportionate": {"type": "score",
        "instructions": "Does the verification accompanying this change match what the change touches?",
        "criteria": ["no verification at all accompanies a change that needs it",
                     "some verification, but the main risk is left untested",
                     "verification matches what the change touches"]},
}


def claim_questions(claims: list[str]) -> dict:
    """One pair of judgements per claim, built fresh for this pull request -
    the same shape as a control discovered on a screen."""
    q = {}
    for i, c in enumerate(claims):
        q[f"claim{i}.artifact"] = {"type": "noul",
            "instructions": (f"The body states: {c!r}. Does the body also carry a concrete artifact "
                             "for that specific statement - pasted command output, a log excerpt, a CI "
                             "link, a commit hash or a screenshot - that a reviewer could open and check?"),
            "criteria": {"true": "a checkable artifact accompanies this specific statement",
                         "false": "the statement is asserted with nothing a reviewer could verify"}}
        q[f"claim{i}.scope"] = {"type": "noul",
            "instructions": (f"The body states: {c!r}. Is that statement consistent with the list of "
                             "changed file paths in the state?"),
            "criteria": {"true": "the changed paths could plausibly produce this outcome",
                         "false": "the changed paths do not account for what is claimed"}}
    return q


def extras(claims: list[str]) -> dict:
    return {**claim_questions(claims), **RISK_QUESTIONS}


def state_for(pr: PR, claims: list[str]) -> dict:
    return {"title": pr.title,
            "body": pr.body[:4000],
            "changed_paths": pr.files[:60],
            "change_size": {"files": len(pr.files),
                            "additions": pr.additions, "deletions": pr.deletions},
            "checks_reported": pr.checks or {"(none)": "MISSING"},
            "artifacts_counted_by_code": find_artifacts(pr.body),
            "claims_split_out_by_code": claims}
