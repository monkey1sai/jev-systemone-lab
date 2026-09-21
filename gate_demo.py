# -*- coding: utf-8 -*-
"""The PR evidence gate: same Dispatcher, different spec.

  Dispatcher(spec.json, LANES, client)     <- identical construction to demo_dispatch.py
  dispatcher(state, extra=claim_questions) <- claims found in THIS body ride along
  policy.decide(...)                       <- the lane is settled in code
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

from jev import Client, Dispatcher          # noqa: E402
from gate.lanes import LANES                # noqa: E402
from gate import claims as C, policy        # noqa: E402
from gate.fixtures import ALL               # noqa: E402

SPEC = json.loads((ROOT / "gate" / "spec.json").read_text(encoding="utf-8"))


def main():
    client = Client()
    d = Dispatcher(SPEC, LANES, client)
    print(f"  {len(d.questions)} fixed questions from {len(LANES)} lanes "
          f"+ per-PR claim questions\n")

    for name, pr in ALL.items():
        cl = C.extract_claims(pr.body)
        extra = C.extras(cl)
        call = d(C.state_for(pr, cl), extra=extra)
        dec = policy.decide(pr, cl, call)
        print(f"  #{pr.number}  {pr.title}")
        print(f"  {'-'*74}")
        print(f"  claims    {len(cl)} split out, {len(d.questions)+len(extra)} questions, "
              f"{call.ms}ms")
        print(policy.report(dec, call))
        print()

    print(f"  {client.calls} requests, {client.input_tokens:,} in / "
          f"{client.output_tokens:,} out tokens")


if __name__ == "__main__":
    main()
