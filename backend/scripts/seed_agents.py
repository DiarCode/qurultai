"""Seed or replace the local agent catalog with the Kazakhstan government structure.

Usage:
    uv run python -m scripts.seed_agents
    uv run python -m scripts.seed_agents --replace-existing
"""

from __future__ import annotations

import argparse

from sqlmodel import Session

from app.db.engine import engine
from app.services.database_service import initialize_database
from app.services.kz_government_catalog import seed_kz_government_catalog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Delete existing agents and reseed the canonical Kazakhstan government catalog.",
    )
    args = parser.parse_args()

    initialize_database()
    with Session(engine) as session:
        summary = seed_kz_government_catalog(session, replace_existing_agents=args.replace_existing)

    print("Kazakhstan government catalog seeded.")
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
