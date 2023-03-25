from flask import (
    Flask,
    render_template,
    request,
)
from datetime import date
from pony.flask import Pony
from pony.orm import select
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
    sql = (
        "SELECT member, SUM(score) as score, ROW_NUMBER() OVER() as rank, "
        "COUNT(*) as number_sessions "
        "FROM SessionResult "
        "GROUP BY member "
        "ORDER BY score DESC"
    )
    leaderboard = [
        {"name": row[0], "score": row[1], "rank": row[2], "number_sessions": row[3]}
        for row in db.select(sql)
    ]
    images = []
    for i, member in enumerate([l["name"] for l in leaderboard]):
        picture = (
            base64.standard_b64encode(Member[member].profile_picture).decode("utf-8")
        )
        leaderboard[i]["profile_picture"] = picture
        images.append(picture)

    return render_template(
        "home.html", 
        title="Board gamers",
        leaderboard=leaderboard,
        images=images
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
    if member := Member.get(name=name):
        member.set(join_date=join_date, profile_picture=picture_file)
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

    if session_result := SessionResult.get(session=session, member=member):
        session_result.set(place=place, score=score)
    else:
        SessionResult(session=session, member=member, place=place, score=score)
    return input_page()