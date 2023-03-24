from config import *
from models import *

def getStudios():
    studios = db.session.query(Studio.studio_id, Studio.name).all()
    return sorted([(str(row.studio_id), row.name) for row in studios], key=lambda x: x[1].lower())

def getGenres():
    genres = db.session.query(Genres.genre).all()
    return sorted([row.genre for row in genres], key=lambda x: x[0].lower())

def getDirectors():
    directors = db.session.query(Director.director_id, Director.firstname, Director.surname, Director.birth_date)
    directors = [(str(row.director_id), row.firstname + ' ' + row.surname, row.birth_date) for row in directors]
    return unambiguous(directors)

def getActors():
    actors = db.session.query(Actor.actor_id, Actor.firstname, Actor.surname, Actor.birth_date)
    actors = [(str(row.actor_id), row.firstname + ' ' + row.surname, row.birth_date) for row in actors]
    return unambiguous(actors)

def unambiguous(data): # when directors/actors with the exactly same full name occure it appends birth_date to full_name in dropdownlist
    full_names = [element[1] for element in data]
    data_unambiguous = ['' for _ in range(len(data))]
    count = 0
    for person in data:
        cur_full_name = person[1]
        full_names = full_names[1:]
        if cur_full_name in full_names:
            i = full_names.index(cur_full_name) + count + 1
            data_unambiguous[count] = (person[0], cur_full_name + ' ' + str(person[2]))
            data_unambiguous[i] = (str(data[i][0]), cur_full_name + ' ' + str(data[i][2]))
        else:
            if data_unambiguous[count] == '':
                data_unambiguous[count] = person[:2]
        count+=1
    return sorted(data_unambiguous, key=lambda x: x[1].lower())

def initGenres():
    for genre in init_genres:
        g = db.session.query(Genres).filter(
            Genres.genre == genre
        ).first()
        if g is None:
            row = Genres(genre=genre)
            db.session.add(row)
    db.session.commit()

def convertName(name): # convert name to have first big letter and small as the rest
    dash_fragments = name.split('-')
    space_fragments = name.split(' ')
    converted = ""
    if len(dash_fragments) > 1:
        for fragment in dash_fragments:
            c = [fragment[0].upper()]
            for char in fragment[1:]:
                c.append(char.lower())
            converted += "".join(c)+'-'
        return converted[:-1]
    if len(space_fragments) > 1:
        for fragment in space_fragments:
            c = [fragment[0].upper()]
            for char in fragment[1:]:
                c.append(char.lower())
            converted += "".join(c)+' '
        return converted[:-1]
    if len(space_fragments) == 1 and len(dash_fragments) == 1:
        c = [name[0].upper()]
        for char in name[1:]:
            c.append(char.lower())
        return ''.join(c)

def nameHasNumbers(name): # check if name contains any numbers
    return any(char.isdigit() for char in name)

def nameInvalid(name):
    # accepts regular names
    # and names with one or multiple dashes '-'
    # also with spaces e.g John Smith-Jackson
    if nameHasNumbers(name):
        return True
    if re.match("^[a-zA-ZœęßóąśðæŋəłżźćńµΩĘÓĄŚÐÆŊŁŻŹĆŃ\s]+([-][a-zA-ZœęßóąśðæŋəłżźćńµΩĘÓĄŚÐÆŊŁŻŹĆŃ\s]+)*$", name): 
        return False
    return True
