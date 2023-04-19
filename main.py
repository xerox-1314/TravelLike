from flask import Flask, render_template, request
from data import db_session
from data.users import User
from data.news import News


class Login_User:
    login_flag = False
    nickname = ''
    email = ''
    about = ''
    male_female = ''
    image = ''


app = Flask(__name__)
login_user = Login_User()


@app.route('/')
@app.route('/home')
def welcome():
    return render_template('welcome.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error='')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for email in db_sess.query(User).filter(User.email == request.form['email']):
            return render_template('register.html', error='Пользователь с таким email уже зарегистрирован')
        for nick in db_sess.query(User).filter(User.nickname == request.form['nickname']):
            return render_template('register.html', error='Такой ник на сайте уже зарегистрирован')
        user = User()
        user.nickname = request.form['nickname']
        user.email = request.form['email']
        user.password = request.form['password']
        user.about = request.form['about']
        try:
            a = request.form['male']
            user.male_female = 'male'
        except KeyError:
            user.male_female = 'female'
        f = request.files['file']
        with open(f'avatars/{user.nickname}.jpg', 'wb') as file:
            file.write(f.read())
            user.image = f'{user.nickname}.jpg'
        login_user.login_flag = True
        login_user.nickname = user.nickname
        login_user.email = user.email
        login_user.about = user.about
        login_user.male_female = user.male_female
        login_user.image = user.image
        db_sess.add(user)
        db_sess.commit()
        return render_template('welcome.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error='')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for user in db_sess.query(User).filter(User.email == request.form['email'], User.password == request.form['password']):
            login_user.login_flag = True
            login_user.nickname = user.nickname
            login_user.email = user.email
            login_user.about = user.about
            login_user.male_female = user.male_female
            login_user.image = user.image
            return render_template('welcome.html')
        return render_template('login.html', error='Неверная почта или пароль. Попробуйте еще раз!')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/news')
def news():
    news_list = []
    db_sess = db_session.create_session()
    for new in db_sess.query(News).all():
        user = db_sess.query(User).filter(User.id == new.user_id).first()
        news_list.append({'id': new.id, 'title': new.title, 'content': new.content, 'images': new.images,
                          'user_nickname': user.nickname, 'user_image': user.image})
    return render_template('news.html', news_list=news_list)


@app.context_processor
def user_info():
    if login_user.login_flag is True:
        result = {'login': True, 'nickname': login_user.nickname, 'email': login_user.email, 'about': login_user.about,
                'male_female': login_user.male_female, 'image': login_user.image}
        return dict(data=result)
    else:
        return dict(data={'login': False})


if __name__ == '__main__':
    db_session.global_init("db/main_db.db")
    app.run(debug=True, host='127.0.0.1', port=5000)