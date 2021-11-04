from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
import math

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    #user profile stuff
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow())
    
    #actual player stuff
    wins = db.Column(db.Integer, default = 0)
    losses = db.Column(db.Integer, default = 0)
    elo= db.Column(db.Float, default = 1000)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def getwins(self):
        return self.wins + self.losses
    
    def ptobeat(self, other):
        return 1.0 * 1.0 / (1+1.0*math.pow(10, 1.0 * (self.elo - other.elo) / 400 ))

    def beat(self, other):
        p2 = other.ptobeat(self)
        p1 = 1-p2
        self.elo += 30 * (1-p1)
        other.elo += 30 * (0-p2)
        self.wins +=1
        other.losses +=1

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
