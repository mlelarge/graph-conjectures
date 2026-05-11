"""Build a reproducibility manifest for a snark catalogue + cert directory.

The manifest records the exact generator commands, tool versions, per-order
counts, SHA-256 of every catalogue and intermediate file, and a content
hash of the certificate directory. Without this, a sweep result is
replayable from a stored cert but the *enumeration claim* (e.g. "all
nontrivial snarks through n=22") is not independently verifiable.

Usage::

    python scripts/manifest.py \\
        --catalogue data/catalogues/nontrivial_snarks_n10_to_22.g6 \\
        --orders 10 18 20 22 \\
        --geng "geng -d3 -D3 -c -tf -q {n}" \\
        --filter-cmd "scripts/catalogue.py {cubic_g5} --filter nontrivial-snark --emit-jsonl" \\
        --intermediate-dir data/catalogues \\
        --cert-dir data/interval_certs/nontrivial_n10_to_22 \\
        --out data/catalogues/nontrivial_snarks_n10_to_22.manifest.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import platform
import subprocess
from typing import Any


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: pathlib.Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _content_hash_dir(root: pathlib.Path, *, glob: str = "*.json") -> dict[str, Any]:
    """Hash a directory by hashing each file's contents in sorted name order,
    then SHA-256 the concatenation of ``name + ":" + sha256`` lines."""
    h = hashlib.sha256()
    files = []
    for p in sorted(root.glob(glob)):
        if not p.is_file():
            continue
        s = _sha256_file(p)
        h.update(f"{p.name}:{s}\n".encode("ascii"))
        files.append({"name": p.name, "sha256": s, "size": p.stat().st_size})
    return {
        "root": str(root),
        "glob": glob,
        "n_files": len(files),
        "directory_sha256": h.hexdigest(),
        "files": files,
    }


def _tool_version(name: str, args: list[str]) -> str:
    try:
        out = subprocess.run(
            args, capture_output=True, text=True, timeout=10, check=False
        )
        first_line = (out.stdout or out.stderr or "").splitlines()[0:2]
        return " ".join(first_line).strip() or "<no output>"
    except FileNotFoundError:
        return f"<{name} not found>"
    except Exception as exc:  # pragma: no cover - defensive
        return f"<error invoking {name}: {exc}>"


def _nauty_version() -> str:
    """Try to detect the installed nauty version via Homebrew, then fall
    back to the geng usage banner. Both are best-effort -- the manifest
    consumer should treat this as informational, not a verifier input."""
    try:
        out = subprocess.run(
            ["brew", "list", "--versions", "nauty"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        line = (out.stdout or "").strip()
        if line.startswith("nauty "):
            return line
    except (FileNotFoundError, Exception):
        pass
    return _tool_version("geng", ["geng", "-h"])


def build_manifest(
    *,
    catalogue: pathlib.Path,
    orders: list[int],
    geng_pattern: str,
    filter_cmd_pattern: str,
    intermediate_dir: pathlib.Path,
    cert_dir: pathlib.Path | None,
    name: str,
) -> dict[str, Any]:
    counts = []
    catalogues_per_order = []
    for n in orders:
        cubic_g5 = intermediate_dir / f"cubic_g5_n{n}.g6"
        nontrivial_g6 = intermediate_dir / f"nontrivial_snarks_n{n}.g6"
        nontrivial_jsonl = intermediate_dir / f"nontrivial_snarks_n{n}.jsonl"
        block: dict[str, Any] = {
            "order": n,
            "geng_command": geng_pattern.format(n=n),
            "filter_command": filter_cmd_pattern.format(cubic_g5=str(cubic_g5)),
        }
        if cubic_g5.exists():
            block["cubic_g5_file"] = {
                "path": str(cubic_g5),
                "n_lines": sum(1 for _ in cubic_g5.open()),
                "sha256": _sha256_file(cubic_g5),
                "bytes": cubic_g5.stat().st_size,
            }
        if nontrivial_g6.exists():
            block["nontrivial_snark_file"] = {
                "path": str(nontrivial_g6),
                "n_lines": sum(1 for _ in nontrivial_g6.open()),
                "sha256": _sha256_file(nontrivial_g6),
                "bytes": nontrivial_g6.stat().st_size,
            }
            counts.append({"order": n, "nontrivial_snarks": block["nontrivial_snark_file"]["n_lines"]})
        if nontrivial_jsonl.exists():
            block["nontrivial_snark_jsonl"] = {
                "path": str(nontrivial_jsonl),
                "sha256": _sha256_file(nontrivial_jsonl),
                "bytes": nontrivial_jsonl.stat().st_size,
            }
        catalogues_per_order.append(block)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "name": name,
        "summary": {
            "orders": orders,
            "counts_by_order": counts,
            "total_nontrivial_snarks": sum(c["nontrivial_snarks"] for c in counts),
        },
        "combined_catalogue": {
            "path": str(catalogue),
            "n_lines": sum(1 for _ in catalogue.open()) if catalogue.exists() else None,
            "sha256": _sha256_file(catalogue) if catalogue.exists() else None,
            "bytes": catalogue.stat().st_size if catalogue.exists() else None,
        },
        "per_order": catalogues_per_order,
        "tools": {
            "nauty": _nauty_version(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "definitions": {
            "nontrivial_snark": (
                "simple, cubic, bridgeless, girth >= 5, "
                "cyclically 4-edge-connected, chromatic index 4"
            ),
            "cubic_g5_source": (
                "all simple connected cubic graphs of girth >= 5 from nauty geng "
                "(-d3 -D3 -c -tf), one per line in graph6 format"
            ),
            "filter_pipeline": (
                "scripts/catalogue.py classifies each graph and keeps those "
                "matching --filter nontrivial-snark"
            ),
        },
        "timestamp_utc": _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }

    if cert_dir is not None and cert_dir.exists():
        manifest["interval_certificates"] = _content_hash_dir(cert_dir, glob="*.json")

    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", type=pathlib.Path, required=True)
    ap.add_argument("--orders", type=int, nargs="+", required=True)
    ap.add_argument("--geng", default="geng -d3 -D3 -c -tf -q {n}")
    ap.add_argument(
        "--filter-cmd",
        default="python scripts/catalogue.py {cubic_g5} --filter nontrivial-snark --emit-jsonl",
    )
    ap.add_argument("--intermediate-dir", type=pathlib.Path, required=True)
    ap.add_argument("--cert-dir", type=pathlib.Path, default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    name = args.name or args.catalogue.stem
    manifest = build_manifest(
        catalogue=args.catalogue,
        orders=args.orders,
        geng_pattern=args.geng,
        filter_cmd_pattern=args.filter_cmd,
        intermediate_dir=args.intermediate_dir,
        cert_dir=args.cert_dir,
        name=name,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2))
    print(f"wrote {args.out}")
    print(
        f"  total_nontrivial_snarks={manifest['summary']['total_nontrivial_snarks']}"
    )
    if "interval_certificates" in manifest:
        print(
            f"  interval_certificates: n_files={manifest['interval_certificates']['n_files']} "
            f"directory_sha256={manifest['interval_certificates']['directory_sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
