import factory

from src.database import Session
from src.models import SimpleModel


class BasicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = Session

    id = factory.Sequence(lambda x: x + 1)


class SimpleModelFactory(BasicFactory):
    class Meta:
        model = SimpleModel
