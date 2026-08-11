# Submit a pond to the lake

This directory is the lake's front desk. To have your self-hosted pond admitted to the
**canonical lake at [acsa.ai](https://acsa.ai)**, open a pull request that adds one file:

```
submissions/<your-pond-domain>.json
```

whose contents are your signed **`sava-registration/1`** document.

## Before you submit — gate your own pond

The lake admits by **proof, not trust**: it will pull your pond and re-verify every claim
against its own sources. You can run that exact gate yourself first, cold, with nothing
installed — and **if it passes for you, it passes for the lake.**

```bash
# fetch the three pinned tools, hash-check them, then gate your pond
curl -O https://acsa.ai/lake/sava_verify.py
curl -O https://acsa.ai/lake/sava_content_id.py
curl -O https://acsa.ai/lake/sava_gate.py
python3 -S sava_gate.py ./out --trust <your-pond-pubkey-hex> --now <ISO8601>
# -> "ADMISSIBLE — all Drops verify and reconstruct the signed pond head"  (exit 0)
```

If it is not `ADMISSIBLE`, fix it before submitting — a pond whose quotes don't match its
own sources is refused, not merely unlisted.

## Produce the registration

```bash
python3 sava_produce.py register \
  --pond ./pond-dir --key ./keys/pond.key \
  --head-url https://<your-host>/.well-known/sava/pond_head.json \
  --out ./out
```

`./out/registration.json` self-signs a proof that you hold the pond key and names the
public HTTPS URL where your `pond_head.json` lives. Copy it to
`submissions/<your-pond-domain>.json` and open the PR.

## What happens next

You already know the outcome — you ran the gate yourself. There is **no CI check** on this
PR, and that is deliberate: a runner asserting "admissible" would only be a trusted third
party re-deriving what you already proved. Instead:

1. The lake — the operator today, an automated signer later — pulls your pond from the
   `head_url` and re-runs the identical gate against freshly-fetched bytes.
2. On a pass it signs your pond in as a new leaf of the lake head and mirrors it.
3. **Your confirmation is a signature, not a badge:** your pond appears in the signed lake
   at [acsa.ai/lake](https://acsa.ai/lake) — pinned to `cf98ec47108b1296`, re-verifiable by
   anyone. That is the only "✓" in the trust path.

You never push to an API. The proof travels with the bytes; the lake only pulls; GitHub is
a dumb inbox, never a verifier.

> **Note:** the canonical, signed lake is served at **acsa.ai** (lake key fingerprint
> `cf98ec47108b1296`). This repository is its public submission inbox; its own historical
> `index.html`/data surface is being reconciled to mirror acsa.ai.
