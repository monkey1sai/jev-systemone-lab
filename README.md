# jev_demo

A Dispatcher skeleton for TypeSafe System One (Jev), plus a browser harness that
measures it against ground truth.

The core (`jev/`) has **no dependencies** - stdlib and `urllib` only. Only the
browser layer needs `playwright`.

## Layout

```
jev/closed_sets.py   type hints -> question shapes (Literal=choice, list[Literal]=set, bool=flag)
jev/dispatcher.py    spec + functions -> one batched request -> a typed Call
jev/client.py        HTTP client; reads TYPESAFE_API_KEY from env or the user registry
browser/snapshot.py  live page -> (state, action space) with clickable refs
sample/scenarios.py  20 obvious rooms   (saturates at 100%; smoke test only)
sample/hard.py       12 near-miss rooms (has headroom; use this one)
sample/render.py     renders a room inside real page furniture: nav, ads, cookie bar, footer
play_chrome.py       watch it play in a headed browser
stress.py            four-way comparison against ground truth
calib.py             is the confidence worth gating on
```

## Run

```bash
python play_chrome.py -n 10            # headed, watchable
python stress.py --set hard            # the four-way comparison
python calib.py                        # confidence vs truth
```

## What the design commits to

**The action space is built per tick from the page, not from a fixed tool list.**
`snapshot()` tags every visible, enabled control with a ref and returns
`{ref: 'role "name"'}`. Those refs become the Choice criteria, so the model
cannot emit a control that is not on the screen. An illegal move is not a thing
it can express.

**Free-form arguments never get a question.** `closed_sets()` skips `int`, `str`
and dates, exactly as the official function-calling cookbook does, and the
function's own default stands. Jev selects; it does not generate.

**A no-match outcome is always added.** Without it the model is forced to pick
something from a list where nothing fits.

**Confidence is the least certain judgement, not the product.** One wrong
argument spoils a call, and a product decays with argument count whether or not
any single judgement is shaky. `Call.weakest()` names the culprit.

## Measured on this machine (jev-1.13.0, 12 hard rooms)

| run | accuracy | controls | p50 | in-tokens |
|---|---|---|---|---|
| A scoped + English | 11/12 92% | 4 | 641ms | 466 |
| B whole page + English | 11/12 92% | 46 | 627ms | 1318 |
| C Chinese state + Chinese questions | 11/12 92% | 4 | 632ms | 511 |
| D scoped + 20 questions in one request | 11/12 92% | 4 | 624ms | 766 |

- **Fan-out is genuinely close to free.** Twenty questions cost 0.97x the
  latency of one. Batch speculative questions; do not serialise branches.
- **Not filtering costs 2.8x input tokens** for the same answer. On this
  workload it did not cost accuracy - but the choice was 4-way either way once
  the model had the game text, and the documented degradation from irrelevant
  state needs a harder or noisier task to show up. Treat the token number as
  established and the accuracy number as untested, not as a clearance.
- **Chinese matched English at 92% here.** The docs state CJK accuracy is lower;
  twelve rooms cannot refute that. It only means the gap did not appear at this
  difficulty.
- **Confidence carried real signal.** The one error scored 0.63 while ten of the
  eleven correct answers scored 0.96 or above. A `p < 0.70` gate caught the
  error and held back one good answer out of eleven.

All four runs failed the same room - the one where rolling a deploy back is the
instinctive answer but does not release the lock the index build is holding.

---

# The PR evidence gate

Same engine, different spec. `gate_demo.py` builds a `Dispatcher` exactly the
way `demo_dispatch.py` does - a spec, a set of typed functions, a client - and
the only thing that changed is which functions and which spec.

```
gate/lanes.py     four lanes as ordinary typed functions; Literal args become questions
gate/spec.json    what each lane and each argument means, in plain words
gate/claims.py    what code does first: split the body into claims, count artifacts
gate/policy.py    the lane is settled here, in code, by explicit conditions
gate/fixtures.py  five synthetic pull requests, one per outcome
```

Note what `gate/lanes.py` does not contain: any `str` argument. There is no
`reason: str` for the model to write. Every fillable slot is a closed set a
reviewer could have enumerated beforehand, so nothing is generated.

## The model does not choose the lane

The route question is asked - it rides along free - but it is advisory. The
governing rule is that failed, skipped or missing evidence never counts as a
pass, and that is a hard condition, not a weight something else can compensate
for. `policy.decide` applies conditions in order, and reports for each decision
which parts were VERIFIED by code and which were INFERRED by the model.

Two of the five fixtures are decided against the model's own answer:

| PR | lane | decided by | model said |
|---|---|---|---|
| 101 docs, evidence complete | hold | `overclaim` only 0.68 certain, gate is 0.70 | ready |
| 102 claims a green suite, shows nothing | request_evidence | a claim has no checkable artifact | agrees |
| 103 touches auth and secrets | deep_review | security 0.99 | agrees |
| 104 checks still queued | hold | **VERIFIED**: checks have not reported | request_evidence |
| 105 a check is failing | request_evidence | **VERIFIED**: unit is FAILURE | agrees |

## Why the policy is not one question

On PR 101 every atomic judgement came back decisive - artifact 0.94, scope
0.80, overclaim 0.32, security 0.02, blast radius 0.03, verification 1.93 -
while the single "which lane" question sat at 0.51 ready against 0.39
request_evidence. Synthesising a policy in one shot is the indirection the
model is documented to be worst at; the atomic signals are what it is good at.

So the approval gate reads the judgements the rules actually consulted, not the
lane answer and not the weakest argument overall. A shaky answer to a cosmetic
flag like `needs_release_note` is not a reason to withhold approval - the
uncertainty that matters is the uncertainty the decision rests on.
