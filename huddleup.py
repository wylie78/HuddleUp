# HuddleUp Application Flask Server
# Arthur: Zihan Yu, James Huang, Guanjia Wang

import calendar
import time
import os
import json
from hashlib import md5
from datetime import datetime, date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import and_, or_

from models import db, User, Group, List, Task

# create our little application :)
app = Flask(__name__)

# configuration
# the toolbar is only enabled in debug mode:
#app.debug = False
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'huddleup.db')

app.config.from_object(__name__)
app.config.from_envvar('HUDDLEUP_SETTINGS', silent=True)
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

def get_group_id(group_name):
	"""Convenience method to look up the id for a group name."""
	rv = Group.query.filter_by(group_name=group_name).first()
	return rv.group_id if rv else None
	
def get_list_id(list_name):
	"""Convenience method to look up the id for a list name."""
	rv = List.query.filter_by(list_name=list_name).first()
	return rv.list_id if rv else None
	
def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	
@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()
						
@app.route('/groups')
def groups_all():
	"""Display all groups"""
	if not g.user:
		return redirect(url_for('login'))
	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	# Check if user is currently in a group, if so, redirect to that group
	if u.enter:
		pregroup = Group.query.filter_by(group_id=u.enter).first()
		if pregroup:
			flash('Warning: You are currently in group "%s". Please leave first.' % pregroup.group_name)
			return redirect(url_for('in_group',group_name=pregroup.group_name))
		else:
			u.enter = None
			db.session.commit()
	
	group_ids = []	
	for gp in u.follows:
		group_ids.append(gp.group_id)
		
	groups = Group.query.filter(Group.group_id.in_(group_ids)).order_by(Group.date).all()
	if groups:
		session['last_group'] = groups[-1].date
	else:
		session['last_group'] = 0
	return render_template('index.html', groups=groups, username=u.username)


@app.route('/group/<group_name>')
def in_group(group_name):
	"""Displays the lists in the group.
	"""
	if not g.user:
		return redirect(url_for('login'))	
	visiting_id = get_group_id(group_name)
	u = User.query.filter_by(user_id=session['user_id']).first()
	if visiting_id is None:
		if u.enter is not None:
			u.enter = None
			db.session.commit()
		else:
			flash('Error: Group "%s" does not exists anymore.' % group_name)
		return redirect(url_for('groups_all'))
		
	gp = Group.query.filter_by(group_name=group_name).first()
	
	"""Check if the current user is in another group."""
	if u.enter is None: 
		u.enter = gp.group_id
		db.session.commit()
		flash('Welcome to group "%s".' % group_name)
	elif u.enter != gp.group_id:
		pregroup = Group.query.filter_by(group_id=u.enter).first()
		flash('Error: Cannot join "%s". You are currently in another group.' % group_name)
		return redirect(url_for('in_group',group_name=pregroup.group_name))
	
	list_ids = []	
	for l in gp.lists:
		list_ids.append(l.list_id)
		
	lists = List.query.filter(List.list_id.in_(list_ids)).order_by(List.date).all()
	if lists:
		session['last_list'] = lists[-1].date
	else:
		session['last_list'] = 0
	
	# Get list items	
	list_ids = []
	for l in gp.lists:
		list_ids.append(l.list_id)
		
	lists = List.query.filter(List.list_id.in_(list_ids)).all()
	
	# Get task items
	tasks_all = []
	if lists:
		for l in lists:
			task_ids = []
			for t in l.tasks:
				task_ids.append(t.task_id)
			tasks = Task.query.filter(Task.task_id.in_(task_ids)).all()
			tasks_all.append(tasks)
		
	# Get members	
	member_ids = []
	for m in gp.followers:
		member_ids.append(m.user_id)
		
	members = User.query.filter(User.user_id.in_(member_ids)).all()
	
	return render_template('index.html', lists=lists, tasks=tasks_all, members=members, group=gp )


@app.route('/leave')
def leave_group():
	"""Leave the current group."""
	if not g.user:
		return redirect(url_for('login'))
	u = User.query.filter_by(user_id=session['user_id']).first()
	if u.enter:
		gp = Group.query.filter_by(group_id=u.enter).first()
		u.enter = None
		db.session.commit()
	else:
		flash('Error: You are not in any group.')
	
	return redirect(url_for('groups_all'))
	

@app.route('/my_groups')
def user_groups():
	"""Display a user's created groups."""
	if not g.user:
		return redirect(url_for('login'))
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	if u.enter:
		return redirect(url_for('groups_all'))
			
	gs = Group.query.filter_by(host_id=u.user_id).order_by(Group.date.desc()).all()
	return render_template('index.html', groups=gs)

	
@app.route('/delete/<group_name>')
def delete_group(group_name):
	"""Removes the group."""
	if not g.user:
		abort(401)
	hosted_id = get_group_id(group_name)
	if hosted_id is None:
		abort(404)
	
	hosted = Group.query.filter_by(group_id=hosted_id).first()
	if hosted.host_id != session['user_id']:
		flash('Error: You cannot delete "%s".' % group_name)
		return redirect(url_for('groups_all'))
	
	us = User.query.filter_by(enter=hosted_id).all()
	for u in us:
		u.enter = None
	
	db.session.delete(hosted)
	db.session.commit()
	
	print('Group removed!')
	
	flash('The group "%s" has been deleted' % group_name)
	return redirect(url_for('user_groups'))


@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
	"""Creates a new group for the user."""
	if not g.user:
		return redirect(url_for('login'))
		
	error = None
	if request.method == 'POST':
		if request.form['group_name']:	
			db.session.add(Group(session['user_id'], request.form['group_name'], request.form['description'], int(time.time())))			
			db.session.commit()
			un = User.query.filter_by(user_id=session['user_id']).first()
			gp = Group.query.filter_by(group_name=request.form['group_name']).first()		
			un.follows.append(gp)
			db.session.commit()
			flash('Group created!')
			return redirect(url_for('user_groups'))
	
	return render_template('index.html',error = error)
	
@app.route("/new_list", methods=['GET', 'POST'])
def add_list():
	"""Add list to the group"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	print('Checking status!')
	
	if u.enter is None:
		flash('You are not in the current group anymore!')
		return json.dumps({'url':url}),301
	if not Group.query.filter_by(group_id=u.enter).first():
		flash('The group is deleted, Please enter another group!')
		return json.dumps({'url':url}),301
		
	print('Adding list!')	
	
	gp = Group.query.filter_by(group_id=u.enter).first()
	
	if request.form['title']:
		db.session.add(List(u.enter, request.form['title'], int(time.time())))
		db.session.commit()

	return redirect(url_for('in_group',group_name=gp.group_name))
	
@app.route("/new_task/<list_name>", methods=['GET', 'POST'])
def add_task(list_name):
	"""Add task to the list"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	gp = Group.query.filter_by(group_id=u.enter).first()
	list_id = get_list_id(list_name)
	if list_id is None:
		flash('Error: list not found.')
		return redirect(url_for('in_group',group_name=gp.group_name))
		
	print('Checking status!')
	
	if u.enter is None:
		flash('You are not in the current group anymore!')
		return json.dumps({'url':url}),301
	if not Group.query.filter_by(group_id=u.enter).first():
		flash('The group is deleted, Please enter another group!')
		return json.dumps({'url':url}),301
		
	print('Adding task!')	
	
	error = None
	if request.method == 'POST':		
		if request.form['task_name']:
			db.session.add(Task(u.username, list_id, request.form['task_name'], request.form['description'],int(time.time())))
			db.session.commit()
		
	return redirect(url_for('in_group',group_name=gp.group_name))

	
@app.route("/changeTask/<task_id>", methods=['GET', 'POST'])
def change_task(task_id):
	"""Change task status"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	print('Checking status!')
	
	if u.enter is None:
		flash('You are not in the current group anymore!')
		return json.dumps({'url':url}),301
	if not Group.query.filter_by(group_id=u.enter).first():
		flash('The group is deleted, Please enter another group!')
		return json.dumps({'url':url}),301
		
	print('Modifying task status!')	
	
	gp = Group.query.filter_by(group_id=u.enter).first()	
	
	if request.form['state']:
		t = Task.query.filter_by(task_id=task_id).first()
		t.state = request.form['state']
		db.session.commit()
		print('State changed to:' + request.form['state'])	

	return redirect(url_for('in_group',group_name=gp.group_name))
	
@app.route("/deleteTask/<task_id>", methods=['GET', 'POST'])
def delete_task(task_id):
	"""delete the task"""
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	print('Checking status!')
	
	if u.enter is None:
		flash('You are not in the current group anymore!')
		return json.dumps({'url':url}),301
	if not Group.query.filter_by(group_id=u.enter).first():
		flash('The group is deleted, Please enter another group!')
		return json.dumps({'url':url}),301
		
	print('Deleting the task!')	
	
	gp = Group.query.filter_by(group_id=u.enter).first()	
	t = Task.query.filter_by(task_id=task_id).first()
	db.session.delete(t)
	db.session.commit()

	return redirect(url_for('in_group',group_name=gp.group_name))

@app.route('/addMember', methods=['GET', 'POST'])
def add_member():
	"""Display search page"""
	if not g.user:
		return redirect(url_for('login'))
	
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	# Check if user is the host of current group, if not, redirect to that group
	if u.enter:
		pregroup = Group.query.filter_by(group_id=u.enter).first()
		if pregroup:
			if pregroup.host_id != u.user_id:
				flash('Warning: You do not have the authority for this page')
				return redirect(url_for('in_group',group_name=pregroup.group_name))
		else:
			flash('Warning: Group does not found')
			u.enter = None
			return redirect(url_for('groups_all'))
	else:
		flash('Warning: You are not in any group')
		return redirect(url_for('groups_all'))
			
	if request.form['user']:
		un = User.query.filter(or_(User.username==request.form['user'], User.email==request.form['user'])).first()
		if un:
			gp = Group.query.filter_by(group_id=u.enter).first()
			un.follows.append(gp)
			db.session.commit()
			flash('User Added Success!')
		else:
			flash('Failed. Could not find the user with credential')
	gp = Group.query.filter_by(group_id=u.enter).first()
		
	return redirect(url_for('in_group',group_name=gp.group_name))

	
@app.route('/removeMember/<username>')
def remove_member(username):
	"""remove a member from the group"""
	if not g.user:
		return redirect(url_for('login'))
	followee_id = get_user_id(username)
	if followee_id is None:
		abort(404)
	u = User.query.filter_by(user_id=session['user_id']).first()
	
	# Check if user is the host of current group, if not, redirect to that group
	if u.enter:
		pregroup = Group.query.filter_by(group_id=u.enter).first()
		if pregroup:
			if pregroup.host_id != u.user_id:
				flash('Warning: You do not have the authority for this page')
				return redirect(url_for('in_group',group_name=pregroup.group_name))
			if pregroup.host_id == followee_id:
				flash('Warning: You cannot remove host of the group')
				return redirect(url_for('in_group',group_name=pregroup.group_name))
		else:
			flash('Warning: Group does not found')
			u.enter = None
			return redirect(url_for('groups_all'))
	else:
		flash('Warning: You are not in any group')
		return redirect(url_for('groups_all'))
			
	follower = User.query.filter_by(user_id=followee_id).first()
	gp = Group.query.filter_by(group_id=u.enter).first()	
	gp.followers.remove(follower)
	db.session.commit()
		
	return redirect(url_for('in_group',group_name=gp.group_name))	

@app.route('/', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('groups_all'))
			
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(email=request.form['email']).first()
		if user is None:
			error = 'Invalid email'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('groups_all'))
			
	return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the user."""
	
	if g.user:
		flash('Please log out first')
		return redirect(url_for('groups_all'))

	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['email']:
			error = 'You have to enter an email'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], request.form['email'], generate_password_hash(request.form['password'])))
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
		gp = Group.query.filter_by(group_id=user.enter).first()
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

