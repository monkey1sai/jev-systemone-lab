# -*- coding: utf-8 -*-
"""Run the gate on a real pull request. Dry run by default.

Dry run builds the exact request body and writes it to disk without sending
it, so the bytes that would leave this machine can be read first.
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

from jev import Client, Dispatcher                     # noqa: E402
from jev.client import API_URL, DEFAULT_MODEL          # noqa: E402
from gate.lanes import LANES                           # noqa: E402
from gate import claims as C, policy                   # noqa: E402
from gate.github_pr import from_gh_json                # noqa: E402

SPEC = json.loads((ROOT / "gate" / "spec.json").read_text(encoding="utf-8"))


def payload_for(pr):
    cl = C.extract_claims(pr.body)
    d = Dispatcher.__new__(Dispatcher)
    d.spec, d.tools, d.stated_threshold = SPEC, LANES, 0.5
    d.questions = d._build()
    body = {"state": C.state_for(pr, cl), "model": DEFAULT_MODEL,
            "questions": {**d.questions, **C.extras(cl)}}
    return cl, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_files", nargs="+")
    ap.add_argument("--send", action="store_true",
                    help="actually call the API; omitted means dry run")
    a = ap.parse_args()

    for jf in a.json_files:
        pr = from_gh_json(jf)
        cl, body = payload_for(pr)
        blob = json.dumps(body, ensure_ascii=False)
        out = ROOT / "out" / "realpr" / f"payload_{pr.number}.json"
        out.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n  PR #{pr.number}  {pr.title[:56]}")
        print(f"  {'-'*74}")
        print(f"  would POST to      {API_URL}")
        print(f"  payload            {len(blob.encode('utf-8')):,} bytes"
              f"   ({len(body['questions'])} questions)")
        print(f"  state contains     title, body ({len(pr.body)} chars), "
              f"{len(pr.files)} paths, {len(pr.checks)} check results")
        print(f"  claims split out   {len(cl)}")
        for c in cl:
            print(f"      - {c[:84]}")
        print(f"  diff content       NOT included")
        print(f"  written for review {out}")

        if a.send:
            d = Dispatcher(SPEC, LANES, Client())
            call = d(C.state_for(pr, cl), extra=C.extras(cl))
            dec = policy.decide(pr, cl, call)
            print(f"\n{policy.report(dec, call)}")


if __name__ == "__main__":
    main()
