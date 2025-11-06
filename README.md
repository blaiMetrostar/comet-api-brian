# Welcome to the Comet API!

The goal of this project is to provide a Python-based starter API, which comes pre-configured with tools supporting the accelerated development of both Comet as well as general python APIs. Some of these tools are as follows:

- Platform: Python
- Web Framework: Fast API
- Database: SQLite, Alembic
- ORM: SQLAlchemy
- Data Validation: Pydantic
- Unit Testing: PyTest
- Code Quality: Ruff, PyLint, Black, isort
- Authentication support: JWT
- Documentation: Swagger and ReDoc

## Table of Contents

1. [Running the Project Locally](#running-the-project-locally)
2. [Running with Docker](#running-with-docker)
3. [Initializing PostgreSQL Database](#initializing-postgresql-database)
4. [Running Unit Tests](#running-unit-tests)
5. [Running Code Quality Checks](#running-code-quality-checks)
6. [Running Code Formatting](#running-code-formatting)
7. [Publishing Updated Docs](#publishing-updated-docs)
8. [Contributing](#contributing)
9. [Next Steps](#next-steps)

## Running the Project Locally

To override default environment variables, add a `.env` file to the `comet-api` directory and update as needed (optional):

```
API_PREFIX=[SOME_ROUTE] # Ex: '/api'
DATABASE_URL=[SOME_URL] # Ex: 'postgresql://username:password@localhost:5432/database_name'
OIDC_CONFIG_URL=[SOME_URL] # Ex: 'https://keycloak.auth.metrostar.cloud/auth/realms/dev/.well-known/openid-configuration'
LOG_LEVEL=[LOG_LEVEL] # Ex: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' (Default: 'INFO')
```

### Option 1: Using uv (recommended)

1. To install project dependencies, run the following:

```sh
uv sync
```

2. To install dev dependencies, run the following:

```sh
uv sync --extra dev
```

3. To start the app, run the following:

```sh
uv run uvicorn app.main:app --reload --host=0.0.0.0 --port=5000
```

4. Access the swagger docs by navigating to: `http://0.0.0.0:5000/docs`

### Option 2: Using virtualenv and pip

1. To create an environment, run the following:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

2. To install project dependencies, run the following:

```sh
pip install .
```

3. To install dev dependencies, run the following (optional):

```sh
pip install -e ".[dev]"
```

4. To start the app, run the following:

```sh
uvicorn app.main:app --reload --host=0.0.0.0 --port=5000
```

5. Access the swagger docs by navigating to: `http://0.0.0.0:5000/docs`

## Running with Docker

1. To build the image, run the following:

```sh
docker build . -t comet-api
```

2. To run the container, run the following:

```sh
docker run -p 5000:5000 --name comet-api comet-api
```

3. Access the swagger docs by navigating to: `http://0.0.0.0:5000/docs`

## Initializing PostgreSQL Database

If you're using PostgreSQL instead of SQLite, you can use the provided initialization script to set up your database:

1. Ensure your `.env` file contains a PostgreSQL DATABASE_URL:

```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

2. Run the initialization script using either method:

**Using the shell script:**

```sh
./scripts/init_db.sh
```

**Or using Python directly:**

```sh
python scripts/init_postgres.py
```

3. To seed initial data along with the schema (optional):

```sh
./scripts/init_db.sh --seed
```

**Script Options:**

- `--seed`: Seed initial data after running migrations
- `--skip-create`: Skip database creation (only run migrations)

The script will:

- Create the database if it doesn't exist
- Run all Alembic migrations to set up the schema
- Optionally seed initial data

## Running Unit Tests

1. To run unit tests, run the following:

```sh
pytest
```

2. To run unit tests with code coverage, run the following:

```sh
coverage run -m pytest && coverage html
```

## Running Code Quality Checks

1. To run code quality checks, run the following:

```sh
ruff check .
```

## Running Code Formatting

1. To run code formatting, run the following:

```sh
ruff format .
```

## Publishing Updated Docs

1. Access the swagger ReDocs by navigating to: `http://0.0.0.0:5000/redoc`

2. Click the Download button

3. Copy the downloaded file into the `comet-api/docs` directory

4. To convert the json into html, run the following:

```sh
npx @redocly/cli build-docs docs/openapi.json --output docs/index.html
```

5. Commit the spec and html files and merge into `main` to publish docs

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature_a`)
3. Commit your Changes (`git commit -m 'Added new feature_a'`)
4. Push to the Branch (`git push origin feature_a`)
5. Open a Pull Request

## Next Steps

The following provides a short list of tasks which are potential next steps for this project. These could be steps in making use of this baseline or they could be for learning purposes.

- [ ] Add/Update existing endpoints with more applicable entities and/or columns
- [ ] Update applicable endpoints to require JWT
- [ ] Replace default database with external database (Ex. Postgres)
- [ ] Deploy to cloud infrastructure
- [ ] Automate doc publishing process
