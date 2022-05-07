import flask
from flask import jsonify, request
from . import db_session
from .debtors import Debtor
from flask_restful import Resource



class DebtorResource(Resource):
    def put(self):
        db_sess = db_session.create_session()
        changed = False
        if not 'id' in request.json.keys():
            debtor = Debtor()
        else:
            debtor = db_sess.query(Debtor).filter(Debtor.id == request.json['id']).first()
            changed = True
        debtor.user_id = request.json['user_id']
        debtor.debt_id = request.json['debt_id']
        debtor.sum = request.json['sum']
        debtor.collector_id = request.json['collector_id']
        if changed:
            db_sess.merge(debtor)
        else:
            db_sess.add(debtor)
        db_sess.commit()
        return jsonify('ok')

    def get(self):
        db_sess = db_session.create_session()
        out = db_sess.query(Debtor).all()
        out = list(map(lambda x: x.to_dict(), out))
        return jsonify(out)


class OneDebtorResource(Resource):
    def get(self, debtor_id):
        db_sess = db_session.create_session()
        out = db_sess.query(Debtor).filter(Debtor.id == debtor_id).first()
        return jsonify(out.to_dict())

    def delete(self, debtor_id):
        db_sess = db_session.create_session()
        debtor = db_sess.query(Debtor).filter(Debtor.id == debtor_id).first()
        db_sess.delete(debtor)
        db_sess.commit()
        return jsonify('ok')
