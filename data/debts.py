import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Debt(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'debts'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    collector_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String)
    tag = sqlalchemy.Column(sqlalchemy.String, unique=True)
    group = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'), nullable=True)
    time = sqlalchemy.Column(sqlalchemy.DateTime)
