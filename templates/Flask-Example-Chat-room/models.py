from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return datetime.utcfromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')


class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)
	enter = db.Column(db.Integer)
	
	hosts = db.relationship('Room', backref='host')
	
	def __init__(self, username, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<User {}>'.format(self.username)


class Room(db.Model):
	room_id = db.Column(db.Integer, primary_key=True)
	host_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	room_name = db.Column(db.Text, nullable=False)
	date = db.Column(db.Integer, nullable=False)
	
	messages = db.relationship('Message', backref='container', cascade="all, delete-orphan")
	
	def __init__(self, host_id, name, date):
			self.host_id = host_id
			self.room_name = name
			self.date = date

	def __repr__(self):
			return '<Room {}>'.format(self.name)


class Message(db.Model):
	message_id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(24), nullable=False)
	room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
	text = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.Integer, nullable=False)

	def __init__(self, author, room_id,text, pub_date):
			self.author = author
			self.text = text
			self.pub_date = pub_date
			self.room_id = room_id			

	def __repr__(self):
			return '<Message {}'.format(self.message_id)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'author'				: self.author,
			'text'				: self.text,
			'pub_date'			: dump_datetime(self.pub_date)
		}