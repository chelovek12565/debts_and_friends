import flask
from . import db_session
from flask import Blueprint, request
from .debts import Debt
from flask_restful import Resource


class DebtsResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        data = db_sess.query(Debt).all()
        out = []
        for i in data:
            out.append(i.to_dict())
        return flask.jsonify(out)

    def put(self):
        db_sess = db_session.create_session()
        found = False
        if 'id' in request.json.keys():
            debt = db_sess.query(Debt).filter(Debt.id == request.json['id']).first()
            found = True
        else:
            debt = Debt()
        debt.collector_id = request.json['collector_id']
        debt.name = request.json['name']
        debt.tag = request.json['tag']
        if 'group' in request.json.keys():
            debt.group = request.json['group']
        debt.sum = request.json['sum']
        if not found:
            db_sess.add(debt)
        db_sess.commit()
        return flask.jsonify({'success': 'ok'})


class OneDebtsResource(Resource):
    def get(self, debt_id):
        db_sess = db_session.create_session()
        debt = db_sess.query(Debt).filter(Debt.id == debt_id).first()
        if not debt:
            return flask.make_response(flask.jsonify({'error': 'Bad Request'}), 400)
        return flask.jsonify(debt.to_dict())

    def delete(self, debt_id):
        db_sess = db_session.create_session()
        debt = db_sess.query(Debt).filter(Debt.id == debt_id).first()
        db_sess.delete(debt)
        db_sess.commit()
        return flask.jsonify({'success': 'ok'})


