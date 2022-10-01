import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Group_Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'group_notifications'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    time = sqlalchemy.Column(sqlalchemy.DateTime)


class Friend_Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'friend_notifications'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    time = sqlalchemy.Column(sqlalchemy.DateTime)


class Debt_Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'debt_notifications'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    debt_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('debts.id'))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    time = sqlalchemy.Column(sqlalchemy.DateTime)