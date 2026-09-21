# -*- coding: utf-8 -*-
"""Is the confidence worth acting on? Print it per room against the truth.

A typed answer guarantees the interface, not the truth. The question that
matters operationally is whether the number tells you when not to act.
"""
from __future__ import annotations
import pathlib, sys

ROOT = pathlib.Path(__file__).parent
sys.path[:0] = [str(ROOT), str(ROOT / "sample")]

from playwright.sync_api import sync_playwright           # noqa: E402
from jev import Client                                     # noqa: E402
from jev.dispatcher import decide, NO_MATCH                # noqa: E402
from browser.snapshot import snapshot, click_ref, outcome  # noqa: E402
import render, hard                                        # noqa: E402

OUT = ROOT / "out"; OUT.mkdir(exist_ok=True)
EN = ("Which single control on this screen best advances the stated goal? "
      "Judge the meaning of each control against the situation, not its position.")

rows = []
client = Client()
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 1100, "height": 900})
    for i in range(hard.count()):
        r = hard.get(i, "en")
        f = OUT / f"_c{i:02d}.html"
        f.write_text(render.room_html(r["goal"], r["situation"], r["correct"],
                                      r["distractors"], junk=True, seed=i), encoding="utf-8")
        page.goto(f.as_uri())
        snap = snapshot(page, "#game")
        ref, p, resp = decide(client, {"goal": r["goal"], "screen": snap["screen"]},
                              snap["actions"], EN)
        ok = False
        if ref != NO_MATCH:
            click_ref(page, ref, timeout=3000)
            ok = outcome(page)["outcome"] == "correct"
        rows.append((i, ok, p, r["goal"]))
    b.close()

print(f"\n  {'room':<6}{'verdict':<9}{'p':>6}   goal")
print("  " + "-" * 64)
for i, ok, p, goal in sorted(rows, key=lambda r: r[2]):
    print(f"  {i+1:<6}{'HIT' if ok else 'MISS':<9}{p:>6.2f}   {goal}")

hits = [p for _, ok, p, _ in rows if ok]
miss = [p for _, ok, p, _ in rows if not ok]
print(f"\n  hits  n={len(hits)}  min p {min(hits):.2f}  mean {sum(hits)/len(hits):.2f}")
if miss:
    print(f"  miss  n={len(miss)}  max p {max(miss):.2f}")
    for t in (0.70, 0.80, 0.90):
        held = [p for p in hits if p < t]
        caught = [p for p in miss if p < t]
        print(f"  gate p<{t:.2f}: catches {len(caught)}/{len(miss)} errors, "
              f"holds back {len(held)}/{len(hits)} good answers")
