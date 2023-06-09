from datetime import date
from pony.orm import *

db = Database()

class Member(db.Entity):
    name = PrimaryKey(str)
    join_date = Required(date)
    profile_picture = Optional(bytes)
    hosted_sessions = Set("Session")
    session_results = Set("SessionResult")

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.name)

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
    score = Required(float)
    composite_key(session, member)
