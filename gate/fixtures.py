# -*- coding: utf-8 -*-
"""Five synthetic pull requests, one per lane, plus the two deterministic ones."""
from .claims import PR

GOOD_DOCS = PR(
    number=101, title="docs(gate): document the evidence lanes",
    files=["docs/gate/lanes.md", "docs/gate/README.md"], additions=180, deletions=12,
    checks={"lint": "SUCCESS", "markdown-link-check": "SUCCESS"},
    body="""Adds the lane documentation that was missing.

- Link check passes over all 14 new links, see https://github.com/acme/repo/actions/runs/889231
- Rendered locally and reviewed, output below

```
$ npx markdown-link-check docs/gate/lanes.md
14 links checked.
0 dead links found.
```

No behaviour changes: only files under docs/ are touched.
""")

UNPROVEN = PR(
    number=102, title="fix(viewer): stop the camera snapping back on resize",
    files=["src/viewer/camera.ts", "src/viewer/resize.ts", "src/viewer/state.ts"],
    additions=96, deletions=41,
    checks={"build": "SUCCESS", "unit": "SUCCESS"},
    body="""Fixes the camera reset that happened on every window resize.

- The full regression suite passes, no regressions anywhere
- Verified manually on all supported browsers
- Performance is noticeably better after this change

Should be safe to merge.
""")

SECURITY = PR(
    number=103, title="feat(auth): rotate session tokens on privilege change",
    files=["src/auth/session.py", "src/auth/tokens.py", "src/auth/permissions.py",
           "tests/auth/test_session.py"],
    additions=240, deletions=58,
    checks={"build": "SUCCESS", "unit": "SUCCESS", "security-scan": "SUCCESS"},
    body="""Sessions now get a fresh token whenever a user's permissions change.

- New tests cover the rotation path, output below
- CI run https://github.com/acme/repo/actions/runs/889305 is green
- Commit 4f2a91c has the migration-free implementation

```
$ pytest tests/auth -q
28 passed in 3.41s
```
""")

PENDING = PR(
    number=104, title="refactor(api): collapse the three response builders into one",
    files=["src/api/responses.py", "src/api/handlers.py", "tests/api/test_responses.py"],
    additions=310, deletions=402,
    checks={"build": "SUCCESS", "unit": "PENDING", "integration": "QUEUED"},
    body="""Three builders that did the same thing are now one.

- Unit tests updated and passing locally
- Behaviour is identical, verified against the recorded fixtures
""")

FAILING = PR(
    number=105, title="feat(export): add IFC property set export",
    files=["src/export/ifc.py", "src/export/psets.py", "tests/export/test_ifc.py"],
    additions=420, deletions=15,
    checks={"build": "SUCCESS", "unit": "FAILURE", "lint": "SUCCESS"},
    body="""Exports property sets alongside geometry.

- Tested against three real IFC files, all round-trip correctly
- See run https://github.com/acme/repo/actions/runs/889402
""")

ALL = {"GOOD_DOCS": GOOD_DOCS, "UNPROVEN": UNPROVEN, "SECURITY": SECURITY,
       "PENDING": PENDING, "FAILING": FAILING}
