# Zihan Yu
# ziy7@pitt.edu
# assignment 3
# Reference to minitwit example

import calendar
import time
import os
import json
from hashlib import md5
from datetime import datetime, date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import and_


from models import db, User, Room, Message

# create our little application :)
app = Flask(__name__)

# configuration
# the toolbar is only enabled in debug mode:
#app.debug = False
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')

app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent=True)
#app.config['SECRET_KEY'] = SECRET_KEY


#toolbar = DebugToolbarExtension(app)

db.init_app(app)


@app.cli.command('initdb')
def initdb_command():
	"""Initialize the database tables."""
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

	
def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

	
def get_room_id(room_name):
	"""Convenience method to look up the id for a room name."""
	rv = Room.query.filter_by(room_name=room_name).first()
	return rv.room_id if rv else None
	
def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	
@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

@app.route('/list')
def rooms_all():
	"""Display all rooms"""
	if not g.user:
		return redirect(url_for('login'))
	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	if u.enter:
		preroom = Room.query.filter_by(room_id=u.enter).first()
		if preroom:
			flash('Warning: You are currently in room "%s". Please leave first.' % preroom.room_name)
			return redirect(url_for('in_room',room_name=preroom.room_name))
		else:
			u.enter = None
			db.session.commit()
			
	return render_template('chats.html', rooms=Room.query.order_by(Room.date.desc()).all())


@app.route('/room/<room_name>')
def in_room(room_name):
	"""Displays the messages in the room.
	"""
	if not g.user:
		return redirect(url_for('login'))	
	visiting_id = get_room_id(room_name)
	u = User.query.filter_by(user_id=session['user_id']).first()
	if visiting_id is None:
		if u.enter is not None:
			u.enter = None
			db.session.commit()
		else:
			flash('Error: Room "%s" does not exists anymore.' % room_name)
		return redirect(url_for('rooms_all'))
		
	r = Room.query.filter_by(room_name=room_name).first()
	
	"""Check if the current user is in another room."""
	if u.enter is None: 
		u.enter = r.room_id
		db.session.commit()
		flash('Welcome to room "%s".' % room_name)
	elif u.enter != r.room_id:
		preroom = Room.query.filter_by(room_id=u.enter).first()
		flash('Error: Cannot join "%s". You are currently in another room.' % room_name)
		return redirect(url_for('in_room',room_name=preroom.room_name))
	
	message_ids = []
	
	for m in r.messages:
		message_ids.append(m.message_id)
		
	messages = Message.query.filter(Message.message_id.in_(message_ids)).order_by(Message.pub_date).all()
	if messages:
		session['last_msg'] = messages[-1].pub_date
	else:
		session['last_msg'] = 0
	return render_template('chats.html', messages=messages, room_name=room_name)


@app.route('/leave')
def leave_room():
	"""Leave the current room."""
	if not g.user:
		return redirect(url_for('login'))
	u = User.query.filter_by(user_id=session['user_id']).first()
	if u.enter:
		r = Room.query.filter_by(room_id=u.enter).first()
		u.enter = None
		db.session.commit()
	else:
		flash('Error: You are not in any room.')
	
	return redirect(url_for('rooms_all'))
	

@app.route('/my_rooms')
def user_rooms():
	"""Display a user's created rooms."""
	if not g.user:
		return redirect(url_for('login'))
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	if u.enter:
		return redirect(url_for('rooms_all'))
			
	rs = Room.query.filter_by(host_id=u.user_id).order_by(Room.date.desc()).all()
	return render_template('chats.html', rooms=rs)

	
@app.route('/delete/<room_name>')
def delete_room(room_name):
	"""Removes the room."""
	if not g.user:
		abort(401)
	hosted_id = get_room_id(room_name)
	if hosted_id is None:
		abort(404)
	
	hosted = Room.query.filter_by(room_id=hosted_id).first()
	if hosted.host_id != session['user_id']:
		flash('Error: You cannot delete "%s".' % room_name)
		return redirect(url_for('rooms_all'))
	
	us = User.query.filter_by(enter=hosted_id).all()
	for u in us:
		u.enter = None
	
	db.session.delete(hosted)
	db.session.commit()
	
	print('Room removed!')
	
	flash('The room "%s" has been deleted' % room_name)
	return redirect(url_for('user_rooms'))


@app.route('/add_room', methods=['POST'])
def add_room():
	"""Creates a new room for the user."""
	if not g.user:
		abort(401)
	if request.form['room_name']:	
		db.session.add(Room(session['user_id'], request.form['room_name'], int(time.time()))) 
		db.session.commit()
		flash('Room created!')
	return redirect(url_for('user_rooms'))

	
@app.route("/new_msg", methods=["POST"])
def add_msg():
	"""Add message to the room"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	print('Checking status!')
	
	if u.enter is None:
		flash('You are not in the current room anymore!')
		return json.dumps({'url':url}),301
	if not Room.query.filter_by(room_id=u.enter).first():
		flash('The room is deleted, Please enter another room!')
		return json.dumps({'url':url}),301
		
	print('Adding message!')	
	
	if request.form['text']:
		db.session.add(Message(u.username, u.enter, request.form['text'], int(time.time())))
		db.session.commit()

	return "OK!"
	
	
@app.route("/get_messages")
def get_msg():
	"""Get messages to the room"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	if u.enter is None:
		flash('You are not in the room anymore!')
		url = url_for('rooms_all')
		return json.dumps({'url':url}),301
	if not Room.query.filter_by(room_id=u.enter).first():
		flash('The room is deleted, Please enter another room!')
		url = url_for('rooms_all')
		return json.dumps({'url':url}),301
	
	messages = Message.query.filter(Message.room_id == u.enter, Message.pub_date > session['last_msg']).order_by(Message.pub_date).all()
	if messages:
		session['last_msg'] = messages[-1].pub_date

	return json.dumps([m.serialize for m in messages])

	
@app.route('/', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('rooms_all'))
			
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('rooms_all'))
			
	return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the user."""
	
	if g.user:
		flash('Please log out first')
		return redirect(url_for('rooms_all'))

	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
			flash('You were successfully registered and can login now')
			db.session.commit()
			if 'user_id' in session:
				session.pop('user_id', None)
			return redirect(url_for('login'))

	return render_template('register.html', error=error)


@app.route('/logout')
def logout():
	"""Logs the user out."""
	if not g.user:
		return redirect(url_for('login'))
		
	user = User.query.filter_by(user_id=session['user_id']).first()
	if user.enter is not None:
		r = Room.query.filter_by(room_id=user.enter).first()
		user.enter = None
	db.session.commit()
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('login'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime

print("__name__:")
print(__name__)

if __name__ == "__main__":
	app.run(debug = True)
	app.run(threaded=True)

