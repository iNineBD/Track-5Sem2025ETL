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

## Testing the Project

Run the tests to ensure that the project is working correctly:

Runs the flake8 linter on the etl_taiga directory to check if the code follows Python style best practices (PEP8).

```bash
flake8 etl_taiga
```

Runs the tests and details the coverage in ```index.html``` in the "coverage_report" directory at the root of the project.
Evaluate the report using the user's preferred browser

```bash
pytest --disable-warnings --cov=etl_taiga --cov-report=html:coverage_report --cov-report=xml:coverage_report/coverage.xml
```

## Additional Information

This project is part of an academic initiative and is tailored for educational purposes. Contributions and feedback are welcome!
