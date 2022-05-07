import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Debtor(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'debtors'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    debt_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('debts.id'))
    collector_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    sum = sqlalchemy.Column(sqlalchemy.Integer)
    # user = orm.relation('User')