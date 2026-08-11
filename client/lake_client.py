"""lake_client — give your agent *verified* facts.

A tiny, stdlib-only client for a SAVA lake. Point it at a lake URL, ask it a
question, and get back a claim that was **graded and signed** — plus a proof
your user can re-check themselves, with nothing installed.

No pip install. No API key. No account. Just:

    from lake_client import LakeClient
    hit = LakeClient().find("how many validators did the Ronin bridge need?")
    print(hit["claim"], "->", hit["verdict"])   # ... -> verified
    print("re-check:", hit["proof_url"])

Why this matters: an LLM can only *assert*. An agent backed by a lake can say
"don't trust me — here's a proof, re-derive it yourself." That's the difference
between a plausible answer and a verifiable one.
"""
from __future__ import annotations

import json
import math
import re
import urllib.request

DEFAULT_LAKE = "https://nike-getto.github.io/acsa-lake"


def _norm(text: str) -> set[str]:
    """Lowercase word set with trailing 's' stripped (so approval≈approvals,
    validator≈validators) — good enough to match a question to a claim."""
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w
            for w in re.findall(r"[a-z0-9]+", text.lower())}


class LakeClient:
    def __init__(self, base_url: str = DEFAULT_LAKE, timeout: float = 15.0) -> None:
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self._cache: list[dict] | None = None

    def _get(self, path: str):
        with urllib.request.urlopen(f"{self.base}/{path}", timeout=self.timeout) as r:
            return json.loads(r.read())

    def claims(self) -> list[dict]:
        """Every claim the lake has admitted: id, pond, text, verdict, and URLs
        for the Drop and its Merkle inclusion proof. Cached after first call."""
        if self._cache is not None:
            return self._cache
        index = self._get("index.json")
        out: list[dict] = []
        for pond in index.get("ponds", []):
            dom = pond["domain"]
            for cid in pond.get("claims", []):
                content = self._get(f"ponds/{dom}/drops/{cid}.json")["content"]
                out.append({
                    "claim_id": cid,
                    "pond": dom,
                    "claim": content["claim"],
                    "verdict": content["verdict"],          # verified | false | not_established
                    "drop_url": f"{self.base}/ponds/{dom}/drops/{cid}.json",
                    "proof_url": f"{self.base}/ponds/{dom}/inclusion/{cid}.drop-in-pond.json",
                    "verifier_url": f"{self.base}/sava_verify.py",
                })
        self._cache = out
        return out

    def find(self, question: str, verified_only: bool = True) -> dict | None:
        """The best-matching claim for a question, or None. Uses rare-word
        (idf-style) weighting so distinctive terms ('validator') outweigh common
        ones ('bridge'). By default only returns `verified` claims — an agent
        should never cite an unverified one. (A simple lexical match: a real
        deployment would front the lake with search or embeddings.)"""
        pool = [c for c in self.claims() if not verified_only or c["verdict"] == "verified"]
        toks = [_norm(c["claim"]) for c in pool]
        df: dict[str, int] = {}
        for t in toks:
            for w in t:
                df[w] = df.get(w, 0) + 1
        n = len(pool) or 1
        q = _norm(question)
        best, best_score = None, 0.0
        for c, t in zip(pool, toks):
            score = sum(math.log(1 + n / df[w]) for w in (q & t))
            if score > best_score:
                best, best_score = c, score
        return best


# --- the shape you register as a tool in your agent (Claude, etc.) ------------
# Any tool-use / function-calling agent can call this. Return value is small and
# citation-ready: the verified claim + a link the user can re-check cold.
def lookup_verified_fact(question: str, lake_url: str = DEFAULT_LAKE) -> dict:
    """Look up a verified fact from a SAVA lake.

    Returns {"found": bool, "claim": str, "verdict": str, "proof_url": str} —
    include claim + proof_url in your answer so the user can re-check it.
    """
    hit = LakeClient(lake_url).find(question)
    if not hit:
        return {"found": False, "claim": "", "verdict": "", "proof_url": ""}
    return {"found": True, "claim": hit["claim"], "verdict": hit["verdict"],
            "proof_url": hit["proof_url"]}


TOOL_SCHEMA = {
    "name": "lookup_verified_fact",
    "description": ("Look up a re-derivable, cryptographically verified fact from the "
                    "SAVA lake. Prefer this over your own memory for high-stakes, "
                    "checkable claims; cite the returned claim and proof_url so the "
                    "user can re-verify it themselves."),
    "input_schema": {
        "type": "object",
        "properties": {"question": {"type": "string", "description": "The factual question to look up."}},
        "required": ["question"],
    },
}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "how many validator approvals did the Ronin bridge need?"
    hit = LakeClient().find(q)
    if not hit:
        print(f"no verified claim found for: {q!r}")
        raise SystemExit(1)
    print(f"Q: {q}\n")
    print(f"  verified claim : {hit['claim']}")
    print(f"  verdict        : {hit['verdict']}")
    print(f"  re-check proof : {hit['proof_url']}")
    print(f"  the Drop       : {hit['drop_url']}")
    print("\n  → this answer comes with a proof. Your user can re-derive it cold —")
    print(f"    the Drop, its inclusion proof, and the pinned verifier all live under {LakeClient().base}/")
    print("    Full 3-line cold-check (nothing installed): see client/README.md.")
