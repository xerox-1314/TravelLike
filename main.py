from flask import Flask, render_template, request, url_for
from data import db_session
from data.users import User
from data.news import News
from data.lifehucks import Lifehacks


class Login_User:
    login_flag = False
    id = -1


def get_user_info(id):
    print(id)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    num_posts = len(db_sess.query(News).filter(News.user_id == id).all())
    num_lifehucks = len(db_sess.query(Lifehacks).filter(Lifehacks.user_id == id).all())
    return {'nickname': user.nickname, 'email': user.email, 'about': user.about,
            'male_female': user.male_female, 'image': url_for('static', filename=f'avatars/{user.image}'),
            'likes': user.likes, 'dislikes': user.dislikes, 'num_posts': num_posts, 'num_lifehucks': num_lifehucks}


def get_news_list():
    db_sess = db_session.create_session()
    news_list = []
    for new in db_sess.query(News).all():
        user = db_sess.query(User).filter(User.id == new.user_id).first()
        news_list.append({'id': new.id, 'title': new.title, 'content': new.content, 'image': new.images,
                          'user_nickname': user.nickname, 'user_image': url_for('static', filename=f'avatars/{user.image}'),
                          'created_date': new.created_date})
    return news_list


def get_news_id_info(news_id):
    db_sess = db_session.create_session()
    new = db_sess.query(News).filter(News.id == news_id).first()
    user = db_sess.query(User).filter(User.id == new.user_id).first()
    return {'id': new.id, 'title': new.title, 'content': new.content, 'image': url_for('static', filename=f'news_images/{new.images}'),
            'user_nickname': user.nickname, 'user_image': url_for('static', filename=f'avatars/{user.image}'),
            'dislikes': new.dislikes, 'likes': new.likes, 'created_date': new.created_date}


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
        with open(f'static/avatars/{user.nickname}.jpg', 'wb') as file:
            file.write(f.read())
            user.image = f'{user.nickname}.jpg'
        login_user.login_flag = True
        db_sess.add(user)
        db_sess.commit()
        login_user.id = db_sess.query(User).filter(User.nickname == user.nickname).first().id
        return render_template('welcome.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error='')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for user in db_sess.query(User).filter(User.email == request.form['email'], User.password == request.form['password']):
            login_user.login_flag = True
            login_user.id = db_sess.query(User).filter(User.nickname == user.nickname).first().id
            return render_template('welcome.html')
        return render_template('login.html', error='Неверная почта или пароль. Попробуйте еще раз!')


@app.route('/profile')
def profile():
    return render_template('profile.html', user_data=get_user_info(login_user.id))


@app.route('/news')
def news():
    return render_template('news.html', news_list=get_news_list())


@app.route('/full_news/<int:news_id>')
def full_news(news_id):
    print(1)
    return render_template('news_id.html', news_data=get_news_id_info(news_id))


@app.route('/create_news', methods=['POST', 'GET'])
def create():
    if request.method == 'GET':
        return render_template('create_news.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        news = News()
        news.title = request.form['title']
        news.content = request.form['content']
        news.user_id = login_user.id
        f = request.files['file']
        with open(f'static/news_images/{news.id}.jpg', 'wb') as file:
            file.write(f.read())
            news.images = f'{news.id}.jpg'
        db_sess.add(news)
        db_sess.commit()
        return render_template('news.html', news_list=get_news_list())


@app.route('/logout')
def logout():
    login_user.login_flag = False
    login_user.id = -1
    return render_template('welcome.html')


@app.context_processor
def user_info():
    if login_user.login_flag is True:
        result = get_user_info(login_user.id)
        result['login'] = True
        return dict(data=result)
    else:
        return dict(data={'login': False})


if __name__ == '__main__':
    db_session.global_init("db/main_db.db")
    app.run(debug=True, host='127.0.0.1', port=5000)