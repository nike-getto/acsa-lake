# Give your agent *verified* facts

Your agent can only *assert*. An agent backed by a **SAVA lake** can say:
**"don't trust me — here's a proof, re-check the math yourself."**

`lake_client.py` is the ~15 lines that get you there. **Stdlib only — no pip
install, no API key, no account.**

---

## Quickstart

```python
from lake_client import LakeClient

hit = LakeClient().find("how many validators did the Ronin bridge need?")
print(hit["claim"])      # The bridge required approval from a majority of five of the nine validator nodes...
print(hit["verdict"])    # verified
print(hit["proof_url"])  # a Merkle proof your user can re-derive, cold
```

Or from the shell:

```
python3 lake_client.py "Ronin bridge validator approvals"
```

Point it at any lake: `LakeClient("https://your-lake.example/…")`.

## Drop it into your agent as a tool

`lake_client.py` ships a ready-made tool function + schema. Register it with any
tool-use / function-calling agent (Claude, etc.):

```python
from lake_client import lookup_verified_fact, TOOL_SCHEMA
# TOOL_SCHEMA -> give it to your agent as a tool definition
# when the model calls the tool with {"question": "..."}, run:
result = lookup_verified_fact(question)
# -> {"found": True, "claim": "...", "verdict": "verified", "proof_url": "https://…"}
```

Then have your agent **cite `claim` and hand the user `proof_url`.** For
high-stakes, checkable questions it now answers with a fact *and a receipt* —
instead of a plausible guess.

> Rule of thumb: only cite claims where `verdict == "verified"` (the default the
> client returns). The lake also holds `false` and `not_established` verdicts —
> those are answers too, just not ones to assert as true.

## The receipt: your user re-checks it, nothing installed

The whole point is that the proof isn't *ours* to be trusted — anyone can
re-derive it. From the lake, with only system `python3`:

```
base=https://nike-getto.github.io/acsa-lake
pond=teardown-ronin.acsa.ai
curl -sO $base/sava_verify.py
# fetch the Drop, its inclusion proof, and the cited source, then:
python3 -S sava_verify.py drop  drops/tr-6.json --sources sources --trust <pond-pubkey>
python3 -S sava_verify.py inclusion  tr-6.drop-in-pond.json --root <pond-root>
#   -> sava-verify: CONFIRMED (result=0)
```

(`<pond-pubkey>` for this lake is
`a421e6e68e9e7f1c9a383465e747e0ad59bc34840473d90c3f326dd322f37117`; the pond's
key fingerprint is committed by the signed lake head, so it's anchored, not
taken on faith. See the [demo](https://nike-getto.github.io/acsa-lake/) for the
full chain lake → pond → drop.)

## Where the facts come from

A **lake** is a body of claims that were each **graded and signed**, then pulled
into the lake through a **grounded-verify gate** — a claim only gets in if it
actually holds against its cited source. The lake is an *authority, not a host*:
it re-derives, it never trusts a push. You're drawing from that, not asserting
on your own.

Want to contribute your own verified claims? A lake admits **ponds** — self-hosted,
signed claim sets anyone can stand up. (Ask the lake operator to admit yours.)
