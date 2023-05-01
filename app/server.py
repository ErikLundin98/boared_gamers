from typing import Dict
from flask import (
    Flask,
    render_template,
    request,
)
from flask_login.login_manager import LoginManager
from flask_login import (
    login_required, 
    login_user, 
    logout_user,
    current_user,
)
from datetime import date
from pony.flask import Pony
from pony.orm import select, count
from app.constants import DATABASE_PATH
from app.database import (
    db,
    Member,
    Game,
    Session,
    SessionResult,
)
from dotenv import load_dotenv
import base64
import os
import trueskill

load_dotenv()
app = Flask(__name__)
app.config.update(dict(
    DEBUG = True,
    PONY = {
        'provider': 'sqlite',
        'filename': DATABASE_PATH,
        'create_db': True
    },
    SECRET_KEY = os.getenv("PASSWORD"),
))
login_manager = LoginManager(app=app)

db.bind(**app.config["PONY"])
db.generate_mapping(create_tables=True)
Pony(app)

@app.route("/")
def home():
    """Load home page."""
    leaderboard = _get_leaderboard()
    upcoming_sessions = _get_upcoming_sessions()
    return render_template(
        "home.html", 
        title="Board gamers",
        leaderboard=leaderboard,
        upcoming_sessions=upcoming_sessions,
        user_info=_get_user_info(),
    )


def get_trueskill_ratings() -> Dict[Member, trueskill.Rating]:
    """Get trueskill ratings based on previous results."""

    ratings = {}
    for member in select(member.name for member in Member):
        ratings[member] = trueskill.Rating()

    for session in select(session for session in Session).order_by(Session.date):
        # in each session, create a game with all present players
        # get ordered list of players based on standings
        ordered_results = list(
            select((result.member.name, result.place) for result in SessionResult if result.session == session).order_by(2)
        )
        if len(ordered_results) < 2:
            continue
        ordered_members = [result[0] for result in ordered_results]
        ordered_ratings = [ratings[member] for member in ordered_members]
        game = [(rating,) for rating in ordered_ratings]
        new_ratings = [new_rating[0] for new_rating in trueskill.rate(game)]

        for member, new_rating in zip(ordered_members, new_ratings):
            ratings[member] = new_rating
        
    return ratings
    

@login_manager.user_loader
def load_user(name):
    """Load user."""
    return Member.get(name=name)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Log in user."""
    message = "You are not logged in"
    if current_user.is_authenticated:
        message = f"You are already logged in as {current_user.get_id()}"

    if request.method == "POST":
        password = request.form.get('password')
        name = request.form.get('name')
        member = Member.get(name=name)
        if member and password is not None and password == app.config["SECRET_KEY"]:
            login_user(member, remember=True)
            message = "You are now logged in."
        else:
            message = "Incorrect username/password"
    
    return render_template(
        "login.html", message=message, user_info=_get_user_info(),
    )

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log out user"""
    logout_user()
    return render_template(
        "login.html", message="You are now logged out", user_info=_get_user_info(),
    )

@app.route("/input")
def input_page():
    """Input page to add game data."""
    games = list(select(
        game.name for game in Game
    ))
    members = list(select(
        member.name for member in Member
    ))
    sessions = list(select(
        session for session in Session
    ))
    return render_template(
        "input.html", 
        title="Jinja and Flask", 
        date=date.today().strftime("%Y-%m-%d"),
        games=games,
        members=members,
        sessions=sessions,
        user_info=_get_user_info(),
    )

@app.route("/input/member", methods=["POST"])
def add_member():
    """Add member to db."""
    name = request.form.get('name')
    join_date = request.form.get('join_date')
    picture_file = request.files.get("profile_picture").read()
    existing_member = Member.get(name=name)
    if existing_member:
        existing_member.set(join_date=join_date, profile_picture=picture_file)
    else:
        Member(name=name, join_date=join_date, profile_picture=picture_file)
    return input_page()

@app.route("/input/game", methods=["POST"])
@login_required
def add_game():
    """Add game to db."""
    game = request.form.get('game')
    type = request.form.get('type')
    Game(name=game, type=type)
    return input_page()

@app.route("/input/session", methods=["POST"])
@login_required
def add_session():
    """Add session to db."""
    game = request.form.get('game')
    date = request.form.get('date')
    host = request.form.get('host')
    Session(game=game, host=host, date=date)
    
    return input_page()


@app.route("/input/session_result", methods=["POST"])
@login_required
def add_session_result():
    """Add result to session in db."""
    session = request.form.get('session')
    member = request.form.get('member')
    place = request.form.get('place')
    score = request.form.get('score')
    existing_session_result = SessionResult.get(session=session, member=member)
    if existing_session_result:
        existing_session_result.set(place=place, score=score)
    else:
        SessionResult(session=session, member=member, place=place, score=score)
    return input_page()

def _get_leaderboard():
    """Get leaderboard of player scores."""
    leaderboard = [
        {"name": row[0], "score": row[1], "number_sessions": row[2]}
        for row in
        select(
            (group.member.name, sum(group.score), count(group))
            for group in SessionResult
        ).order_by(
            -2 # order by score desc.
        )
    ]
    rank = 1
    last_score = -1

    trueskill_ratings = get_trueskill_ratings()
    for i, member in enumerate([l["name"] for l in leaderboard]):
        picture = (
            base64.standard_b64encode(Member[member].profile_picture).decode("utf-8")
        )
        leaderboard[i]["trueskill_rating"] = round(trueskill.expose(trueskill_ratings[member]), 2)
        leaderboard[i]["profile_picture"] = picture
        rank = rank + 1 if leaderboard[i]["score"] < last_score else rank
        leaderboard[i]["rank"] = rank
        last_score = leaderboard[i]["score"]
    print(leaderboard)
    return leaderboard

def _get_upcoming_sessions():
    """Get information on coming sessions."""
    current_date = date.today()
    query = select(
        (s.date, s.host.name, s.game.name) 
        for s in Session 
        if s.date >= current_date
    )
    upcoming_sessions = [
        {"date": session[0], "host": session[1], "game": session[2]}
        for session in query
    ]
    return upcoming_sessions

def _get_user_info():
    """Get user welcome message."""
    return current_user.get_id() or "nonexistent"