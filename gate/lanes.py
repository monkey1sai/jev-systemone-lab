# -*- coding: utf-8 -*-
"""The four lanes, as ordinary typed functions.

Their Literal arguments are what `closed_sets` turns into questions, exactly
like the trading assistant. Nothing here knows about Jev.

Note what is deliberately NOT an argument: free text. There is no `reason: str`
anywhere, because that would be generation, and Jev does not generate. Every
fillable slot is a closed set a reviewer could have enumerated in advance.
"""
from typing import Literal

MISSING = Literal["command_output", "ci_link", "log_excerpt",
                  "commit_hash", "screenshot", "reviewer_signoff"]
AREA = Literal["auth_or_secrets", "data_or_migration", "deploy_or_infra",
               "shared_interface", "external_effect", "complex_logic"]


def ready_for_manual_approval(
    residual_risk: Literal["negligible", "ordinary", "elevated"] = "ordinary",
    needs_release_note: bool = False,
):
    """Evidence is complete. A human still presses the button."""
    return {"lane": "ready_for_manual_approval",
            "residual_risk": residual_risk, "needs_release_note": needs_release_note}


def request_evidence(
    missing: list[MISSING],
    severity: Literal["blocking", "advisory"] = "blocking",
):
    """Something is claimed that a reviewer cannot check."""
    return {"lane": "request_evidence", "missing": missing, "severity": severity}


def deep_review(
    area: AREA,
    reviewer: Literal["security", "data", "platform", "domain_owner"],
    read_the_diff: bool = True,
):
    """A human has to read the code, whatever the evidence says."""
    return {"lane": "deep_review", "area": area,
            "reviewer": reviewer, "read_the_diff": read_the_diff}


def hold(
    reason: Literal["contradictory_evidence", "insufficient_information",
                    "checks_unfinished", "scope_undefined"],
):
    """Not enough to decide either way. Preserve state, report the blocker."""
    return {"lane": "held", "reason": reason}


LANES = {f.__name__: f for f in
         (ready_for_manual_approval, request_evidence, deep_review, hold)}
