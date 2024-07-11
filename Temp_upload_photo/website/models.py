from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_filename = db.Column(db.String(255))
    messages = db.relationship('Message')

    def __init__(self, email, first_name, last_name, password, image_filename=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.image_filename = image_filename
