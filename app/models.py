from . import db
from datetime import datetime
import pytz


def get_kst_now():
    utc_now = datetime.utcnow()
    kst_now = utc_now.replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone('Asia/Seoul'))
    return kst_now


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(255), primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User와 ChatRoom은 1대 다 관계
    chat_rooms = db.relationship('ChatRoom', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'created_at': self.created_at
        }


class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id'), nullable=False)
    room_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ChatRoom과 Message는 1대 다 관계
    messages = db.relationship('Message', backref='chat_room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_name': self.room_name,
            'created_at': self.created_at
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    chatroom_id = db.Column(db.String(255), db.ForeignKey(
        'chat_rooms.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'chatroom_id': self.chatroom_id,
            'user_id': self.user_id,
            'message_text': self.message_text,
            'created_at': self.created_at
        }
