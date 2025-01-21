from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelters.id'), nullable=True)  # New column

class Shelter(db.Model):
    __tablename__ = 'shelters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', backref='shelter', lazy=True)
    resources = db.relationship('Resource', backref='shelter', lazy=True)

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelters.id'), nullable=False)
