"""Reproduce the public, aggregate-data part of the paired-state audit.

This entry point validates the privacy-reviewed aggregate CSVs, renders the
four main figures and six supplementary figures, and records the environment.
It does not claim to rerun analyses that require restricted participant data.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE / "scripts"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACKAGE / "outputs",
                        help="Output directory for figures and validation reports")
    parser.add_argument("--main-only", action="store_true",
                        help="Render only the four manuscript figures")
    parser.add_argument("--include-amr", action="store_true",
                        help="Also reanalyze the bundled public One Health AMR isolate records")
    parser.add_argument("--include-reviewer-checks", action="store_true",
                        help="Include AMR, all 168 exploratory comparisons and reviewer checks")
    args = parser.parse_args()
    if args.include_reviewer_checks:
        args.include_amr = True
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "validation.json"
    subprocess.run([sys.executable, "-B", str(SCRIPTS / "validate_derived_data.py"),
                    "--report", str(report)], check=True)
    command = [sys.executable, "-B", str(SCRIPTS / "render_submission_revision.py"), "--output", str(output)]
    if args.main_only:
        command.append("--main-only")
    subprocess.run(command, check=True)
    if args.include_amr:
        command = [sys.executable, "-B", str(PACKAGE / "one_health_amr" / "reproduce_amr.py")]
        if args.include_reviewer_checks:
            command.append("--include-reviewer-checks")
        subprocess.run(command, check=True)
        # Refresh the submission displays from the recomputed public/synthetic outputs.
        command = [sys.executable, "-B", str(SCRIPTS / "render_submission_revision.py"), "--output", str(output)]
        if args.main_only:
            command.append("--main-only")
        subprocess.run(command, check=True)
    versions = {}
    packages = ["numpy", "pandas", "matplotlib"]
    if args.include_amr:
        packages.extend(["scipy", "statsmodels", "Pillow"])
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    manifest = {
        "status": "passed",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
        "input_scope": "aggregate human results and public bacterial isolate metadata"
        if args.include_amr else "aggregate derived CSVs only",
        "participant_level_data_included": False,
        "raw_data_reanalysis": bool(args.include_amr),
        "raw_data_reanalysis_scope": "public bacterial isolate metadata only"
        if args.include_amr else "none",
        "restricted_human_raw_data_reanalysis": False,
        "one_health_amr_included": bool(args.include_amr),
        "reviewer_checks_included": bool(args.include_reviewer_checks),
        "figures": "revised main figures 1-4 and supplementary figures S1-S7"
        if not args.main_only else "main figures 1-4",
    }
    (output / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
