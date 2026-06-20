from __future__ import annotations

import argparse

from .cli import build_resources


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Python NeoForge definitions into resources.")
    parser.add_argument("script", help="Python mod definition script to execute")
    parser.add_argument("--mod-id", default="python_for_neoforge")
    parser.add_argument("--mod-version", help="Minecraft target version code, for example 1211 -> 1.21.1")
    parser.add_argument("--resources", default="neoforge-mod/src/main/resources")
    args = parser.parse_args()

    build_resources(args)


if __name__ == "__main__":
    main()
