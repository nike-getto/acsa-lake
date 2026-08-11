#!/usr/bin/env python3
"""Operator/automation admit-fetcher: fetch a submitted pond and gate it.

This runs on the LAKE side at admission time — the operator today, the
KMS-backed signer later — NOT in a GitHub Action. Verification is
deterministic and the submitter already ran the identical gate
(`sava_gate.py`) before submitting; putting a CI runner in the trust path
would only re-assert a result anyone can re-derive, so we don't. GitHub is a
dumb inbox for the submission message; the gate lives here, in a controlled
environment, and the only confirmation that matters is the pond appearing in
the signed lake head.

Given a `submissions/<domain>.json` (a signed `sava-registration/1`), this:

  1. structurally checks the registration — format, HTTPS head URL, and that
     `sha256(public_key_hex)[:16]` equals both the content and seal
     `key_fingerprint`;
  2. fetches the pond (head + manifest + every Drop the manifest lists) from
     the registration's `head_url`, over HTTPS only;
  3. enforces the domain guard — the pond head's self-declared `domain` must
     equal the registration's `domain`;
  4. runs the pinned cold gate (`sava_gate.py`) over the fetched pond.

Admission is by pond-proof, not submitter identity: the gate is the
load-bearing check (the pond head + every Drop verify, and the Drops
reconstruct the signed Merkle root). Exit 0 = admissible, 1 = refused.

Runs with system python3 + the three pinned tools in --tools. No engine.
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse


def _fail(reason: str) -> dict:
    return {"admissible": False, "reason": reason}


def _fetch(url: str, dest: Path) -> None:
    if urlparse(url).scheme != "https":
        raise ValueError(f"non-HTTPS URL refused: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "acsa-lake-gate"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (scheme checked above)
        dest.write_bytes(r.read())


def gate_submission(registration_path: Path, tools: Path, now: str) -> dict:
    try:
        reg = json.loads(registration_path.read_text())
        c = reg["content"]
    except Exception as e:
        return _fail(f"registration is not valid JSON with a content object: {e}")

    if c.get("format") != "sava-registration/1":
        return _fail(f"format is {c.get('format')!r}, expected sava-registration/1")
    domain, pub, head_url = c.get("domain"), c.get("public_key_hex"), c.get("head_url")
    if not (domain and pub and head_url):
        return _fail("registration missing domain, public_key_hex, or head_url")

    try:
        derived_fp = hashlib.sha256(bytes.fromhex(pub)).hexdigest()[:16]
    except ValueError:
        return _fail("public_key_hex is not valid hex")
    if derived_fp != c.get("key_fingerprint") or derived_fp != reg.get("seal", {}).get("key_fingerprint"):
        return _fail("key_fingerprint does not match sha256(public_key_hex)[:16] in content and/or seal")

    tmp = Path(tempfile.mkdtemp())
    (tmp / "drops").mkdir()
    try:
        _fetch(head_url, tmp / "pond_head.json")
        base = head_url.rsplit("/", 1)[0] + "/"
        _fetch(urljoin(base, "manifest.json"), tmp / "manifest.json")
    except Exception as e:
        return _fail(f"could not fetch pond head/manifest from {head_url!r}: {e}")

    head = json.loads((tmp / "pond_head.json").read_text())
    if head.get("content", {}).get("domain") != domain:
        return _fail(
            f"domain guard: pond head domain {head.get('content', {}).get('domain')!r} "
            f"!= registration domain {domain!r}"
        )

    manifest = json.loads((tmp / "manifest.json").read_text())
    try:
        for m in manifest["members"]:
            name = Path(m["drop_path"]).name
            _fetch(urljoin(base, m["drop_path"]), tmp / "drops" / name)
    except Exception as e:
        return _fail(f"could not fetch a member Drop: {e}")

    report_path = tmp / "gate_report.json"
    subprocess.run(
        [
            sys.executable, "-S", str(tools / "sava_gate.py"), str(tmp),
            "--trust", pub, "--now", now,
            "--verifier", str(tools / "sava_verify.py"),
            "--contentid", str(tools / "sava_content_id.py"),
            "--out", str(report_path),
        ],
        check=False,
    )
    try:
        return json.loads(report_path.read_text())
    except Exception as e:
        return _fail(f"gate did not produce a report: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gate a submitted pond, CI-side")
    ap.add_argument("registration", help="path to submissions/<domain>.json")
    ap.add_argument("--tools", default=".", help="dir holding the three pinned tools")
    ap.add_argument("--now", default=None, help="ISO8601 (default: current UTC)")
    args = ap.parse_args(argv)

    now = args.now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = gate_submission(Path(args.registration), Path(args.tools), now)

    verdict = "ADMISSIBLE" if report.get("admissible") else "REFUSED"
    print(f"{verdict} — {report.get('reason')}")
    for claim in report.get("claims", []):
        print(f"  {claim.get('drop')}: result={claim.get('result')} verdict={claim.get('verdict')}")
    return 0 if report.get("admissible") else 1


if __name__ == "__main__":
    sys.exit(main())
