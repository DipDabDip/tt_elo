from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
import math

#all classes in app.models are used to create tables in the db


#admin, contains primary key and foreign key to a User
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#game log, contaning a primary key, three foreign keys and a timestamp
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner = db.Column(db.Integer, db.ForeignKey('user.id'))
    loser = db.Column(db.Integer, db.ForeignKey('user.id'))
    reporter = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def get_time(self):
        return self.timestamp.strftime('%b-%d-%y - %H:%M:%S')

    def get_winner(self):
        return User.query.get(self.winner).fmt_name()
    
    def get_loser(self):
        return User.query.get(self.loser).fmt_name()

    def get_reporter(self):
        return User.query.get(self.reporter).fmt_name()

#database backup sunday
class SunUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    elo = db.Column(db.Float)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

#database backup wednesday
class WedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    elo = db.Column(db.Float)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

#main User class
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
    elo = db.Column(db.Float, default = 1000)

    def winperc(self):
        return str(round(100*self.wins/self.getwins(), 0)) + "%"

    #formatting last seen date
    def get_last_seen(self):
        return self.last_seen.strftime('%b-%d-%y - %H:%M:%S')

    #checks if user has admin privileges, returns as bool
    def is_admin(self):
        for admin in Admin.query.all():
            if self.id == admin.player_id:
                return True
        return False

    def fmt_name(self):
        MAX = 10
        return self.username[:MAX] + ("..."*(len(self.username) > MAX))

    #method to hash the password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #check inputted password against stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #for use in terminal when editing database
    def __repr__(self):
        return "User id: " + str(self.id) + " Username: " + str(self.username)


    #generates link for gravatar, see more here: https://en.gravatar.com/
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    #a very poorly named method that returns the amount of games played
    def getwins(self):
        return self.wins + self.losses
   
    #getter function for elo that also rounds it
    def getelo(self):
        return int(round(self.elo, 0))

    #calculates the probability that one player will beat another
    def ptobeat(self, other):
        return 1.0 / (1+1.0*math.pow(10, 1.0 * (self.elo - other.elo) / 400 ))

    #adjusts elos, wins, losses, when one player beats another
    def beat(self, other):
        p1 = other.ptobeat(self)
        p2 = 1-p1
        self.elo += 30 * (1-p1)
        other.elo += 30 * (0-p2)
        self.wins +=1
        other.losses +=1

    

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
