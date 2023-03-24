CREATE SCHEMA kinofill;

CREATE SEQUENCE kinofill.users_id_seq;

CREATE TABLE kinofill.Users(
    user_id integer PRIMARY KEY DEFAULT nextval('kinofill.users_id_seq'),
    login varchar(20) NOT NULL UNIQUE,
    password_hash varchar(128) NOT NULL,
    join_date date NOT NULL DEFAULT CURRENT_DATE,
    description text,
    active char(1) NOT NULL DEFAULT 't',
    user_type char(1) NOT NULL CHECK (user_type IN ('w', 's', 'd')),
    CHECK(join_date <= CURRENT_DATE),
    CHECK(active in ('t','f'))
);

CREATE TABLE kinofill.Studios(
    studio_id integer PRIMARY KEY,
    name varchar(30) NOT NULL UNIQUE,
    country varchar(30),
    creation_date date,
    viewers_rating decimal(3, 2),
    FOREIGN KEY(studio_id) REFERENCES kinofill.Users(user_id),
    CHECK(creation_date <= CURRENT_DATE)
);

CREATE TABLE kinofill.Directors(
    director_id serial PRIMARY KEY,
    firstname varchar(20) NOT NULL,
    surname varchar(20) NOT NULL,
    birth_date date NOT NULL,
    country varchar(30),
    rate decimal(3, 2),
    studio_id integer,
    FOREIGN KEY(studio_id) REFERENCES kinofill.Studios(studio_id),
    UNIQUE(firstname, surname, birth_date)
);

CREATE TABLE kinofill.Movies(
    movie_id serial PRIMARY KEY,
    name varchar(30) NOT NULL,
    creation_year integer NOT NULL,
    length integer NOT NULL,
    viewers_rating decimal(3,2),
    studio_id integer NOT NULL,
    director_id integer NOT NULL,
    UNIQUE(name, creation_year),
    FOREIGN KEY(studio_id) REFERENCES kinofill.Studios(studio_id),
    FOREIGN KEY(director_id) REFERENCES kinofill.Directors(director_id),
    CHECK( (CAST (EXTRACT(year from CURRENT_DATE) AS INTEGER) ) >= creation_year),
    CHECK(length > 0)
);

CREATE TABLE kinofill.Series(
    series_id serial PRIMARY KEY,
    name varchar(30) NOT NULL,
    episodes integer NOT NULL,
    seasons integer NOT NULL,
    viewers_rating decimal(3,2),
    studio_id integer NOT NULL,
    director_id integer NOT NULL,
    UNIQUE(name, episodes),
    FOREIGN KEY(studio_id) REFERENCES kinofill.Studios(studio_id),
    FOREIGN KEY(director_id) REFERENCES kinofill.Directors(director_id),
    CHECK(episodes >= 0),
    CHECK(seasons >= 0),
    CHECK(episodes >= seasons),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);

CREATE TABLE kinofill.Actors(
    actor_id serial PRIMARY KEY,
    firstname varchar(20) NOT NULL,
    surname varchar(20) NOT NULL,
    birth_date date NOT NULL,
    country varchar(30),
    viewers_rating decimal(3, 2),
    studio_id integer,
    FOREIGN KEY(studio_id) REFERENCES kinofill.Studios(studio_id),
    UNIQUE(firstname, surname, birth_date),
    CHECK(birth_date < CURRENT_DATE),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);


CREATE TABLE kinofill.Journalists(
    journalist_id integer PRIMARY KEY,
    nickname varchar(20) NOT NULL,
    firstname varchar(20),
    surname varchar(20),
    birth_date date,
    FOREIGN KEY(journalist_id) REFERENCES kinofill.Users(user_id),
    UNIQUE(nickname),
    CHECK(birth_date < CURRENT_DATE)
);

CREATE TABLE kinofill.Viewers(
    viewer_id integer PRIMARY KEY,
    is_public char(1) NOT NULL,
    nickname varchar(30),
    FOREIGN KEY(viewer_id) REFERENCES kinofill.Users(user_id),
    CHECK(is_public in ('t', 'f')),
    CHECK(((is_public in ('t')) and (nickname is NOT NULL)) or ((is_public in ('f')) and (nickname is NULL)))
);

CREATE OR REPLACE PROCEDURE kinofill.newUser(
  login VARCHAR(20),
  password_hash VARCHAR(128),
  join_date DATE,
  description TEXT,
  active CHAR(1),
  user_type CHAR(1), -- User
  nickname VARCHAR(30),
  country VARCHAR(30),
  creation_date DATE, -- Studio
  firstname VARCHAR(20),
  surname VARCHAR(20),
  birth_date DATE, -- Journalist
  is_public CHAR(1) -- Viewer
)
AS $$
DECLARE
  user_id kinofill.Users.user_id%TYPE;
BEGIN
  SELECT nextval('kinofill.users_id_seq') INTO user_id;
  INSERT INTO kinofill.Users VALUES (user_id, login, password_hash, join_date, description, active, user_type);
  IF user_type = 'w' THEN
    INSERT INTO kinofill.Viewers VALUES (user_id, is_public, nickname);
  ELSIF user_type = 'd' THEN
    INSERT INTO kinofill.Journalists VALUES (user_id, nickname, firstname, surname, birth_date);
  ELSIF user_type = 's' THEN
    INSERT INTO kinofill.Studios VALUES (user_id, nickname, country, creation_date);
  END IF;
end;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION kinofill.xor3(a int, b int, c int)
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


CREATE TABLE kinofill.Reviews(
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
    CHECK(kinofill.xor3(movie_id, series_id, actor_id)),
    FOREIGN KEY(viewer_id) REFERENCES kinofill.Viewers(viewer_id),
    FOREIGN KEY(journalist_id) REFERENCES kinofill.Journalists(journalist_id),
    FOREIGN KEY(movie_id) REFERENCES kinofill.Movies(movie_id),
    FOREIGN KEY(series_id) REFERENCES kinofill.Series(series_id),
    FOREIGN KEY(actor_id) REFERENCES kinofill.Actors(actor_id),
    CHECK((viewers_rating >= 1) and (viewers_rating <= 5))
);

CREATE TABLE kinofill.News(
    news_id serial PRIMARY KEY,
    title varchar(30) NOT NULL,
    content text NOT NULL,
    publication_date date default CURRENT_DATE NOT NULL,
    journalist_id integer,
    studio_id integer,
    FOREIGN KEY(journalist_id) REFERENCES kinofill.Journalists(journalist_id),
    FOREIGN KEY(studio_id) REFERENCES kinofill.Studios(studio_id),
    CHECK((studio_id is NOT NULL AND journalist_id is NULL) OR (studio_id is NULL AND journalist_id is NOT NULL)),
    CHECK(publication_date <= CURRENT_DATE),
    UNIQUE(title, content, publication_date)
);

CREATE TABLE kinofill.Movie_Characters(
    character_id serial PRIMARY KEY,
    character_name varchar(30) NOT NULL,
    movie_id integer NOT NULL,
    actor_id integer NOT NULL,
    FOREIGN KEY(movie_id) REFERENCES kinofill.Movies(movie_id),
    FOREIGN KEY(actor_id) REFERENCES kinofill.Actors(actor_id),
    UNIQUE(character_name, movie_id, actor_id)
);

CREATE TABLE kinofill.Series_Characters(
    character_id serial PRIMARY KEY,
    character_name varchar(30) NOT NULL,
    series_id integer NOT NULL,
    actor_id integer NOT NULL,
    FOREIGN KEY(series_id) REFERENCES kinofill.Series(series_id),
    FOREIGN KEY(actor_id) REFERENCES kinofill.Actors(actor_id),
    UNIQUE(character_name, series_id, actor_id)
);

CREATE TABLE kinofill.Genres(
    genre varchar(20) PRIMARY KEY
);

CREATE TABLE kinofill.Movie_genres(
    genre varchar(20),
    movie_id integer,
    PRIMARY KEY(genre, movie_id),
    FOREIGN KEY(genre) REFERENCES kinofill.Genres(genre),
    FOREIGN KEY(movie_id) REFERENCES kinofill.Movies(movie_id)
);

CREATE TABLE kinofill.Series_genres(
    genre varchar(20),
    series_id integer,
    PRIMARY KEY(genre, series_id),
    FOREIGN KEY(genre) REFERENCES kinofill.Genres(genre),
    FOREIGN KEY(series_id) REFERENCES kinofill.Series(series_id)
);

CREATE TABLE kinofill.Journalists_reviews_ratings(
    viewers_rating integer not null,
    review_id integer not null,
    viewer_id integer not null,
    PRIMARY KEY(review_id, viewer_id),
    FOREIGN KEY(viewer_id) REFERENCES kinofill.Viewers(viewer_id),
    FOREIGN KEY(review_id) REFERENCES kinofill.Reviews(review_id),
    CHECK(viewers_rating = -1 OR viewers_rating = 1)
);

CREATE OR REPLACE FUNCTION kinofill.mean_rate(pMovieId integer)
RETURNS numeric(3, 2) AS $$
DECLARE
	vRatingMean numeric(3, 2);
BEGIN
	SELECT ROUND( AVG(rate)::numeric, 2 )
	INTO vRatingMean
	FROM kinofill.Reviews
	WHERE movie_id = pMovieId;

	RETURN vRatingMean;
END;
$$ LANGUAGE plpgsql;


-- sample inserts
-- insert into kinofill.Users (login, password_hash, user_type) values ('label', 'xyz', 's');
-- insert into kinofill.Users (login, password_hash, user_type) values ('viewer', 'xyz', 'w');
-- insert into kinofill.Users (login, password_hash, user_type) values ('journalist', 'xyz', 'd');

-- insert into kinofill.Studios (studio_id, name) values (1, 'studio1');

-- insert into kinofill.Viewers (viewer_id, is_public, nickname) values (2, 't','viewer1');

-- insert into kinofill.Journalists (journalist_id, nickname) values (3, 'journalist1');

-- insert into kinofill.Directors (name, surname, birth_date) values ('janusz','iksinski','1988-02-02');

-- insert into kinofill.Movies (name, creation_year, length, studio_id, director_id) values ('Lefleur', 1998, 122, 1, 1);

-- insert into kinofill.Series (name, episodes, seasons, studio_id, director_id) values ('something', 107, 13, 1, 1);

-- insert into kinofill.Actors (name, surname, birth_date) values ('John', 'Doe', '1992-02-12');

-- insert into kinofill.Reviews (rate, author_type, viewer_id, review_object, movie_id) values (5, 'w', 2, 'f', 1);

-- insert into kinofill.News (content, journalist_id) values ('hello', 3);

-- insert into kinofill.Movie_characters (character_name, movie_id, actor_id) values ('batman', 1, 1);

-- insert into kinofill.Series_characters (character_name, series_id, actor_id) values ('hulk', 1, 1);

-- insert into kinofill.Genres (genre) values ('sci-fi');

-- insert into kinofill.Movie_genres (genre, movie_id) values ('sci-fi', 1);

-- insert into kinofill.Series_genres (genre, series_id) values ('sci-fi', 1);

-- insert into kinofill.Journalist_review_viewers_ratings (viewers_rating, review_id, viewer_id) values (1, 1, 2);


--CALL kinofill.newUser(
--  'user123',
--  'password123',
--  '2022-01-01',
--  'I am a new viewer',
--  't',
--  'w',
--  'viewer1',
--  NULL,
--  NULL,
--  NULL,
--  NULL,
--  NULL,
--  't'
--);

-- drop table kinofill.Journalists_reviews_ratings;
-- drop table kinofill.Series_genres;
-- drop table kinofill.Movie_genres;
-- drop table kinofill.Genres;
-- drop table kinofill.Series_Characters;
-- drop table kinofill.Movie_Characters;
-- drop table kinofill.News;
-- drop table kinofill.Reviews;
-- drop table kinofill.Viewers;
-- drop table kinofill.Journalists;
-- drop table kinofill.Actors;
-- drop table kinofill.Series;
-- drop table kinofill.Movies;
-- drop table kinofill.Directors;
-- drop table kinofill.Studios;
-- drop table kinofill.Users;
-- drop function kinofill.xor3;
-- drop function kinofill.mean_rate;
-- drop procedure kinofill.newUser;
-- drop sequence kinofill.users_id_seq;
