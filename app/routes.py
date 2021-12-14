from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, UpdateScoreForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Game
from werkzeug.urls import url_parse
from datetime import datetime

#class to help the formatting of the game table on the home page
class game_with_player:
    def __init__(self, game):
        self.winner = User.query.get(game.winner).username
        self.loser = User.query.get(game.loser).username
        self.reporter = User.query.get(game.reporter).username
        self.id = game.id
        self.timestamp = game.timestamp


#function to generate index
@app.route('/')
@app.route('/index')
def index():
    #generate and sort a list of players by elo for leaderboard 
    players = User.query.all()
    players.sort(key=lambda x: x.elo, reverse=True)
    #generate a chronological list of games for game log
    games = Game.query.all()
    games = [game_with_player(x) for x in games]
    games.reverse()
    #generate webpage with jinja
    return render_template('index.html', title='Home', players=players, games=games)


#function to generate login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    #redirect user if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #define web form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #ensure user details correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #if the user tried to access a page that requires login, this code redirects them to that page after logging in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    #render page with jinja template
    return render_template('login.html', title='Sign In', form=form)


#simple logout button, doesn't render a page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#register user page
@app.route('/register', methods=['GET', 'POST'])
def register():
    #redirect if user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #generate register form
    form = RegistrationForm()
    if form.validate_on_submit():
        #create User object from app.models
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        #add to db and save
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    #render page
    return render_template('register.html', title='Register', form=form)

#user profile page
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #render page
    return render_template('user.html', user=user)


#edit profile page
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #load web form from app.forms
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        #push changes to db
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        #loads the form with current data already loaded into the boxes
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    #render page
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


#page to update scores
@app.route('/update_scores', methods=['GET', 'POST'])
@login_required
def update_scores():
    #load form from app.forms
    form = UpdateScoreForm()
    if form.validate_on_submit():
        playerwin = User.query.filter_by(username=form.winner.data).first()
        playerlose = User.query.filter_by(username=form.loser.data).first()
        #method of user class that implements the 'Elo system'
        #fun little easter egg that also prevents players reporting that they played themselves
        if playerwin.id == playerlose.id:
            return redirect('https://www.youtube.com/watch?v=Zd9muK2M36c')
        playerwin.beat(playerlose)
        #log the game
        game = Game(winner = playerwin.id, loser = playerlose.id, reporter = current_user.id)
        #make necessary database changes
        db.session.add(game)
        db.session.commit()
        flash('Player scores updated!')
        return redirect(url_for('update_scores'))
    #render page
    return render_template('update_scores.html', title='Update Scores', form = form)

#before any requests are fullfilled, if user logged in, updates their last seen value
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#see here: http://www.gnuterrypratchett.com/
#an internet homage to Terry Pratchett, based off the discworld series. After the request is made to the server for a webpage
#and before the webpage is sent back, the server adds the homage to the header.
@app.after_request
def gnu_terry_pratchett(resp):
    resp.headers.add("X-Clacks-Overhead", "GNU Terry Pratchett")
    return resp