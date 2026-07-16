"""Command line interface for buildgen."""

from __future__ import annotations

import argparse
import pathlib
import sys

from .generator import BuildManifest, BuildScriptGenerator


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="buildgen",
        description=(
            "Generate platform-specific build scripts (Makefile and "
            "mswin32/Build.bat) from a single build.yaml manifest."
        ),
    )
    parser.add_argument("manifest", type=pathlib.Path, help="Path to a build.yaml manifest")
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Directory to write generated build scripts into (default: current directory)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not args.manifest.exists():
        print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    try:
        manifest = BuildManifest.from_yaml(args.manifest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    generator = BuildScriptGenerator(manifest)
    written = generator.write(args.output)

    print(f"Generated build scripts for '{manifest.name}' v{manifest.version}:")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
