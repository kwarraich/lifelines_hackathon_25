from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased length for hashed passwords
    shelter_name = db.Column(db.String(100), nullable=False)

    # Relationship with resources (one-to-many)
    resources = db.relationship('Resource', backref='user', lazy=True)

class Resource(db.Model):
    __tablename__ = 'resources'
    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

# Function to initialize the database
def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
