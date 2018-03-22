import os, sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from model import *

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'huddleup.db')

app.config.update(dict(
	DEBUG = True,
	SECRET_KEY='development key',
	USERNAME='owner',
	PASSWORD='pass'
))

app.config.from_object(__name__)
app.config.from_envvar('HUDDLEUP_SETTINGS', silent=True)

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	db.create_all()
	print('Initialized the database.')

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('index.html')
    
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        #TODO: Connect to DB
        print(request.form['email'])
        print(request.form['password'])
        return redirect(url_for('home'))
        
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        #TODO: Connect to DB
        print(request.form['firstname'])
        print(request.form['lastname'])
        print(request.form['email'])
        print(request.form['password'])
        print(request.form['repeatpassword'])
        return redirect(url_for('home'))
    
@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'GET':
        return render_template('register.html')