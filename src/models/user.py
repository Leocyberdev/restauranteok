from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
from src.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # <- ESSENCIAL para evitar conflito com palavra reservada

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_in=3600):
        self.reset_token = secrets.token_urlsafe(20)
        self.reset_token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.commit()
        return self.reset_token

    @staticmethod
    def verify_reset_token(token):
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expiration and user.reset_token_expiration > datetime.utcnow():
            return user
        return None

    def __repr__(self):
        return '<User %r>' % self.username


