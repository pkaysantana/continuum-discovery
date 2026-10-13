"""Stage B subprocess. No source discovery and no historical runner imports."""
import argparse
import json
import os
from pathlib import Path
from . import provenance as p
from .export import approved_export, verify_export
from .harness import evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--synthetic-directory", type=Path)
    parser.add_argument("--export-sha256")
    parser.add_argument("--receipt-sha256")
    args = parser.parse_args()
    if args.development:
        if args.synthetic_directory is not None:
            raise PermissionError("cannot mix synthetic and development modes")
        bundle, _ = approved_export()
    else:
        if args.synthetic_directory is None:
            parser.error("explicit synthetic fixture directory required")
        root = args.synthetic_directory
        manifest = json.loads((root / "manifest.json").read_bytes())
        if manifest["kind"] != "synthetic" or any(not r["id"].startswith("SYN_") for r in manifest["members"]):
            raise PermissionError("synthetic worker requires synthetic fixture manifest")
        bundle, _ = verify_export(root / "export.json", root / "receipt.json", manifest,
                                 export_sha256=args.export_sha256, receipt_sha256=args.receipt_sha256)
    result = evaluate(bundle["records"], bundle["provenance"], approve_development=args.development)
    with Path(os.environ["GSK_CANDIDATE_RESULT"]).open("xb") as fh:
        fh.write(p.encoded(result))


if __name__ == "__main__":
    main()
