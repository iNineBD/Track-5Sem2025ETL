# Track-5Sem2025ETL

Repository intended for the implementation of an academic project in partnership with a real company.

## About the Project

This ETL (Extract, Transform, Load) project is designed to process and manage data efficiently. It integrates with the Taiga API to extract project-related data, transform it into meaningful insights, and load it into a PostgreSQL data warehouse. The project is implemented using Python and leverages libraries such as SQLAlchemy, Pandas, and Requests for database operations, data manipulation, and API communication.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- pip (Python Package Manager)

## Cloning the Repository

Clone this repository using the following commands:

```bash
git clone https://github.com/your-repo/Track-5Sem2025ETL.git
cd Track-5Sem2025ETL
```

Replace the placeholders with your database and Taiga API credentials.

## Installing Dependencies

Install the project dependencies with the command:

```bash
pip install -r requirements.txt
```

## Accessing the Data

After running the ETL pipeline, the processed data will be available in the PostgreSQL database specified in the `.env` file.

```bash
DB_HOST=localhost
DB_DATABASE=projeto_tarefas
DB_SCHEMA=public
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=senha123

TAIGA_HOST=https://taiga.example.com
TAIGA_USER=taiga_admin
TAIGA_PASSWORD=taiga_pass
TAIGA_MEMBER=eduardo_f_paula

JIRA_HOST=https://jira.example.com
JIRA_USER=eduardo.jira
JIRA_TOKEN=jiraToken123abcXYZ456

EMAIL_EDUARDO=eduardo.fariasp@example.com
EMAIL_ANA=ana.silva@example.com
EMAIL_LUCAS=lucas.rocha@example.com
EMAIL_ANDRE=andre.martins@example.com
EMAIL_ALI=ali.khan@example.com
EMAIL_ALITA=alita.garcia@example.com
EMAIL_WILLIAM=william.souza@example.com
```

## Testing the Project

Run the tests to ensure that the project is working correctly:

Runs the flake8 linter on the etl_taiga directory to check if the code follows Python style best practices (PEP8).

```bash
flake8 etl_taiga
```
```bash
Runs the tests and details the coverage in ```index.html``` in the "coverage_report" directory at the root of the project.
Evaluate the report using the user's preferred browser
```
```bash
pytest --disable-warnings --cov=etl_taiga --cov-report=html:coverage_report --cov-report=xml:coverage_report/coverage.xml
```


## Starting the Prefect Service

This project uses a `prefect.yaml` file to configure and run the Prefect project.

### Initialize the Prefect Project (if not already initialized)

```bash
prefect project init
```

This will create or update the `prefect.yaml` file.

### Deploy the Flow with Prefect

```bash
prefect deploy --all
```

This will build and register all deployments defined in your `prefect.yaml`.

### Start an Agent to Run the Flow

```bash
prefect agent start --pool default-agent-pool
```

> ⚠️ Replace `default-agent-pool` with the actual name of your agent pool if different.

---
