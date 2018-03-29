from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return datetime.utcfromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

follows = db.Table('follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('target_id', db.Integer, db.ForeignKey('group.group_id'))
)

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)
	enter = db.Column(db.Integer)
	
	# Groups the user hosts
	hosts = db.relationship('Room', backref='host')
	# Groups the user follows
	follows = db.relationship('Group', secondary='follows', backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self, username, email, pw_hash):
		self.username = username
		self.email = email
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<User {}>'.format(self.username)


class Group(db.Model):
	group_id = db.Column(db.Integer, primary_key=True)
	host_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	group_name = db.Column(db.String(64), nullable=False)
	description = db.Column(db.Text, nullable=False)
	date = db.Column(db.Integer, nullable=False)
	
	lists = db.relationship('List', backref='group', cascade="all, delete-orphan")
	
	def __init__(self, host_id, name, description, date):
			self.host_id = host_id
			self.group_name = name
			self.description = description
			self.date = date

	def __repr__(self):
			return '<Group {}>'.format(self.name)
			
class List(db.Model):
	list_id = db.Column(db.Integer, primary_key=True)
	group_id = db.Column(db.Integer, db.ForeignKey('group.group_id'), nullable=False)
	list_name = db.Column(db.Text, nullable=False)
	date = db.Column(db.Integer, nullable=False)
	
	tasks = db.relationship('Task', backref='container', cascade="all, delete-orphan")
	
	def __init__(self, group_id, name, date):
			self.group_id = group_id
			self.list_name = name
			self.date = date

	def __repr__(self):
			return '<List {}>'.format(self.name)


class Task(db.Model):
	task_id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(24), nullable=False)
	list_id = db.Column(db.Integer, db.ForeignKey('list.list_id'), nullable=False)
	text = db.Column(db.Text, nullable=False)
	state = db.Column(db.String(24), nullable=False)
	pub_date = db.Column(db.Integer, nullable=False)

	def __init__(self, author, list_id,text, pub_date):
			self.author = author
			self.text = text
			self.pub_date = pub_date
			self.list_id = list_id	
			self.state = "incomplete"

	def __repr__(self):
			return '<Task {}'.format(self.message_id)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'author'				: self.author,
			'state'				: self.state,
			'text'				: self.text,
			'pub_date'			: dump_datetime(self.pub_date)
		}