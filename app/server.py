from flask import (
    Flask,
    render_template,
    request,
)
from datetime import date
from pony.flask import Pony
from pony.orm import select, count, desc
from app.constants import DATABASE_PATH
from app.database import (
    db,
    Member,
    Game,
    Session,
    SessionResult,
)
import base64

app = Flask(__name__)
app.config.update(dict(
    DEBUG = True,
    PONY = {
        'provider': 'sqlite',
        'filename': DATABASE_PATH,
        'create_db': True
    }
))
db.bind(**app.config["PONY"])
db.generate_mapping(create_tables=True)

Pony(app)

@app.route("/")
def home():
    leaderboard = _get_leaderboard()
    upcoming_sessions = _get_upcoming_sessions()
    return render_template(
        "home.html", 
        title="Board gamers",
        leaderboard=leaderboard,
        upcoming_sessions=upcoming_sessions,
    )

@app.route("/input")
def input_page():
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
    )

@app.route("/input/member", methods=["POST"])
def add_member():
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
def add_game():
    game = request.form.get('game')
    type = request.form.get('type')
    Game(name=game, type=type)
    return input_page()

@app.route("/input/session", methods=["POST"])
def add_session():
    game = request.form.get('game')
    date = request.form.get('date')
    host = request.form.get('host')
    Session(game=game, host=host, date=date)
    
    return input_page()


@app.route("/input/session_result", methods=["POST"])
def add_session_result():
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
    for i, member in enumerate([l["name"] for l in leaderboard]):
        picture = (
            base64.standard_b64encode(Member[member].profile_picture).decode("utf-8")
        )
        leaderboard[i]["profile_picture"] = picture
        rank = rank + 1 if leaderboard[i]["score"] < last_score else rank
        leaderboard[i]["rank"] = rank
        last_score = leaderboard[i]["score"]

    return leaderboard

def _get_upcoming_sessions():
    """Get information on coming sessions"""
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
    print(upcoming_sessions)
    return upcoming_sessions