# acsa-lake

A live **SAVA lake**. It pulls admitted ponds over HTTPS, runs a grounded-verify
gate, and publishes a signed, cold-verifiable lake surface — served here.

- Front page (`index.html`): *Verified, not plausible* — a plain LLM vs. an agent
  backed by this lake, on one high-stakes Ronin-bridge fact.
- `lake_head.json` — the signed `sava-lake/1` head. `ponds/<domain>/` — each
  admitted pond (drops, sources, Merkle inclusion proofs).
- `sava_verify.py` (pinned) + `sava_content_id.py` — re-check any claim yourself,
  nothing installed:
  `python3 -S sava_verify.py drop ponds/teardown-ronin.acsa.ai/drops/tr-6.json --sources ponds/teardown-ronin.acsa.ai/sources --trust <pond-pubkey>`

The pond flows in from **github.com/nike-getto/acsa-pond-teardown** via `acsa lake sync`.
The lake is an authority, not a host — re-derive it offline.
