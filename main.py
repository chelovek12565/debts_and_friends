import os
import flask
from data.debts_api import DebtsResource, OneDebtsResource
from data.users_api import UserResource, OneUserResource
from data.debtors_api import DebtorResource, OneDebtorResource
from data.groups_api import GroupResource, OneGroupResource
from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField, Label, FieldList, FormField
from wtforms.validators import DataRequired
from flask import request, render_template, redirect
from flask_restful import Api
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.__all_models import *

from data import db_session
db_session.global_init('data/db/db_main.db')
app = flask.Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

api.add_resource(DebtorResource, '/api/debtors')
api.add_resource(OneDebtorResource, '/api/debtors/<int:debtor_id>')
api.add_resource(DebtsResource, '/api/debts')
api.add_resource(OneDebtsResource, '/api/debts/<int:debt_id>')
api.add_resource(GroupResource, '/api/groups')
api.add_resource(OneGroupResource, '/api/groups/<int:group_id>')
api.add_resource(UserResource, '/api/users')
api.add_resource(OneUserResource, '/api/users/<int:user_id>')

app.config['SECRET_KEY'] = 'ultra_mega_secret_key'


def check_account():
    if not int(request.cookies.get('account_id', 0)):
        return False
    return True


class MyBooleanField(BooleanField):
    def __init__(self, value):
        self.value = value
        super(MyBooleanField, self).__init__()


def search_user(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    return user


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ConfirmForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class EditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class NewDebtForm(FlaskForm):
    name = StringField('Название долга', validators=[DataRequired()])
    debt_tag = StringField('Тэг долга', validators=[DataRequired()])
    sum_ = IntegerField('Сумма долга', validators=[DataRequired()])
    radio_field = RadioField('Выбор', choices=[(1, 'Группа'), (2, 'Пользователь')], validators=[DataRequired()])
    tag = StringField('Тэг / логин',  validators=[DataRequired()])
    submit = SubmitField('Создать')


class NewUserForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Создать')


class SelectFrom(FlaskForm):
    label_data = StringField()
    boolean = BooleanField('bool')


class NewGroupForm(FlaskForm):
    tag = StringField('Тэг', validators=[DataRequired()])
    select = FieldList(FormField(SelectFrom), min_entries=0)
    submit = SubmitField('Создать')


class SearchForm(FlaskForm):
    searched = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/leave_group/<int:group_id>')
@login_required
def leave_group(group_id):
    db_sess = db_session.create_session()
    member = db_sess.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    db_sess.delete(member)
    db_sess.commit()
    return redirect('/groups')


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/friends')
@login_required
def friends():
    db_sess = db_session.create_session()
    friends = db_sess.query(Friend).filter(Friend.user_id == current_user.id).all()
    users = list(map(lambda x: db_sess.query(User).get(x.friend_id), friends))
    return render_template('friends.html', users=users)


@app.route('/search', methods=['POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        searched = form.searched.data
        debtors_as_me = db_sess.query(Debtor).filter(Debtor.user_id == current_user.id).all()
        debts_ids = list(map(lambda x: x.debt_id, debtors_as_me))
        debts = db_sess.query(Debt).filter(Debt.tag.like(f'{searched}%'), Debt.id.in_(debts_ids)).all()

        debtors_debts = db_sess.query(Debt).filter(Debt.collector_id == current_user.id, Debt.tag.like(f'{searched}%')).all()
        debtors_debts_ids = db_sess.query(Debtor).filter(Debtor.debt_id.in_(list(map(lambda x: x.id, debtors_debts)))).all()
        debtors = list(map(lambda x: db_sess.query(User).get(x.user_id), debtors_debts_ids))
        debtors_debts = dict(list(map(lambda x: (x.id, x), debtors_debts)))
        group_members_as_me = db_sess.query(GroupMember).filter(GroupMember.user_id == current_user.id).all()
        groups = db_sess.query(Group).filter(Group.id.in_(list(map(lambda x: x.group_id, group_members_as_me))), Group.tag.like(f'{searched}%')).all()

        users = db_sess.query(User).filter(User.username.like(f'{searched}%'), User.id != current_user.id).all()

        friends = db_sess.query(Friend).filter(Friend.user_id == current_user.id).all()
        friends_users = db_sess.query(User).filter(User.id.in_(list(map(lambda x: x.friend_id, friends))), User.username.like(f'{searched}%')).all()

        return render_template('search.html', form=form, searched=searched,
                               debts=debts, debtors_debts=debtors_debts
                               , debtors=debtors, groups=groups, users=users,
                               debtors_debts_ids=debtors_debts_ids,
                               friends=friends_users)


@app.route('/users/<int:user_id>')
@login_required
def user_page(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    is_friend = bool(db_sess.query(Friend).filter(Friend.user_id == current_user.id, Friend.friend_id == user_id).first())
    return render_template('user.html', title=f'Пользователь {user.username}', user=user, is_friend=is_friend)


@app.route('/add_friend/<int:user_id>')
@login_required
def add_friend(user_id):
    db_sess = db_session.create_session()

    friend = Friend()
    friend.user_id = current_user.id
    friend.friend_id = user_id
    db_sess.add(friend)
    db_sess.commit()
    print(friend.to_dict())

    friend_2 = Friend()
    notification = Friend_Notification()
    notification.sender_id = current_user.id
    notification.receiver_id = user_id
    notification.time = datetime.datetime.now()
    db_sess.add(notification)
    friend_2.user_id = user_id
    friend_2.friend_id = current_user.id
    db_sess.add(friend_2)

    db_sess.commit()
    return redirect(f'/users/{user_id}')


@app.route('/delete_friend/<int:user_id>')
@login_required
def delete_friend(user_id):
    db_sess = db_session.create_session()
    friend = db_sess.query(Friend).filter(Friend.user_id == current_user.id, Friend.friend_id == user_id).first()
    friend_2 = db_sess.query(Friend).filter(Friend.user_id == user_id, Friend.friend_id == current_user.id).first()
    db_sess.delete(friend_2)
    db_sess.commit()
    db_sess.delete(friend)
    db_sess.commit()
    return redirect(f'/users/{user_id}')


@app.route('/new_group', methods=['GET', 'POST'])
def new_group(): # TODO
    db_sess = db_session.create_session()
    friends = db_sess.query(Friend).filter(Friend.user_id == current_user.id).all()
    users = list(map(lambda x: db_sess.query(User).get(x.friend_id), friends))
    a = []
    for user in users:
        a.append({'label_data': user.username})
    form = NewGroupForm(select=a)
    if not current_user.is_authenticated:
        return render_template('error.html', title='Ошибка', error='Вы не вошли в аккаунт')
    elif form.validate_on_submit():
        is_exist = db_sess.query(Group).filter(Group.tag == form.tag.data).first()
        if is_exist:
            return render_template('error.html', title='Ошибка', error='Группа с таким тэгом уже существует')
        group = Group()

        pinged_users = []
        for i in form.select:
            if i.boolean.data:
                pinged_users.append(i.label_data.data)
        if not pinged_users:
            return render_template('new_group.html', title='Новая группа', form=form, alert='Вы не выбрали участников')
        users = db_sess.query(User).filter(User.username.in_(pinged_users)).all()
        group.tag = form.tag.data
        group.admin_id = current_user.id
        db_sess.add(group)
        db_sess.commit()
        gm = GroupMember()
        gm.group_id = group.id
        gm.user_id = current_user.id
        db_sess.add(gm)
        db_sess.commit()
        for i in users:
            gm = GroupMember()
            gm.group_id = group.id
            gm.user_id = i.id
            notification = Group_Notification()
            notification.sender_id = current_user.id
            notification.receiver_id = i.id
            notification.group_id = group.id
            notification.time = datetime.datetime.now()
            db_sess.add(notification)
            db_sess.add(gm)
            db_sess.commit()
        return redirect('/groups')
    return render_template('new_group.html', title='Новая группа', form=form)


@app.route('/groups')
def groups_page():
    if not current_user.is_authenticated:
        return render_template('error.html', title='Ошибка', error='Вы не вошли в аккаунт')
    db_sess = db_session.create_session()
    groups = db_sess.query(Group).filter(Group.id.in_(list(map(lambda x: x.group_id, db_sess.query(GroupMember).
                                                               filter(GroupMember.user_id == current_user.id).all())))).all()
    members_ids = list(map(lambda x: db_sess.query(GroupMember).filter(GroupMember.group_id == x.id).all(), groups))
    members = [list(map(lambda x: db_sess.query(User).get(x.user_id), i)) for i in members_ids]
    return render_template('groups.html', title='Группы', groups=groups, members=members)


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        is_exist = db_sess.query(User).filter(User.username == form.username.data).first()
        if is_exist:
            return render_template('error.html', title='Ошибка', error='Пользователь с таким логином уже существует')
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.username = form.username.data
        user.password = form.password.data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('new_user.html', title='Новый аккаунт', form=form)


@app.route('/new_debt', methods=['GET', 'POST'])
def new_debt():
    form = NewDebtForm()
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return render_template('error.html', title='Вы не вошли в аккаунт', error='Вы не вошли в аккаунт!')
    elif form.validate_on_submit():
        name = form.name.data
        sum_ = form.sum_.data
        if sum_ <= 0:
            return render_template('error.html', title='Ошибка', error='Вы ввели неправильное значение суммы долга')
        if int(form.radio_field.data) == 2:
            user = search_user(form.tag.data)
            print('WRHBTEHB')
            if not user:
                return render_template('error.html', title='Ошибка', error='Пользователь не найден')
            debt = Debt()
            debt.collector_id = current_user.id
            debt.name = form.name.data
            debt.tag = form.debt_tag.data
            db_sess.add(debt)
            db_sess.commit()

            notification = Debt_Notification()
            notification.debt_id = debt.id
            notification.sender_id = current_user.id
            notification.receiver_id = user.id
            notification.time = datetime.datetime.now()
            debtor = Debtor()
            debtor.user_id = user.id
            debtor.debt_id = debt.id
            debtor.sum = form.sum_.data
            debtor.collector_id = current_user.id
            db_sess.add(debtor, notification)
            db_sess.commit()

        elif int(form.radio_field.data) == 1:
            group = db_sess.query(Group).filter(Group.tag == form.tag.data).first()
            members = db_sess.query(GroupMember).filter(GroupMember.group_id == group.id, GroupMember.user_id != current_user.id).all()
            user_ids = list(map(lambda x: x.user_id, members))
            debt = Debt()
            debt.collector_id = current_user.id
            debt.name = form.name.data
            debt.tag = form.debt_tag.data
            debt.group = group.id
            debt.time = datetime.datetime.now()
            db_sess.add(debt)
            db_sess.commit()
            one_user_sum = form.sum_.data // len(user_ids)
            for i in user_ids:
                debtor = Debtor()
                notification = Debt_Notification()
                notification.sender_id = current_user.id
                notification.receiver_id = i
                notification.debt_id = debt.id
                notification.time = datetime.datetime.now()
                debtor.user_id = i
                debtor.debt_id = debt.id
                debtor.sum = one_user_sum
                debtor.collector_id = current_user.id
                db_sess.add(debtor)
                db_sess.add(notification)
                db_sess.commit()

        return redirect('/debtors')

    return render_template('new_debt.html', form=form)


@app.route('/edit_data', methods=['GET', 'POST'])
def edit_data():
    form = EditForm()
    if not current_user.is_authenticated:
        return render_template('error.html', error='Вы не вошли в аккаунт')
    elif form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        user.id = current_user.id
        user.name = form.name.data
        user.surname = form.surname.data
        user.username = current_user.username
        user.password = form.password.data
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/account')
    form.name.data = current_user.name
    form.surname.data = current_user.surname
    form.password.data = current_user.password
    return render_template('edit.html', title='Редактировать профиль', form=form)


@app.route('/debts')
def debts():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        our_debtor = db_sess.query(Debtor).filter(Debtor.user_id == current_user.id).all()
        debts = db_sess.query(Debt).filter(Debt.id.in_(list(map(lambda x: x.debt_id, our_debtor)))).all()
        collectors = list(map(lambda y: db_sess.query(User).get(y), list(map(lambda x: x.collector_id, debts))))
        groups = list(map(lambda x: db_sess.query(Group).get(x.group), debts))
        return render_template('debts.html', title='Долги', debts=debts, collectors=collectors, groups=groups,
                               our_debtor=our_debtor)
    else:
        return render_template('error.html', error='Вы не вошли в аккаунт')


@app.route('/close_debt/<int:debt_id>')
def close_debt(debt_id):
    db_sess = db_session.create_session()
    debtor = db_sess.query(Debtor).filter(Debtor.debt_id == debt_id, Debtor.user_id == current_user.id).first()
    if not debtor:
        return render_template('error.html', title='Долг не найден!', error='Искомый долг не найден!')
    db_sess.delete(debtor)
    db_sess.commit()
    return redirect('/debts')


@app.route('/debtors')
def debtors_page():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        debtors = db_sess.query(Debtor).filter(Debtor.collector_id == current_user.id).all()
        debts = list(map(lambda x: db_sess.query(Debt).get(x.debt_id), debtors))
        users = list(map(lambda x: db_sess.query(User).get(x.user_id), debtors))
        groups = list(map(lambda x: db_sess.query(Group).get(x.group), debts))
        return render_template('debtors.html', debtors=debtors, debts=debts, groups=groups, users=users)
    else:
        return render_template('error.html', error='Вы не вошли в аккаунт')


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    form = ConfirmForm()
    if not current_user.is_authenticated:
        return render_template('error.html', error="Вы не вошли в аккаунт")
    elif form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.password.data != db_sess.query(User).get(current_user.id).password:
            return render_template('confirm.html', alert="Пароль неверный", form=form, title='Подтвердите действие')
        return redirect('/edit_data')
    return render_template('confirm.html', form=form, title='Подтведите действие', alert=None)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        # Получение долгов пользователя
        debts = db_sess.query(Debt).filter(Debt.id.in_(list(map(lambda x: x.debt_id, db_sess.query(Debtor).
                                                                filter(Debtor.user_id == current_user.id).all())))).all()
        # Получение должников пользователя
        debtors = db_sess.query(Debtor).filter(Debtor.collector_id == current_user.id).all()
        user_ids = list(map(lambda x: x.user_id, debtors))
        debtors_debts = list(map(lambda y: db_sess.query(Debt).get(y), list(map(lambda x: x.debt_id, debtors))))
        debtors_users = list(map(lambda x: db_sess.query(User).get(x), user_ids))
        groups = db_sess.query(Group).filter(Group.id.in_(list(map(lambda x: x.group_id, db_sess.query(GroupMember).
                                                     filter(GroupMember.user_id == current_user.id).all())))).all()
    else:
        debts, debtors, groups, debtors_debts, debtors_users = None, None, None, None, None
    return render_template('index.html',
                           debts=debts,
                           groups=groups,
                           debtors_users=debtors_users,
                           debtors=debtors,
                           debtors_debts=debtors_debts,
                           title='Главная')


@app.route('/account')
def account():
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id).to_dict()

    return render_template('account.html', user=user, title='Аккаунт')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = search_user(username)
        if not user:
            return render_template('login.html', title='Авторизация', form=form, alert='Пользователь не найден!')
        elif user.password != password:
            return render_template('login.html', title='Авторизация', form=form, alert='Неверный пароль!')
        login_user(user, remember=form.remember_me.data)
        return flask.redirect('/')

    if not current_user.is_authenticated:
        return render_template('login.html', title='Авторизация', form=form, alert=None)
    else:
        return redirect('/account')


@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()