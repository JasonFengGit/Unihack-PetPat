from flask import Flask, redirect, request, flash, session, render_template
from flask.helpers import url_for
from password_manager import PasswordManager
from redis_client import RedisClient
from impression_container import ImpressionContainer
from user_list import UserList
from datetime import timedelta
from recall_manager import RecallManager
from recent_likes import RecentLikes
from random import randint
import random

app = Flask(__name__, template_folder='./')
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
root_url = 'http://106.54.178.189'
_redis_client = RedisClient()
_password_manager = PasswordManager(_redis_client)
_impression_countainer = ImpressionContainer(_redis_client)
_user_list = UserList(_redis_client)
_recall_manager = RecallManager(_redis_client, _impression_countainer)
_recent_likes = RecentLikes(_redis_client)

env = app.jinja_env

@app.template_global('get_icon')
def get_icon():
    rand = randint(1, 25)
    if rand < 10:
        rand = "0"+str(rand)
    else:
        rand = str(rand)
    re = "https://github.com/JasonFengGit/Unihack-Pettinder/raw/master/icons/icons{}.jfif".format(rand)

    return re

@app.template_global('get_feeds')
def get_feeds_initial(count):
    #session['user'] = 'test4'
    if count == -1:
        re = ['1', '20210808024207', '202108080242071', '2021080802420710', '202108080242072']
        random.shuffle(re)
        re = ['https://raw.githubusercontent.com/JasonFengGit/Unihack-Pettinder/master/candidates_dedup/'+name+'.jpg' for name in re]
        return re
    re = _recall_manager.provide_feed(session['user'], count)
    for item in re:
        _impression_countainer.set_impr(session['user'], item)
    re = ['https://raw.githubusercontent.com/JasonFengGit/Unihack-Pettinder/master/candidates_dedup/'+name+'.jpg' for name in re]
    print(re)
    return re

@app.route('/get_feeds')
def get_feeds():
    session['user'] = session['user']
    if 'user' not in session:
        return []
    re = _recall_manager.provide_feed(session['user'], 1)
    for item in re:
        _impression_countainer.set_impr(session['user'], item)
    re = ['https://raw.githubusercontent.com/JasonFengGit/Unihack-Pettinder/master/candidates_dedup/'+name+'.jpg' for name in re]
    return re[0]

@app.route('/')
def home():
    #return redirect(root_url+"/login")
    if 'user' in session and session['user']:
        return redirect(root_url+"/{}/feed".format(session['user']))
    else:
        return redirect(root_url+"/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user', '')
        pwd = request.form.get('pwd', '')
        r_user = request.form.get('r_user', '')
        r_pwd = request.form.get('r_pwd', '')

        if user:
            pwd_checked = user and pwd and _password_manager.check(user, pwd)
            if pwd_checked:
                session['user'] = user
                return redirect('{}/{}/feed'.format(root_url, user))
            else:
                flash('username and password not matched')
                return redirect(root_url+"/login")
        elif r_user:
            if r_user not in _user_list.get_user_list():
                print(_user_list.get_user_list())
                _user_list.add_user(r_user)
                _password_manager.set(r_user, r_pwd)
                session['user'] = r_user
                return redirect('{}/{}/feed'.format(root_url, r_user))
            else:
                flash('username has been used')
                return redirect(root_url+"/login")
        return redirect(root_url+"/login")
    return render_template("login.html")

@app.route('/<uid>/feed')
def feed(uid):
    if 'user' in session and session['user'] == uid:
        print("imors:", _impression_countainer.get_impr(uid))
        return render_template("feed.html", username=session['user'])
    else:
        return redirect(root_url+"/login")

@app.route('/set_inter/<item>')
def set_inter(item):
    if 'user' in session and session['user']:
        _recent_likes.add_like(session['user'], item)
        print("r_likes:",_recent_likes.get_likes(session['user']))
        return '1'
    return '0'
