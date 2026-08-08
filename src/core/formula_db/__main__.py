"""CLI entry point for formula database operations.

Usage:
    python -m src.core.formula_db build --output <path> [--max-mass 1000]
    python -m src.core.formula_db build --output <path> --max-mass 50  # test
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Formula database builder for NOM-HRMS-FGA",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── build ──
    build_p = sub.add_parser("build", help="Build a formula database offline")
    build_p.add_argument(
        "--output", type=Path, required=True,
        help="Output path prefix (writes <output>.fdb + <output>.manifest.json)",
    )
    build_p.add_argument(
        "--max-mass", type=float, default=1000.0,
        help="Maximum neutral monoisotopic mass (Da). Default 1000.",
    )
    build_p.add_argument(
        "--elements", type=str, default="CHNOSP",
        help="Elements to include. Default CHNOSP.",
    )
    build_p.add_argument(
        "--profile", type=str, default="dbe_nonnegative_even_p3_s2",
        help="Validity profile. Default dbe_nonnegative_even_p3_s2.",
    )
    build_p.add_argument(
        "--bin-width", type=float, default=0.1,
        help="Mass bin width (Da). Default 0.1.",
    )
    build_p.add_argument(
        "--compression-level", type=int, default=9,
        help="Zstd compression level (1-22). Default 9.",
    )

    args = parser.parse_args()

    if args.command == "build":
        from ._builder import BuildConfig, build_database

        config = BuildConfig(
            output=args.output,
            max_mass=args.max_mass,
            elements=tuple(args.elements),
            profile=args.profile,
            bin_width=args.bin_width,
            compression_level=args.compression_level,
        )
        build_database(config)


if __name__ == "__main__":
    main()
