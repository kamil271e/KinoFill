CREATE SEQUENCE filmweb.users_id_seq;

CREATE TABLE filmweb.Users(
    user_id integer PRIMARY KEY DEFAULT nextval('filmweb.users_id_seq'),
    login varchar(20) NOT NULL UNIQUE,
    password_hash varchar(128) NOT NULL,
    join_date date NOT NULL DEFAULT CURRENT_DATE,
    description text,
    active char(1) NOT NULL DEFAULT 't',
    user_type char(1) NOT NULL CHECK (user_type IN ('w', 's', 'd')),
    CHECK(join_date <= CURRENT_DATE),
    CHECK(active in ('t','f'))
);

CREATE TABLE filmweb.Studios(
    studio_id integer PRIMARY KEY,
    name varchar(30) NOT NULL UNIQUE,
    country varchar(20),
    creation_date date,
    viewers_rating decimal(3, 2),
    FOREIGN KEY(studio_id) REFERENCES filmweb.Users(user_id),
    CHECK(creation_date <= CURRENT_DATE)
);

CREATE TABLE filmweb.Directors(
    director_id serial PRIMARY KEY,
    firstname varchar(20) NOT NULL,
    surname varchar(20) NOT NULL,
    birth_date date NOT NULL,
    country varchar(20),
    rate decimal(3, 2),
    studio_id integer,
    FOREIGN KEY(studio_id) REFERENCES filmweb.Studios(studio_id),
    UNIQUE(firstname, surname, birth_date)
);

CREATE TABLE filmweb.Movies(
    movie_id serial PRIMARY KEY,
    name varchar(30) NOT NULL,
    creation_year integer NOT NULL,
    length integer NOT NULL,
    viewers_rating decimal(3,2),
    studio_id integer NOT NULL,
    director_id integer NOT NULL,
    UNIQUE(name, creation_year),
    FOREIGN KEY(studio_id) REFERENCES filmweb.Studios(studio_id),
    FOREIGN KEY(director_id) REFERENCES filmweb.Directors(director_id),
    CHECK( (CAST (EXTRACT(year from CURRENT_DATE) AS INTEGER) ) >= creation_year),
    CHECK(length > 0)
);

CREATE TABLE filmweb.Series(
    series_id serial PRIMARY KEY,
    name varchar(30) NOT NULL,
    episodes integer NOT NULL,
    seasons integer NOT NULL,
    viewers_rating decimal(3,2),
    studio_id integer NOT NULL,
    director_id integer NOT NULL,
    UNIQUE(name, episodes),
    FOREIGN KEY(studio_id) REFERENCES filmweb.Studios(studio_id),
    FOREIGN KEY(director_id) REFERENCES filmweb.Directors(director_id),
    CHECK(episodes >= 0),
    CHECK(seasons >= 0),
    CHECK(episodes >= seasons),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);

CREATE TABLE filmweb.Actors(
    actor_id serial PRIMARY KEY,
    firstname varchar(20) NOT NULL,
    surname varchar(20) NOT NULL,
    birth_date date NOT NULL,
    country varchar(20),
    viewers_rating decimal(3, 2),
    studio_id integer,
    FOREIGN KEY(studio_id) REFERENCES filmweb.Studios(studio_id),
    UNIQUE(firstname, surname, birth_date),
    CHECK(birth_date < CURRENT_DATE),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);


CREATE TABLE filmweb.Journalists(
    journalist_id integer PRIMARY KEY,
    nickname varchar(20) NOT NULL,
    firstname varchar(20),
    surname varchar(20),
    birth_date date,
    FOREIGN KEY(journalist_id) REFERENCES filmweb.Users(user_id),
    UNIQUE(nickname),
    CHECK(birth_date < CURRENT_DATE)
);

CREATE TABLE filmweb.Viewers(
    viewer_id integer PRIMARY KEY,
    is_public char(1) NOT NULL,
    nickname varchar(30),
    FOREIGN KEY(viewer_id) REFERENCES filmweb.Users(user_id),
    CHECK(is_public in ('t', 'f')),
    CHECK(((is_public in ('t')) and (nickname is NOT NULL)) or ((is_public in ('f')) and (nickname is NULL)))
);

CREATE OR REPLACE PROCEDURE filmweb.newUser(
  login VARCHAR(20),
  password_hash VARCHAR(128),
  join_date DATE,
  description TEXT,
  active CHAR(1),
  user_type CHAR(1), -- User
  nickname VARCHAR(30),
  country VARCHAR(20),
  creation_date DATE, -- Studio
  firstname VARCHAR(20),
  surname VARCHAR(20),
  birth_date DATE, -- Journalist
  is_public CHAR(1) -- Viewer
)
AS $$
DECLARE
  user_id filmweb.Users.user_id%TYPE;
BEGIN
  SELECT nextval('filmweb.users_id_seq') INTO user_id;
  INSERT INTO filmweb.Users VALUES (user_id, login, password_hash, join_date, description, active, user_type);
  IF user_type = 'w' THEN
    INSERT INTO filmweb.Viewers VALUES (user_id, is_public, nickname);
  ELSIF user_type = 'd' THEN
    INSERT INTO filmweb.Journalists VALUES (user_id, nickname, firstname, surname, birth_date);
  ELSIF user_type = 's' THEN
    INSERT INTO filmweb.Studios VALUES (user_id, nickname, country, creation_date);
  END IF;
end;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION filmweb.xor3(a int, b int, c int)
RETURNS boolean AS $$
BEGIN
  IF (a IS NOT NULL AND b IS NULL AND c IS NULL) OR
     (a IS NULL AND b IS NOT NULL AND c IS NULL) OR
     (a IS NULL AND b IS NULL AND c IS NOT NULL) THEN
    RETURN true;
  ELSE
    RETURN false;
  END IF;
end;
$$ LANGUAGE plpgsql;


CREATE TABLE filmweb.Reviews(
    review_id serial PRIMARY KEY,
    rate integer NOT NULL,
    posting_date date default CURRENT_DATE NOT NULL,
    content text,
    author_type char(1) NOT NULL,
    viewer_id integer,
    journalist_id integer,
    review_object char(1) NOT NULL,
    movie_id integer,
    series_id integer,
    actor_id integer,
    viewers_rating decimal(3,2),
    CHECK(author_type IN ('w','d')),
    CHECK((viewer_id is NOT NULL AND journalist_id is NULL) OR (viewer_id is NULL AND journalist_id is NOT NULL)),
    CHECK(((author_type IN ('w')) AND (viewer_id IS NOT NULL)) or (author_type IN ('d') AND (journalist_id is NOT NULL))),
    CHECK(review_object IN ('f','s','a')),
    CHECK(xor3(movie_id, series_id, actor_id)),
    FOREIGN KEY(viewer_id) REFERENCES filmweb.Viewers(viewer_id),
    FOREIGN KEY(journalist_id) REFERENCES filmweb.Journalists(journalist_id),
    FOREIGN KEY(movie_id) REFERENCES filmweb.Movies(movie_id),
    FOREIGN KEY(series_id) REFERENCES filmweb.Series(series_id),
    FOREIGN KEY(actor_id) REFERENCES filmweb.Actors(actor_id),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);

CREATE TABLE filmweb.News(
    id_news serial PRIMARY KEY,
    content text NOT NULL,
    publication_date date default CURRENT_DATE NOT NULL,
    journalist_id integer,
    studio_id integer,
    FOREIGN KEY(journalist_id) REFERENCES filmweb.Journalists(journalist_id),
    FOREIGN KEY(studio_id) REFERENCES filmweb.Studios(studio_id),
    CHECK((studio_id is NOT NULL AND journalist_id is NULL) OR (studio_id is NULL AND journalist_id is NOT NULL)),
    CHECK(publication_date <= CURRENT_DATE)
);

CREATE TABLE filmweb.Movie_Characters(
    character_id serial PRIMARY KEY,
    character_name varchar(30) NOT NULL,
    movie_id integer NOT NULL,
    actor_id integer NOT NULL,
    FOREIGN KEY(movie_id) REFERENCES filmweb.Movies(movie_id),
    FOREIGN KEY(actor_id) REFERENCES filmweb.Actors(actor_id),
    UNIQUE(character_name, movie_id, actor_id)
);

CREATE TABLE filmweb.Series_Characters(
    character_id serial PRIMARY KEY,
    character_name varchar(30) NOT NULL,
    series_id integer NOT NULL,
    actor_id integer NOT NULL,
    FOREIGN KEY(series_id) REFERENCES filmweb.Series(series_id),
    FOREIGN KEY(actor_id) REFERENCES filmweb.Actors(actor_id),
    UNIQUE(character_name, series_id, actor_id)
);

CREATE TABLE filmweb.Genres(
    genre varchar(20) PRIMARY KEY
);

CREATE TABLE filmweb.Movie_genres(
    genre varchar(20),
    movie_id integer,
    PRIMARY KEY(genre, movie_id),
    FOREIGN KEY(genre) REFERENCES filmweb.Genres(genre),
    FOREIGN KEY(movie_id) REFERENCES filmweb.Movies(movie_id)
);

CREATE TABLE filmweb.Series_genres(
    genre varchar(20),
    series_id integer,
    PRIMARY KEY(genre, series_id),
    FOREIGN KEY(genre) REFERENCES filmweb.Genres(genre),
    FOREIGN KEY(series_id) REFERENCES filmweb.Series(series_id)
);

CREATE TABLE filmweb.Journalists_reviews_ratings(
    viewers_rating integer not null,
    review_id integer not null,
    viewer_id integer not null,
    PRIMARY KEY(review_id, viewer_id),
    FOREIGN KEY(viewer_id) REFERENCES filmweb.Viewers(viewer_id),
    FOREIGN KEY(review_id) REFERENCES filmweb.Reviews(review_id),
    CHECK(viewers_rating = -1 OR viewers_rating = 1)
);

-- sample inserts
-- insert into filmweb.Users (login, password_hash, user_type) values ('label', 'xyz', 's');
-- insert into filmweb.Users (login, password_hash, user_type) values ('viewer', 'xyz', 'w');
-- insert into filmweb.Users (login, password_hash, user_type) values ('journalist', 'xyz', 'd');

-- insert into filmweb.Studios (studio_id, name) values (1, 'studio1');

-- insert into filmweb.Viewers (viewer_id, is_public, nickname) values (2, 't','viewer1');

-- insert into filmweb.Journalists (journalist_id, nickname) values (3, 'journalist1');

-- insert into filmweb.Directors (name, surname, birth_date) values ('janusz','iksinski','1988-02-02');

-- insert into filmweb.Movies (name, creation_year, length, studio_id, director_id) values ('Lefleur', 1998, 122, 1, 1);

-- insert into filmweb.Series (name, episodes, seasons, studio_id, director_id) values ('something', 107, 13, 1, 1);

-- insert into filmweb.Actors (name, surname, birth_date) values ('John', 'Doe', '1992-02-12');

-- insert into filmweb.Reviews (rate, author_type, viewer_id, review_object, movie_id) values (5, 'w', 2, 'f', 1);

-- insert into filmweb.News (content, journalist_id) values ('hello', 3);

-- insert into filmweb.Movie_characters (character_name, movie_id, actor_id) values ('batman', 1, 1);

-- insert into filmweb.Series_characters (character_name, series_id, actor_id) values ('hulk', 1, 1);

-- insert into filmweb.Genres (genre) values ('sci-fi');

-- insert into filmweb.Movie_genres (genre, movie_id) values ('sci-fi', 1);

-- insert into filmweb.Series_genres (genre, series_id) values ('sci-fi', 1);

-- insert into filmweb.Journalist_review_viewers_ratings (viewers_rating, review_id, viewer_id) values (1, 1, 2);


CALL filmweb.newUser(
  'user123',
  'password123',
  '2022-01-01',
  'I am a new viewer',
  't',
  'w',
  'viewer1',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  't'
);


drop table filmweb.Journalists_reviews_ratings;
drop table filmweb.Series_genres;
drop table filmweb.Movie_genres;
drop table filmweb.Genres;
drop table filmweb.Series_Characters;
drop table filmweb.Movie_Characters;
drop table filmweb.News;
drop table filmweb.Reviews;
drop table filmweb.Viewers;
drop table filmweb.Journalists;
drop table filmweb.Actors;
drop table filmweb.Series;
drop table filmweb.Movies;
drop table filmweb.Directors;
drop table filmweb.Studios;
drop table filmweb.Users;
drop function filmweb.xor3;
drop procedure filmweb.newUser;
drop sequence filmweb.users_id_seq;
