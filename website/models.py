from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash

friends = db.Table('friends',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                   db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
                   )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_filename = db.Column(db.String(255))

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver',
                                        lazy='dynamic')

    friends = db.relationship('User',
                              secondary=friends,
                              primaryjoin=(friends.c.user_id == id),
                              secondaryjoin=(friends.c.friend_id == id),
                              backref=db.backref('friend_of', lazy='dynamic'),
                              lazy='dynamic')

    def add_friend(self, user):
        if not self.is_friend(user):
            self.friends.append(user)

    def remove_friend(self, user):
        if self.is_friend(user):
            self.friends.remove(user)
            user.friends.remove(self)

    def is_friend(self, user):
        return self.friends.filter(friends.c.friend_id == user.id).count() > 0

    friend_requests_received = db.relationship('FriendRequest',
                                               foreign_keys='FriendRequest.receiver_id',
                                               backref='receiver',
                                               lazy='dynamic')

    friend_requests_sent = db.relationship('FriendRequest',
                                           foreign_keys='FriendRequest.sender_id',
                                           backref='sender',
                                           lazy='dynamic')

    # Existing methods...

    def send_friend_request(self, recipient):
        # Check if already friends or has a pending request
        if not self.is_friend(recipient) and not self.has_pending_request(recipient) and not recipient.has_pending_request(self):
            # Create and add the new friend request
            friend_request = FriendRequest(sender_id=self.id, receiver_id=recipient.id)
            db.session.add(friend_request)
            db.session.commit()
            return "Friend request sent successfully."
        elif self.is_friend(recipient):
            return "You are already friends."
        elif self.has_pending_request(recipient):
            return "You have already sent a friend request to this user."
        elif recipient.has_pending_request(self):
            return "This user has already sent you a friend request."

    def has_pending_request(self, user):
        return self.friend_requests_received.filter_by(sender_id=user.id).count() > 0

    def accept_friend_request(self, sender):
        if self.has_pending_request(sender):
            friend_request = self.friend_requests_received.filter_by(sender_id=sender.id).first()
            self.add_friend(sender)  # Add the sender as a friend
            sender.add_friend(self)  # Add yourself as a friend to the sender
            db.session.delete(friend_request)
            db.session.commit()

    def update_profile(self, first_name=None, last_name=None, password=None, image_data=None, image_filename=None):
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if password:
            self.password = generate_password_hash(password)
        if image_data:
            self.image_data = image_data
        if image_filename:
            self.image_filename = image_filename
        db.session.commit()



class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id} at {self.timestamp}>'


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')

