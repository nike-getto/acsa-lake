# acsa-lake

The public home of the **SAVA lake**: its submission inbox and, historically, a
cold-verifiable lake surface. A lake pulls admitted ponds over HTTPS, runs a
grounded-verify gate, and publishes a signed surface that anyone can re-derive offline.

> **Canonical lake: [acsa.ai](https://acsa.ai/lake)** (lake key fingerprint
> `cf98ec47108b1296`). That is the live, signed lake. The `index.html`/data surface in
> *this* repo is an earlier instance being reconciled to mirror acsa.ai; treat acsa.ai as
> the source of truth.

## Submit your pond

Open a PR adding `submissions/<your-pond-domain>.json` (your signed
`sava-registration/1`). Gate it yourself first with `sava_gate.py` — if it passes for
you, it passes for the lake. Full walkthrough: **[`submissions/README.md`](submissions/README.md)**.

- Front page (`index.html`): *Verified, not plausible* — a plain LLM vs. an agent
  backed by this lake, on one high-stakes Ronin-bridge fact.
- `lake_head.json` — the signed `sava-lake/1` head. `ponds/<domain>/` — each
  admitted pond (drops, sources, Merkle inclusion proofs).
- `sava_verify.py` (pinned) + `sava_content_id.py` — re-check any claim yourself,
  nothing installed:
  `python3 -S sava_verify.py drop ponds/teardown-ronin.acsa.ai/drops/tr-6.json --sources ponds/teardown-ronin.acsa.ai/sources --trust <pond-pubkey>`

The pond flows in from **github.com/nike-getto/acsa-pond-teardown** via `acsa lake sync`.
The lake is an authority, not a host — re-derive it offline.
