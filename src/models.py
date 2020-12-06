from enum import Enum
from typing import Any

from sqlalchemy import Column, DateTime, Float, func, Integer, MetaData, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy_utils import ChoiceType


metadata = MetaData(
    naming_convention={
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(column_0_label)s",
        "pk": "pk_%(table_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
    }
)
Base = declarative_base(metadata=metadata)


class BasicMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self):
        return self.to_string(id=self.id)

    def __repr__(self) -> str:
        return self.to_string(id=self.id)

    def to_string(self, **fields: Any) -> str:
        field_strings = []
        at_least_one_attached_attribute = False

        for key, field in fields.items():
            try:
                field_strings.append(f"{key}={field!r}")
            except DetachedInstanceError:
                field_strings.append(f"{key}=DetachedInstanceError")
            else:
                at_least_one_attached_attribute = True

        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({', '.join(field_strings)})>"
        else:
            return f"<{self.__class__.__name__} {id(self)}>"


class SimpleModel(BasicMixin, Base):
    class Type(Enum):
        NORMAL = "NORMAL"
        SUPER = "SUPER"

    col_1 = Column(String(length=100))
    col_2 = Column(String(length=100))
    type = Column(ChoiceType(Type))
    value = Column(Float)

    __table_args__ = (UniqueConstraint("col_1", "col_2"),)

    def __repr__(self) -> str:
        return self.to_string(
            id=self.id, col_1=self.col_1, col_2=self.col_2, type=self.type, value=self.value
        )

    @classmethod
    def get_latest_by_type(cls, db: Session, type_: Type) -> "SimpleModel":
        return db.query(cls).filter(cls.type == type_).order_by(cls.created_at.desc()).first()
