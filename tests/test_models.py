import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from src.models import SimpleModel
from tests.factories import SimpleModelFactory


def test_str_representation(db: Session):
    # WHEN
    instance = SimpleModelFactory()

    # THEN
    assert str(instance) == f"<SimpleModel(id={instance.id})>"


def test_repr_representation(db: Session):
    # WHEN
    instance = SimpleModelFactory()

    # THEN
    assert repr(instance) == (
        f"<"
        f"SimpleModel("
        f"id={instance.id}, "
        f"col_1={instance.col_1}, "
        f"col_2={instance.col_2}, "
        f"type={instance.type}, "
        f"value={instance.value}"
        f")>"
    )


class TestChoices:
    def test_valid_value(self, db: Session):
        # WHEN
        instance = SimpleModel(type=SimpleModel.Type.SUPER)
        db.add(instance)
        db.commit()

        # THEN
        assert instance.type == SimpleModel.Type.SUPER

    def test_invalid_value(self, db: Session):
        # THEN 1
        with pytest.raises(StatementError) as exc:
            # WHEN
            db.add(SimpleModel(type="INVALID_TYPE"))
            db.commit()

        # THEN 2
        assert "is not a valid" in str(exc)


def test_unique_together(db: Session):
    # GIVEN
    db.add(SimpleModel(col_1="foo", col_2="bar"))
    db.add(SimpleModel(col_1="foo", col_2="bar"))

    # THEN 1
    with pytest.raises(IntegrityError) as exc:
        # WHEN
        db.commit()

    # THEN 2
    assert "Duplicate entry" in str(exc)
