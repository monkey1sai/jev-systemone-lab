# -*- coding: utf-8 -*-
"""Stress Jev on a real browser, against ground truth.

Four runs over the same rooms:
  A  scoped extraction, English questions      <- the recommended shape
  B  whole-page extraction, English questions  <- no filtering at all
  C  Chinese state and Chinese questions       <- CJK is documented as weaker
  D  scoped, twenty questions in one request   <- does fan-out really cost nothing

--set easy   twenty obvious common-sense rooms (saturates; use it as a smoke test)
--set hard   twelve rooms whose distractors are near misses (has headroom)
"""
from __future__ import annotations
import argparse, pathlib, statistics, sys

ROOT = pathlib.Path(__file__).parent
sys.path[:0] = [str(ROOT), str(ROOT / "sample")]

from playwright.sync_api import sync_playwright           # noqa: E402
from jev import Client                                     # noqa: E402
from jev.dispatcher import decide, NO_MATCH                # noqa: E402
from browser.snapshot import snapshot, click_ref, outcome  # noqa: E402
import render, scenarios, hard                             # noqa: E402

OUT = ROOT / "out"; OUT.mkdir(exist_ok=True)

EN = ("Which single control on this screen best advances the stated goal? "
      "Judge the meaning of each control against the situation, not its position.")
ZH = ("畫面上哪一個控制項最能推進所述目標？"
      "請依據每個控制項的語意與情境判斷，不要看位置。")

FILLERS = [
    "Is the situation on this screen time critical?",
    "Does the screen describe a physical hazard?",
    "Is a person's life at risk in this situation?",
    "Does the screen involve money or payment?",
    "Is this about computer systems rather than the physical world?",
    "Would a trained professional be needed to resolve this?",
    "Does the screen show an attempt to deceive the reader?",
    "Is the reader being asked to reveal a secret?",
    "Does this situation involve a vehicle?",
    "Does this situation involve fire or smoke?",
    "Is there a child or infant involved?",
    "Does the screen mention a medical condition?",
    "Is the correct response to stop and do nothing for now?",
    "Would delaying the decision make the outcome worse?",
    "Does the situation involve a stranger?",
    "Is regulatory or policy compliance at stake?",
    "Does the screen reference a deadline?",
    "Is the situation happening indoors?",
    "Would calling for outside help be reasonable here?",
]


def run(label, client, page, data, lang, scope, instructions, extra_n=0):
    rooms = data.count()
    hits, lat, ctrls, no_match, misses = 0, [], [], 0, []
    t_in0, t_out0, c0 = client.input_tokens, client.output_tokens, client.calls
    for i in range(rooms):
        room = data.get(i, lang)
        html = render.room_html(room["goal"], room["situation"], room["correct"],
                                room["distractors"], junk=True, seed=i)
        f = OUT / f"_s{i:02d}.html"; f.write_text(html, encoding="utf-8")
        page.goto(f.as_uri())
        snap = snapshot(page, scope)
        ctrls.append(len(snap["actions"]))
        state = {"goal": room["goal"], "screen": snap["screen"]}
        extra = {f"q{k}": {"type": "noul", "instructions": FILLERS[k]} for k in range(extra_n)}
        ref, p, resp = decide(client, state, snap["actions"], instructions, extra=extra)
        lat.append(resp["_ms"])
        if ref == NO_MATCH:
            no_match += 1
            misses.append((i, "(no match)", p))
            continue
        try:
            click_ref(page, ref, timeout=3000)
        except Exception:
            misses.append((i, "(click failed)", p))
            continue
        o = outcome(page)
        if o["outcome"] == "correct":
            hits += 1
        else:
            misses.append((i, o["picked"] or "(nothing)", p))
    n = client.calls - c0
    return {"label": label, "rooms": rooms, "hits": hits, "acc": hits / rooms,
            "p50": statistics.median(lat), "p95": sorted(lat)[max(0, int(len(lat) * .95) - 1)],
            "controls": statistics.mean(ctrls), "no_match": no_match, "misses": misses,
            "tok_in": (client.input_tokens - t_in0) / n,
            "tok_out": (client.output_tokens - t_out0) / n}


def show(rows, data):
    print(f"\n  {'run':<34}{'acc':>11}{'ctrls':>8}{'p50':>8}{'p95':>8}{'tok_in':>8}")
    print("  " + "-" * 77)
    for r in rows:
        print(f"  {r['label']:<34}{r['hits']}/{r['rooms']} {r['acc']:>5.0%}"
              f"{r['controls']:>8.0f}{r['p50']:>6.0f}ms{r['p95']:>6.0f}ms{r['tok_in']:>8.0f}")
    for r in rows:
        if r["misses"]:
            print(f"\n  {r['label']} missed:")
            for i, picked, p in r["misses"]:
                print(f"    room {i+1:>2}  picked {picked!r} p={p:.2f}")
                print(f"              wanted {data.get(i,'en')['correct']!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["easy", "hard"], default="hard")
    a = ap.parse_args()
    data = scenarios if a.set == "easy" else hard

    client = Client()
    rows = []
    print(f"  dataset: {a.set}  ({data.count()} rooms)")
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        page = b.new_page(viewport={"width": 1100, "height": 900})
        rows.append(run("A  scoped + English", client, page, data, "en", "#game", EN))
        rows.append(run("B  whole page + English", client, page, data, "en", None, EN))
        rows.append(run("C  Chinese state + Chinese Q", client, page, data, "zh", "#game", ZH))
        rows.append(run("D  scoped + 20 questions", client, page, data, "en", "#game", EN, 19))
        b.close()
    show(rows, data)
    A, B, C, D = rows
    print(f"\n  fan-out    1 q {A['p50']:.0f}ms -> 20 q {D['p50']:.0f}ms "
          f"({D['p50']/A['p50']:.2f}x latency, {D['tok_out']/A['tok_out']:.1f}x output tokens)")
    print(f"  filtering  scoped {A['tok_in']:.0f} in-tok / {A['controls']:.0f} controls  ->  "
          f"whole page {B['tok_in']:.0f} / {B['controls']:.0f}  ({B['tok_in']/A['tok_in']:.1f}x cost)")
    print(f"  language   English {A['acc']:.0%}  ->  Chinese {C['acc']:.0%}")
    print(f"  total      {client.calls} requests, {client.input_tokens:,} in / "
          f"{client.output_tokens:,} out tokens")


if __name__ == "__main__":
    main()
