#!/usr/bin/env python3
"""Stage supplied HTML byte-for-byte, or verify a staged copy against its source.

This is a file helper, not a deployment API. It does not parse or execute HTML.
Existing CSP and iframe sandbox attributes remain unchanged because all bytes do.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Sites project/static-root directory")
    parser.add_argument("--verify", action="store_true", help="Verify index.html against the supplied source")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace the staged index and manifest")
    args = parser.parse_args(argv)
    try:
        source = args.source.expanduser().resolve(strict=True)
        out = args.out.expanduser().resolve()
        target = out / "index.html"
        manifest_path = out / "preserved-source.json"
        if not source.is_file():
            raise ValueError("Source must be a regular file")
        if source == target or source == manifest_path:
            raise ValueError("Source and output must be different files")
        expected = digest(source)
        if args.verify:
            if not target.is_file() or digest(target) != expected:
                raise ValueError("The staged file differs from the supplied source")
            print(json.dumps({"verified":True,"sha256":expected}))
            return 0
        if source.suffix.lower() not in (".html", ".htm"):
            raise ValueError("Source must be an .html or .htm file")
        if target.is_symlink() or manifest_path.is_symlink():
            raise ValueError("Refusing to replace a symlink")
        if (target.exists() or manifest_path.exists()) and not args.overwrite:
            raise ValueError("Staged output exists; choose a new directory or --overwrite")
        content = source.read_bytes()
        out.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
        manifest = {"schema_version":1,"source_sha256":expected,"staged_sha256":digest(target),
                    "entrypoint":"index.html","mode":"byte-for-byte", "execution":"none"}
        manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        if digest(target) != expected:
            raise ValueError("Copy verification failed")
        print(json.dumps({"entrypoint":str(target),"sha256":expected,"verified":True}))
        return 0
    except (OSError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
