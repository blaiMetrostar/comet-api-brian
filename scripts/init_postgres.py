#!/usr/bin/env python3
"""Initialize PostgreSQL database for Comet API.

This script:
1. Creates the database if it doesn't exist
2. Runs Alembic migrations to set up the schema
3. Optionally seeds initial data

Usage:
    python scripts/init_postgres.py [--seed]
"""

import argparse
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings


def parse_database_url(url: str) -> dict:
    """Parse PostgreSQL database URL.

    Args:
        url: Database URL in format postgresql://user:password@host:port/dbname

    Returns:
        Dictionary with connection parameters.
    """
    # Remove postgresql:// prefix
    url = url.replace("postgresql://", "")

    # Split credentials and host
    if "@" in url:
        credentials, host_part = url.split("@")
        username, password = credentials.split(":")
    else:
        raise ValueError("Invalid database URL format")

    # Split host and database
    host_port, dbname = host_part.split("/")

    # Split host and port
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"

    return {
        "user": username,
        "password": password,
        "host": host,
        "port": int(port),
        "dbname": dbname,
    }


def create_database(db_params: dict) -> None:
    """Create database if it doesn't exist.

    Args:
        db_params: Database connection parameters.
    """
    dbname = db_params["dbname"]
    conn_params = db_params.copy()
    conn_params["dbname"] = "postgres"  # Connect to default database

    print(f"Checking if database '{dbname}' exists...")

    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"Database '{dbname}' already exists.")
        else:
            # Create database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
            print(f"Database '{dbname}' created successfully.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)


def run_migrations() -> None:
    """Run Alembic migrations to set up database schema."""
    import subprocess

    print("\nRunning Alembic migrations...")

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        print("Migrations completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Alembic not found. Please install it with: pip install alembic")
        sys.exit(1)


def seed_initial_data() -> None:
    """Seed initial data into the database."""
    from sqlalchemy.orm import Session

    from app.db import SessionLocal

    print("\nSeeding initial data...")

    db: Session = SessionLocal()

    try:
        # Add your initial data seeding logic here
        # Example:
        # from app.users.models import DBUser
        # admin_user = DBUser(
        #     username="admin",
        #     email="admin@example.com",
        #     is_active=True,
        # )
        # db.add(admin_user)
        # db.commit()

        print("Initial data seeded successfully.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    """Main function to initialize PostgreSQL database."""
    parser = argparse.ArgumentParser(
        description="Initialize PostgreSQL database for Comet API"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed initial data after running migrations",
    )
    parser.add_argument(
        "--skip-create",
        action="store_true",
        help="Skip database creation (only run migrations)",
    )

    args = parser.parse_args()

    # Check if using PostgreSQL
    if not settings.DATABASE_URL.startswith("postgresql"):
        print("Error: This script is only for PostgreSQL databases.")
        print(f"Current DATABASE_URL: {settings.DATABASE_URL}")
        sys.exit(1)

    print("=" * 60)
    print("Comet API - PostgreSQL Database Initialization")
    print("=" * 60)
    print(f"\nDatabase URL: {settings.DATABASE_URL}")

    # Parse database URL
    try:
        db_params = parse_database_url(settings.DATABASE_URL)
    except ValueError as e:
        print(f"Error parsing database URL: {e}")
        sys.exit(1)

    # Create database
    if not args.skip_create:
        create_database(db_params)

    # Run migrations
    run_migrations()

    # Seed data if requested
    if args.seed:
        seed_initial_data()

    print("\n" + "=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
