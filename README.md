# Track-5Sem2025ETL

Repository intended for the implementation of an academic project in partnership with a real company.

## About the Project

This ETL (Extract, Transform, Load) project is designed to process and manage data efficiently. It integrates with the Taiga API to extract project-related data, transform it into meaningful insights, and load it into a PostgreSQL data warehouse. The project is implemented using Python and leverages libraries such as SQLAlchemy, Pandas, and Requests for database operations, data manipulation, and API communication.

## Prerequisites

- Python 3.10 or 3.11
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

Run the tests to ensure the project is functioning correctly:

```bash
pytest etl_taiga/tests/
```

## Additional Information

This project is part of an academic initiative and is tailored for educational purposes. Contributions and feedback are welcome!
