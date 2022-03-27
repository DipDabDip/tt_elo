from app import db
from app.models import User, Game
from flask_googlecharts import BarChart

#early implementation of user stats - design features as discussed with Kyle & Will.
#I'm probably going to end up on a horrible hacky implementation of matplotlib as i dont understand the OOP form of it and id rather just get something working
#small bit of design talk here - i'm gonna assume a lot of this stuff can be implemented as methods of the User class - and theres probably some good code reasons for and against doing that
#i just dont want to, i think a separate stats file will be nice, and thats reason enough
#plus its like functional programming, which is good for data

#experimentation with google charts 
def chart():
    my_chart = BarChart("my_chart", options={"title": "my_Chart"})
    my_chart.add_column("string", "competitor")
    my_chart.add_column("number", "score")
    mychart.add_row(["Mike", 70], ["John", 81], ["Bee", 77])
    return my_chart

#calculates a users record elo
def peak_elo(user):
    #i came up with some clever ways of doing this but its actually just gonna be this
    return max(elo_over_time(user)[1])

def elo_over_time(user):
    #search all games containing the user
    games = Game.query.all()
    elo_over_time = []
    dates = [] #so at first i though - hey, lets start with 1000 elo and the date they started, but then i realised i had no way of finding the date they created their account, and also, everyone already knows they start at 1000
    #this is where the way im implementing might be a little janky, but ill live (copy paste exists)
    #essentially i'll run through all the games, ill have to reset the elo of all the players so its super important i end this with db.session.rollback()
    #theres also a solid chance that two requests at a similar time could seriously break everything but theres not so many users that im super worried (ok im terrified but still)
    users = User.query.all()
    for u in users:
        u.elo = 1000
    #simple iterate through games and just note the elo of the user each time it changes
    for g in games:
        winner = User.query.get(g.winner)
        loser = User.query.get(g.loser)
        winner.beat(loser)
        if winner == user:
            elo_over_time.append(winner.elo)
            dates.append(g.timestamp)
        elif loser == user:
            elo_over_time.append(loser.elo)
            dates.append(g.timestamp)
    db.session.rollback()#super important line right here do NOT mess with it
    return (dates, elo_over_time)



def streak(user):
    #gonna iterate through the game log backwards to their last game, determine wins or losses, then count until it changes or the games run out
    g = Game.query.filter_by(winner = user.id) + Game.query.filter_by(loser = user.id)
    g.sort(sort(key=lambda x: x.timestamp, reverse=True)) #sorts list backwards in time
    first, *rest = g
    streak = 1
    if user.id == first.winner:
        #count winstreak
        for game in rest:
            if game.winner == user.id:
                streak += 1
            else:
                return "Win streak = " + str(streak)
    else:
        for game in rest:
            #count lossstreak
            if game.loser == user.id:
                streak += 1
            else:
                return "Loss streak = " + str(streak)