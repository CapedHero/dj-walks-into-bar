from freezegun import freeze_time
from sqlalchemy import exists, func, or_
from sqlalchemy.orm import Session

from src.models import SimpleModel
from .factories import SimpleModelFactory


def test_count(db: Session):
    # WHEN
    SimpleModelFactory()

    # THEN
    assert db.query(SimpleModel).count() == 1


def test_exists(db: Session):
    # GIVEN
    db_obj = SimpleModelFactory(id=1)
    non_existent_id = 2

    # WHEN & THEN
    assert db.query(exists().where(SimpleModel.id == db_obj.id)).scalar() is True
    assert db.query(exists().where(SimpleModel.id == non_existent_id)).scalar() is False


def test_filters(db: Session):
    # GIVEN
    SimpleModelFactory(col_1="foo", col_2="spam")
    SimpleModelFactory(col_1="foo", col_2="eggs")
    SimpleModelFactory(col_1="bar", col_2="spam")

    # WHEN
    foo_count_1 = db.query(SimpleModel).filter_by(col_1="foo").count()
    foo_count_2 = db.query(SimpleModel).filter(SimpleModel.col_1 == "foo").count()
    foo_or_spam_count = (
        db.query(SimpleModel)
        .filter(or_(SimpleModel.col_1 == "foo", SimpleModel.col_2 == "spam"))
        .count()
    )

    # THEN
    assert foo_count_1 == foo_count_2 == 2
    assert foo_or_spam_count == 3


def test_order_by(db: Session):
    # GIVEN
    SimpleModelFactory(col_1="zzz")
    SimpleModelFactory(col_1="aaa")

    # WHEN
    ascending = db.query(SimpleModel.col_1).order_by(SimpleModel.col_1)
    descending = db.query(SimpleModel.col_1).order_by(SimpleModel.col_1.desc())

    # THEN
    assert [row.col_1 for row in ascending] == ["aaa", "zzz"]
    assert [row.col_1 for row in descending] == ["zzz", "aaa"]


def test_avg_and_sum_simple(db: Session):
    # GIVEN
    SimpleModelFactory(value=0)
    SimpleModelFactory(value=5)

    # WHEN
    db_objs = db.query(
        func.avg(SimpleModel.value).label("avg"),
        func.sum(SimpleModel.value).label("sum"),
    )

    # THEN
    assert db_objs[0].avg == 2.5
    assert db_objs[0].sum == 5.0


def test_avg_and_sum_grouped_by(db: Session):
    # GIVEN
    SimpleModelFactory(type=SimpleModel.Type.NORMAL, value=0)
    SimpleModelFactory(type=SimpleModel.Type.NORMAL, value=5)
    SimpleModelFactory(type=SimpleModel.Type.SUPER, value=5)
    SimpleModelFactory(type=SimpleModel.Type.SUPER, value=10)

    db_objs = (
        db.query(
            SimpleModel.type,
            func.avg(SimpleModel.value).label("avg"),
            func.sum(SimpleModel.value).label("sum"),
        )
        .group_by(SimpleModel.type)
        .order_by(SimpleModel.type)
    )

    assert db_objs[0].type == SimpleModel.Type.NORMAL
    assert db_objs[0].avg == 2.5
    assert db_objs[0].sum == 5

    assert db_objs[1].type == SimpleModel.Type.SUPER
    assert db_objs[1].avg == 7.5
    assert db_objs[1].sum == 15


def test_avg_and_sum_annotated(db: Session):
    # GIVEN
    SimpleModelFactory(type=SimpleModel.Type.NORMAL, value=0)
    SimpleModelFactory(type=SimpleModel.Type.NORMAL, value=5)
    SimpleModelFactory(type=SimpleModel.Type.SUPER, value=5)
    SimpleModelFactory(type=SimpleModel.Type.SUPER, value=10)

    avg_sum_subquery = (
        db.query(
            SimpleModel.type,
            func.avg(SimpleModel.value).label("avg"),
            func.sum(SimpleModel.value).label("sum"),
        )
        .group_by(SimpleModel.type)
        .subquery()
    )

    db_objs = (
        db.query(
            SimpleModel,
            avg_sum_subquery.c.avg,
            avg_sum_subquery.c.sum,
        )
        .join(avg_sum_subquery, SimpleModel.type == avg_sum_subquery.c.type)
        .order_by(SimpleModel.type)
    )

    for i in [0, 1]:
        assert db_objs[i].SimpleModel.type == SimpleModel.Type.NORMAL
        assert db_objs[i].avg == 2.5
        assert db_objs[i].sum == 5

    for i in [2, 3]:
        assert db_objs[i].SimpleModel.type == SimpleModel.Type.SUPER
        assert db_objs[i].avg == 7.5
        assert db_objs[i].sum == 15


def test_class_getters_aka_quasi_manager(db: Session):
    # GIVEN
    with freeze_time("2020-01-02 03:45") as older_timestamp:
        timestamp = older_timestamp.time_to_freeze
        SimpleModelFactory(type=SimpleModel.Type.NORMAL, created_at=timestamp)
        SimpleModelFactory(type=SimpleModel.Type.SUPER, created_at=timestamp)

    with freeze_time("2021-02-03 04:56") as newer_timestamp:
        timestamp = newer_timestamp.time_to_freeze
        obj_to_return = SimpleModelFactory(type=SimpleModel.Type.NORMAL, created_at=timestamp)
        SimpleModelFactory(type=SimpleModel.Type.SUPER, created_at=timestamp)

    # WHEN
    result = SimpleModel.get_latest_by_type(db, SimpleModel.Type.NORMAL)

    # THEN
    assert result == obj_to_return
