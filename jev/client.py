"""TypeSafe System One HTTP client. stdlib only."""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error

API_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"


def api_key() -> str:
    """env var first; fall back to the Windows user environment in the
    registry so a not-yet-restarted shell still works."""
    k = os.environ.get("TYPESAFE_API_KEY")
    if k:
        return k
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            v = winreg.QueryValueEx(h, "TYPESAFE_API_KEY")[0]
            if v:
                return v
    except Exception:
        pass
    raise RuntimeError("TYPESAFE_API_KEY not set (env or user registry)")


class Client:
    def __init__(self, model: str = DEFAULT_MODEL, timeout: float = 30.0):
        self.model, self.timeout = model, timeout
        self._key = api_key()
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def system_one(self, state, questions: dict) -> dict:
        body = {"state": state, "model": self.model, "questions": questions}
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self._key}",
                     "Content-Type": "application/json"},
            method="POST")
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                out = json.load(r)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}") from None
        out["_ms"] = int((time.perf_counter() - t0) * 1000)
        u = out.get("usage") or {}
        self.calls += 1
        self.input_tokens += u.get("input_tokens", 0)
        self.output_tokens += u.get("output_tokens", 0)
        return out
