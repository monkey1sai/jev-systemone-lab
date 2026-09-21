# -*- coding: utf-8 -*-
"""Adapt `gh pr view --json ...` output into the gate's PR record.

Nothing here contacts the gate or the model. It only reshapes what the GitHub
CLI already returned, so a dry run can show exactly which bytes would leave.
"""
from __future__ import annotations
import json, pathlib
from .claims import PR


def from_gh_json(path: str | pathlib.Path) -> PR:
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    checks = {}
    for c in (d.get("statusCheckRollup") or []):
        name = c.get("name") or c.get("context") or c.get("workflowName") or "check"
        checks[name] = (c.get("conclusion") or c.get("state") or "PENDING") or "PENDING"
    return PR(number=d["number"], title=d["title"], body=d.get("body") or "",
              files=[f["path"] for f in (d.get("files") or [])],
              additions=d.get("additions", 0), deletions=d.get("deletions", 0),
              checks=checks)
