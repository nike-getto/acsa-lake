<!-- A pond submission adds exactly one file: submissions/<your-pond-domain>.json
     (your signed sava-registration/1). See submissions/README.md. -->

## Pond submission

- **Pond domain:**
- **Public head URL** (HTTPS `pond_head.json`):
- **Pond key fingerprint** (`sha256(pubkey)[:16]`):

### Confirm

- [ ] The file I added is `submissions/<my-pond-domain>.json` and is my signed `sava-registration/1`.
- [ ] I ran `sava_gate.py` on my pond and it printed **ADMISSIBLE** (exit 0).
- [ ] My pond is hosted over plain **HTTPS** (no self-signed cert; plain HTTP is refused).
- [ ] I hold the pond key behind the fingerprint above; it is not published anywhere.

<!-- The lake will pull your pond from the head URL and re-run the same gate. If it
     passes, your pond is admitted to acsa.ai/lake. Nothing is trusted on your word —
     everything is re-verified from the bytes. -->
