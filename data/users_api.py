import flask
from . import db_session
from flask import request
from .users import User
from flask_restful import Resource


class UserResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        out = db_sess.query(User).all()
        out = list(map(lambda x: x.to_dict(), out))
        return flask.jsonify(out)

    def put(self):
        db_sess = db_session.create_session()
        found = False
        if 'id' in request.json.keys():
            user = db_sess.query(User).filter(User.id == request.json['id']).first()
            print('f')
            found = True
        else:
            user = User()
        user.name = request.json['name']
        user.surname = request.json['surname']
        user.username = request.json['username']
        user.password = request.json['password']
        if not found:
            db_sess.add(user)
        else:
            db_sess.merge(user)
        db_sess.commit()
        return flask.jsonify('ok')


class OneUserResource(Resource):
    def get(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        return flask.jsonify(user.to_dict())

    def delete(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        db_sess.delete(user)
        db_sess.commit()
        return flask.jsonify('ok')
