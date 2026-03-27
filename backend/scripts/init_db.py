from app.services.database_service import initialize_database


def main() -> None:
    status = initialize_database()
    print(
        f"Database ready={status.ready} path={status.sqlite_path} "
        f"wal_mode={status.wal_mode} foreign_keys={status.foreign_keys}"
    )


if __name__ == "__main__":
    main()
