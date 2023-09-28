Run ETL from Kafka to ClickHouse locally:

- python3.11 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- make build
- export DEBUG=True
- make etl
