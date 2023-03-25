from datetime import date
from pony.orm import *

db = Database()

class Member(db.Entity):
    name = PrimaryKey(str)
    join_date = Required(date)
    profile_picture = Optional(bytes)
    hosted_sessions = Set("Session")
    session_results = Set("SessionResult")


class Game(db.Entity):
    name = PrimaryKey(str)
    type = Required(str, unique=True)
    sessions = Set("Session")


class Session(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Required(Game)
    date = Required(date)
    host = Required(Member)
    results = Set("SessionResult")
    composite_key(game, date)

class SessionResult(db.Entity):
    id = PrimaryKey(int, auto=True)
    session = Required(Session)
    member = Required(Member)
    place = Required(int)
    score = Required(int)
    composite_key(session, member)
