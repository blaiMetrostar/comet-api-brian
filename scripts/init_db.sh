#!/bin/bash
# Initialize PostgreSQL database for Comet API
# Usage: ./scripts/init_db.sh [--seed]

set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

echo "Initializing PostgreSQL database..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Python initialization script
python scripts/init_postgres.py "$@"
