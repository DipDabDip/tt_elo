from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
import math

#all classes in app.models are used to create tables in the db

#cool fact! originally i had two separate Users, but it actually makes more sense to have one inherit from the other
class Abstract_User:
    id = db.Column(db.Integer, primary_key=True)
    username = "Abstract - please report this!"
    elo = db.Column(db.Float, default = 1000)
    wins = db.Column(db.Integer, default = 0)
    losses = db.Column(db.Integer, default = 0)

    #backup in case this somehow actually gets made
    def fmt_name(self):
        return self.username

    #elo algorithm! so that the deleted users can exist without storing data on a user
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

    #getter function for elo that also rounds it
    def getelo(self):
        return int(round(self.elo, 0))
    
    #returns win percentage of user
    def winperc(self):
        return str(int(round(100*self.wins/self.getwins(), 0))) + "%"

    #a very poorly named method that returns the amount of games played
    def getwins(self):
        return self.wins + self.losses

#deleted user class - user is not suitable as redundant data fields are not safe to store
class Del_User(Abstract_User, UserMixin, db.Model):
    username = "[Deleted User]"
    user_id = db.Column(db.Integer, index=True, unique=True)



#main User class
class User(Abstract_User,UserMixin, db.Model):
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #user profile stuff
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow())


    #function to delete a user
    def del_user(self):
        #create deleted user
        del_user = Del_User(user_id=self.id, elo=self.elo, wins=self.wins, losses=self.losses)
        #add deleted user to backup
        db.session.add(del_user)
        #remove user
        db.session.delete(self)
        db.session.commit()


    #formatting last seen date
    def get_last_seen(self):
        return self.last_seen.strftime('%b-%d-%y - %H:%M:%S')

    #checks if user has admin privileges, in User as deleted shouldnt be admin
    def is_admin(self):
        for admin in Admin.query.all():
            if self.id == admin.player_id:
                return True
        return False

    #overwrite as users will input longer names than might fit - single var for max length so i can adjust
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


    #simple formatting for timestamp
    def get_time(self):
        return self.timestamp.strftime('%b-%y-%d - %H:%M:%S')

    #handles errors caused by deleted users in game     log
    #may be redundant due to fmt_name defined in Del_User - left here on the off chance its called
    def get_winner(self):
        user = User.query.get(self.winner)
        if user is None:
            return "[Deleted User]"
        else:
            return user.fmt_name()
    
    #same as game_winner
    def get_loser(self):
        user =  User.query.get(self.loser)
        if user is None:
            return "[Deleted User]"
        else:
            return user.fmt_name()

    #same as game_winner
    def get_reporter(self):
        user = User.query.get(self.reporter)
        if user is None:
            return "[Deleted User]"
        else:
            return user.fmt_name()

 
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
