from os import environ


def get_database_url() -> str:
    protocol = "mysql+mysqldb"
    db_user = environ['DB_USER']
    db_pass = environ['DB_PASS']
    db_host = environ['DB_HOST']
    db_port = environ['DB_PORT']
    db_name = environ['DB_NAME']
    return f"{protocol}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
