"""Read a function signature and find the arguments Jev can fill.

Only closed sets get a question. int / str / dates never do - the
function's own default stands. That is the whole point: Jev selects,
it does not generate.
"""
from __future__ import annotations
import inspect, types
from typing import Literal, Union, get_args, get_origin, get_type_hints

CHOICE, SET, FLAG = "choice", "set", "flag"


def _unwrap_optional(t):
    """`X | None` -> `X`"""
    if get_origin(t) in (Union, types.UnionType):
        rest = [a for a in get_args(t) if a is not type(None)]
        if len(rest) == 1:
            return rest[0]
    return t


def _classify(t):
    """-> (shape, options) or None when the argument is not a closed set."""
    t = _unwrap_optional(t)
    if t is bool:
        return FLAG, None
    if get_origin(t) is Literal:
        return CHOICE, [str(v) for v in get_args(t)]
    if get_origin(t) in (list, set, frozenset, tuple):
        args = get_args(t)
        if args:
            inner = _unwrap_optional(args[0])
            if get_origin(inner) is Literal:
                return SET, [str(v) for v in get_args(inner)]
    return None


def closed_sets(fn) -> dict[str, tuple[str, list | None]]:
    """{arg_name: (shape, options)} for every fillable argument."""
    try:
        hints = get_type_hints(fn)
    except Exception:
        hints = getattr(fn, "__annotations__", {})
    out = {}
    for name in inspect.signature(fn).parameters:
        if name in ("self", "cls"):
            continue
        shaped = _classify(hints[name]) if name in hints else None
        if shaped:
            out[name] = shaped
    return out
