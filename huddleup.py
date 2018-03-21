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
def home():
	return render_template('index.html')
    
@app.route('/signin')
def login():
    return render_template('signin.html')