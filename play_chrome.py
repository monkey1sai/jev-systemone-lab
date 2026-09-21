# -*- coding: utf-8 -*-
"""Watch Jev play. Headed Chromium, one room at a time.

Code owns the loop. Every tick: snapshot the page, hand Jev the room and the
controls that actually exist, take back one ref, click it. The choice is
structurally confined to buttons on the page, so an illegal move is not
something the model can emit.
"""
from __future__ import annotations
import argparse, pathlib, statistics, sys, time

ROOT = pathlib.Path(__file__).parent
sys.path[:0] = [str(ROOT), str(ROOT / "sample")]

from playwright.sync_api import sync_playwright          # noqa: E402
from jev import Client                                    # noqa: E402
from jev.dispatcher import decide, NO_MATCH               # noqa: E402
from browser.snapshot import snapshot, click_ref, outcome # noqa: E402
import render, scenarios                                  # noqa: E402

OUT = ROOT / "out"
INSTRUCTIONS = ("Which single control on this screen best advances the stated goal? "
                "Judge the meaning of each control against the situation, not its position.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--rooms", type=int, default=8)
    ap.add_argument("--lang", choices=["en", "zh"], default="en")
    ap.add_argument("--scope", default="#game", help="'' to read the whole page")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--pause", type=float, default=1.1, help="seconds to watch each move")
    a = ap.parse_args()
    scope = a.scope or None

    OUT.mkdir(exist_ok=True)
    client = Client()
    hits, lat, rows = 0, [], []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=a.headless, args=["--window-size=1100,900"])
        page = browser.new_page(viewport={"width": 1100, "height": 900})

        for i in range(min(a.rooms, scenarios.count())):
            room = scenarios.get(i, a.lang)
            html = render.room_html(room["goal"], room["situation"], room["correct"],
                                    room["distractors"], junk=True, seed=i,
                                    title=f"Room {i+1}")
            f = OUT / f"room_{i:02d}.html"
            f.write_text(html, encoding="utf-8")
            page.goto(f.as_uri())

            snap = snapshot(page, scope)
            state = {"goal": room["goal"], "screen": snap["screen"]}
            ref, p, resp = decide(client, state, snap["actions"], INSTRUCTIONS)
            lat.append(resp["_ms"])

            if ref == NO_MATCH:
                print(f"  {i+1:>2}. NO-MATCH  p={p:.2f}  {resp['_ms']}ms")
                rows.append((i, False, p, resp["_ms"], "(no match)"))
                continue

            # make the decision visible before it is taken
            page.eval_on_selector(f'[data-jev-ref="{ref}"]',
                                  "el => {el.style.outline='3px solid #6ee7b7';"
                                  "el.style.background='#2f6f57'}")
            time.sleep(a.pause)
            click_ref(page, ref)
            time.sleep(0.35)

            o = outcome(page)
            ok = o["outcome"] == "correct"
            hits += ok
            rows.append((i, ok, p, resp["_ms"], o["picked"]))
            print(f"  {i+1:>2}. {'HIT ' if ok else 'MISS'}  p={p:.2f}  {resp['_ms']:>4}ms  "
                  f"{len(snap['actions']):>2} controls  -> {o['picked']}")
            if not ok:
                print(f"      expected: {room['correct']}")
            page.screenshot(path=str(OUT / f"room_{i:02d}.png"))

        time.sleep(1.0)
        browser.close()

    n = len(rows)
    print(f"\n  accuracy {hits}/{n} = {hits/n:.0%}" if n else "\n  no rooms")
    if lat:
        print(f"  latency  p50 {statistics.median(lat):.0f}ms   "
              f"max {max(lat)}ms   mean {statistics.mean(lat):.0f}ms")
        print(f"  tokens   in {client.input_tokens:,}  out {client.output_tokens:,}  "
              f"over {client.calls} requests")


if __name__ == "__main__":
    main()
