from config import *
from models import *

def getStudios():
    data = db.session.query(Studio.studio_id, Studio.name).all()
    return sorted([(str(row.studio_id), row.name) for row in data], key=lambda x: x[1].lower())

def getGenres():
    data = db.session.query(Genres.genre).all()
    return sorted([row.genre for row in data], key=lambda x: x[0].lower())

def getDirectors():
    data = db.session.query(Director.director_id, Director.firstname, Director.surname, Director.birth_date)
    return sorted([(str(row.director_id), row.firstname + ' ' + row.surname) for row in data], key=lambda x: x[1].lower())
    # TODO display birthdate if 2 directors with same firstname and surname

def getActors():
    data = db.session.query(Actor.actor_id, Actor.firstname, Actor.surname, Actor.birth_date)
    return sorted([(str(row.actor_id), row.firstname + ' ' + row.surname) for row in data], key=lambda x: x[1].lower())