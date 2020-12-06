import alembic.config

print()
print("Running Alembic migrations...")
print()

alembic_args = ["--raiseerr", "upgrade", "head"]
alembic.config.main(argv=alembic_args)

print()
print("Migrations finished successfully!")
print()

from src.models import SimpleModel
print("Loaded model: SimpleModel")

from src.database import Session

db = Session()
print('Loaded session. It is accessible as "db" variable.')
