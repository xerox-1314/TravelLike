from flask import Flask, render_template, request, url_for
from data import db_session
from data.users import User
from data.news import News
from data.lifehucks import Lifehacks
import requests


class Login_User:
    login_flag = False
    id = -1


def get_user_info(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    num_posts = len(db_sess.query(News).filter(News.user_id == id).all())
    num_lifehucks = len(db_sess.query(Lifehacks).filter(Lifehacks.user_id == id).all())
    level = (((num_posts + num_lifehucks)**2 + user.likes + user.dislikes)/100)
    if level > 100:
        level = 100
    return {'nickname': user.nickname, 'email': user.email, 'about': user.about,
            'male_female': user.male_female, 'image': url_for('static', filename=f'avatars/{user.image}'),
            'likes': user.likes, 'dislikes': user.dislikes, 'num_posts': num_posts, 'num_lifehucks': num_lifehucks, 'level': level}


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
    return {'id': new.id, 'title': new.title, 'place': new.place, 'urls_place': get_url_place(new.place), 'content': new.content, 'image': url_for('static', filename=f'news_images/{new.images}'),
            'user_nickname': user.nickname, 'user_image': url_for('static', filename=f'avatars/{user.image}'),
            'dislikes': new.dislikes, 'likes': new.likes, 'created_date': new.created_date}


def set_like(news_id, user_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.likes += 1
    news.likes += 1
    likes_news = user.likes_news.split(';')
    likes_news.append(str(news_id))
    user.likes_news = ";".join(likes_news)
    db_sess.commit()


def set_dislike(news_id, user_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.dislikes += 1
    news.dislikes += 1
    dislikes_news = user.dislike_news.split(';')
    dislikes_news.append(str(news_id))
    user.dislike_news = ";".join(dislikes_news)
    db_sess.commit()


def delete_like(news_id, user_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.likes -= 1
    news.likes -= 1
    likes_news = user.likes_news.split(';')
    likes_news.remove(str(news_id))
    user.likes_news = ";".join(likes_news)
    db_sess.commit()


def delete_dislike(news_id, user_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.dislikes -= 1
    news.dislikes -= 1
    dislike_news = user.dislike_news.split(';')
    dislike_news.remove(str(news_id))
    user.dislike_news = ";".join(dislike_news)
    db_sess.commit()


def get_user_likes_dislikes(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return [user.likes_news.split(';'), user.dislike_news.split(';')]


def get_url_place(place):
    response = requests.get(f'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode="{place}"&format=json')
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
    toponym_coodrinates = toponym["Point"]["pos"]
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={toponym_coodrinates.split()[0]},{toponym_coodrinates.split()[1]}&spn=0.1,0.1&l=map"
    sat_request = f"http://static-maps.yandex.ru/1.x/?ll={toponym_coodrinates.split()[0]},{toponym_coodrinates.split()[1]}&spn=0.1,0.1&l=sat"
    return [map_request, sat_request]


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
        user.likes_news = 0
        user.dislike_news = 0
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


@app.route('/change_profile', methods=['POST', 'GET'])
def change_profile():
    if request.method == 'GET':
        return render_template('change_profile.html', error='', user_info=get_user_info(login_user.id))
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == login_user.id).first()
        for email in db_sess.query(User).filter(User.email == request.form['email'], User.id != user.id):
            return render_template('change_profile.html', error='Пользователь с таким email уже зарегистрирован', user_info=get_user_info(login_user.id))
        for nick in db_sess.query(User).filter(User.nickname == request.form['nickname'], User.id != user.id):
            return render_template('change_profile.html', error='Такой ник на сайте уже зарегистрирован', user_info=get_user_info(login_user.id))
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
        db_sess.commit()
        return render_template('profile.html', user_data=get_user_info(login_user.id))


@app.route('/news')
def news():
    return render_template('news.html', news_list=get_news_list())


@app.route('/full_news/<int:news_id>')
def full_news(news_id):
    if login_user.login_flag is False:
        return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=0)
    else:
        if str(news_id) in get_user_likes_dislikes(login_user.id)[0]:
            return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=1, dislike_state=0)
        elif str(news_id) in get_user_likes_dislikes(login_user.id)[1]:
            return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=1)
        else:
            return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=0)


@app.route('/set_like/<int:news_id>')
def set_like_ob(news_id):
    set_like(news_id, login_user.id)
    return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=1, dislike_state=0)


@app.route('/set_dislike/<int:news_id>')
def set_dislike_ob(news_id):
    set_dislike(news_id, login_user.id)
    return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=1)


@app.route('/delete_like/<int:news_id>')
def delete_like_ob(news_id):
    delete_like(news_id, login_user.id)
    return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=0)


@app.route('/delete_dislike/<int:news_id>')
def delete_dislike_ob(news_id):
    delete_dislike(news_id, login_user.id)
    return render_template('news_id.html', news_data=get_news_id_info(news_id), like_state=0, dislike_state=0)


@app.route('/create_news', methods=['POST', 'GET'])
def create():
    if request.method == 'GET':
        return render_template('create_news.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        news = News()
        news.title = request.form['title']
        news.place = request.form['place']
        news.content = request.form['content']
        news.user_id = login_user.id
        db_sess.add(news)
        db_sess.commit()
        f = request.files['file']
        with open(f'static/news_images/{news.id}.jpg', 'wb') as file:
            file.write(f.read())
            news.images = f'{news.id}.jpg'
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