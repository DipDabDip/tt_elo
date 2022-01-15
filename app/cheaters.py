from app import db
from app.models import Game, User, SunUser, WedUser

def Backup_User(u, sw):
    if sw == 'S':
        b = SunUser()
    elif sw == 'W':
        b = SunUser()
    b.player_id = u.id
    b.elo = u.elo
    b.wins = u.wins
    b.losses = u.losses
    db.session.add(b)
    db.session.commit()
    
def Clear(sw):
    if sw == 'S':
        data = SunUser.query.all()
    elif sw == 'W':
        data = WedUser.query.all()
    for x in data:
        db.session.delete(x)
    db.session.commit()

def FromBackup(sw):
    if sw == 'S':
        backup = SunUser.query.all()
    elif sw == 'W':
        backup = WedUser.query.all()
    games = Game.query.all()
    for player in backup:
        user = User.query.get(player.player_id)
        user.elo = player.elo
        user.wins = player.wins
        user.losses = player.losses
    for game in games:
        winner = User.query.get(game.winner)
        loser = User.query.get(game.loser)
        winner.beat(loser)
    db.session.commit()