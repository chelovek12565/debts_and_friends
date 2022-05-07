from . import db_session
from flask import jsonify, request, make_response
from .groups import Group, GroupMember
from .users import User
from .debts import Debt
from flask_restful import Resource


class GroupResource(Resource):
    def put(self):
        db_sess = db_session.create_session()
        if not 'id' in request.json.keys():
            users = request.json['users_ids']
            for i in users:
                if not db_sess.query(User).filter(User.id == i):
                    return make_response(jsonify({'error': f'User with id {i} is not existing'}), 400)
            group = Group()
            group.tag = request.json['tag']
            group.admin_id = request.json['admin_id']
            db_sess.add(group)
            db_sess.commit()
            for i in users:
                group_member = GroupMember()
                group_member.group_id = group.id
                group_member.user_id = i
                db_sess.add(group_member)
        else:
            if 'new_member' in request.json.keys():
                member = GroupMember()
                member.group_id = request.json['id']
                member.user_id = request.json['new_member']
                db_sess.add(member)
                db_sess.commit()
            elif 'delete_member' in request.json.keys():
                member = db_sess.query(GroupMember).filter(GroupMember.user_id == request.json['delete_member']).first()
                db_sess.delete(member)
                db_sess.commit()
        db_sess.commit()
        return jsonify('ok')

    def get(self):
        db_sess = db_session.create_session()
        groups = db_sess.query(Group).all()
        out = {}
        for i in groups:
            out[i.id] = {
                'users': list(map(lambda x: x.user_id, db_sess.query(GroupMember).filter
                (GroupMember.group_id == i.id).all())),
                'debts': list(map(lambda x: x.id, db_sess.query(Debt).filter(Debt.group == i.id).all())),
                'admin_id': i.admin_id
            }
        return jsonify(out)


class OneGroupResource(Resource):
    def delete(self, group_id):
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            return make_response(jsonify({'error': f'Group with id {group_id} is not existing'}), 400)
        debts = db_sess.query(Debt).filter(Debt.group == group_id).all()
        if debts:
            return make_response(jsonify({'error': 'This group has an unclosed debts'}), 400)
        users = db_sess.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        for i in users:
            db_sess.delete(i)
            db_sess.commit()
        db_sess.delete(group)
        db_sess.commit()
        return jsonify('ok')

    def get(self, group_id):
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            return make_response(jsonify({'error': f'Group with id {group_id} is not existing'}), 400)
        out = {
            'users': list(
                map(lambda x: x.user_id, db_sess.query(GroupMember).filter(GroupMember.group_id == group_id).all())),
            'debts': list(map(lambda x: x.id, db_sess.query(Debt).filter(Debt.group == group_id).all())),
            'admin_id': group.admin_id
        }
        return jsonify(out)
