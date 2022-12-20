CREATE SEQUENCE filmweb.users_id_seq;


CREATE TABLE filmweb.Uzytkownicy(
    id_uzytkownika integer PRIMARY KEY DEFAULT nextval('filmweb.users_id_seq'),
    login varchar(20) NOT NULL UNIQUE,
    haslo varchar(128) NOT NULL,
    data_dolaczenia date NOT NULL DEFAULT CURRENT_DATE,
    opis_profilu text,
    aktywny char(1) NOT NULL DEFAULT 't',
    typ_uzytkownika char(1) NOT NULL CHECK (typ_uzytkownika IN ('d', 's', 'w')),
    CHECK(data_dolaczenia <= CURRENT_DATE),
    CHECK(aktywny in ('t','n'))
);

CREATE TABLE filmweb.Wytwornie(
    id_wytworni integer PRIMARY KEY,
    nazwa varchar(30) NOT NULL UNIQUE,
    kraj_pochodzenia varchar(20),
    data_zalozenia date,
    ocena_widzow decimal(3, 2),
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Uzytkownicy(id_uzytkownika),
    CHECK(data_zalozenia <= CURRENT_DATE)
);

CREATE TABLE filmweb.Rezyserowie(
    id_rezysera serial PRIMARY KEY,
    imie varchar(20) NOT NULL,
    nazwisko varchar(20) NOT NULL,
    data_urodzenia date NOT NULL,
    kraj_pochodzenia varchar(20),
    ocena decimal(3, 2),
    id_wytworni integer,
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Wytwornie(id_wytworni),
    UNIQUE(imie, nazwisko, data_urodzenia)
);

CREATE TABLE filmweb.Filmy(
    id_filmu serial PRIMARY KEY,
    nazwa varchar(30) NOT NULL,
    rok_produkcji integer NOT NULL,
    dlugosc integer NOT NULL,
    ocena_widzow decimal(3,2),
    id_wytworni integer NOT NULL,
    id_rezysera integer NOT NULL,
    UNIQUE(nazwa, rok_produkcji),
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Wytwornie(id_wytworni),
    FOREIGN KEY(id_rezysera) REFERENCES filmweb.Rezyserowie(id_rezysera),
    CHECK( (CAST (EXTRACT(year from CURRENT_DATE) AS INTEGER) ) >= rok_produkcji),
    CHECK(dlugosc > 0)
);

CREATE TABLE filmweb.Seriale(
    id_serialu serial PRIMARY KEY,
    nazwa varchar(30) NOT NULL,
    liczba_odcinkow integer NOT NULL,
    liczba_sezonow integer NOT NULL,
    ocena_widzow decimal(3,2),
    id_wytworni integer NOT NULL,
    id_rezysera integer NOT NULL,
    UNIQUE(nazwa, liczba_odcinkow),
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Wytwornie(id_wytworni),
    FOREIGN KEY(id_rezysera) REFERENCES filmweb.Rezyserowie(id_rezysera),
    CHECK(liczba_odcinkow >= 0),
    CHECK(liczba_sezonow >= 0),
    CHECK(liczba_odcinkow >= liczba_sezonow),
    CHECK((ocena_widzow >= 1) and (ocena_widzow <= 5))
);

CREATE TABLE filmweb.Aktorzy(
    id_aktora serial PRIMARY KEY,
    imie varchar(20) NOT NULL,
    nazwisko varchar(20) NOT NULL,
    data_urodzenia date NOT NULL,
    kraj_pochodzenia varchar(20),
    ocena decimal(3, 2),
    id_wytworni integer,
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Wytwornie(id_wytworni),
    UNIQUE(imie, nazwisko, data_urodzenia),
    CHECK(data_urodzenia < CURRENT_DATE),
    CHECK((ocena >= 1) and (ocena <= 5))
);


CREATE TABLE filmweb.Dziennikarze(
    id_dziennikarza integer PRIMARY KEY,
    nazwa varchar(20) NOT NULL,
    imie varchar(20),
    nazwisko varchar(20),
    data_urodzenia date,
    FOREIGN KEY(id_dziennikarza) REFERENCES filmweb.Uzytkownicy(id_uzytkownika),
    UNIQUE(nazwa),
    CHECK(data_urodzenia < CURRENT_DATE)
);

CREATE TABLE filmweb.Widzowie(
    id_widza integer PRIMARY KEY,
    czy_publiczny char(1) NOT NULL,
    nazwa varchar(30),
    FOREIGN KEY(id_widza) REFERENCES filmweb.Uzytkownicy(id_uzytkownika),
    CHECK(czy_publiczny in ('t', 'n')),
    CHECK(((czy_publiczny in ('t')) and (nazwa is NOT NULL)) or ((czy_publiczny in ('n')) and (nazwa is NULL)))
);

CREATE OR REPLACE PROCEDURE filmweb.nowyUzytkownik(
  login VARCHAR(20),
  haslo VARCHAR(128),
  data_dolaczenia DATE,
  opis_profilu TEXT,
  aktywny CHAR(1),
  typ_uzytkownika CHAR(1), -- Użytkownik
  nazwa VARCHAR(30),
  kraj_pochodzenia VARCHAR(20),
  data_zalozenia DATE,  -- Wytwórnia
  imie VARCHAR(20),
  nazwisko VARCHAR(20),
  data_urodzenia DATE, -- Dziennikarz
  czy_publiczny CHAR(1) -- Widz
)
AS $$
DECLARE
  id_uzytkownika filmweb.Uzytkownicy.id_uzytkownika%TYPE;
BEGIN
  SELECT nextval('filmweb.users_id_seq') INTO id_uzytkownika;
  INSERT INTO filmweb.Uzytkownicy VALUES (id_uzytkownika, login, haslo, data_dolaczenia, opis_profilu, aktywny, typ_uzytkownika);
  IF typ_uzytkownika = 'w' THEN
    INSERT INTO filmweb.Widzowie VALUES (id_uzytkownika, czy_publiczny, nazwa);
  ELSIF typ_uzytkownika = 'd' THEN
    INSERT INTO filmweb.Dziennikarze VALUES (id_uzytkownika, nazwa, imie, nazwisko, data_urodzenia);
  ELSIF typ_uzytkownika = 's' THEN
    INSERT INTO filmweb.Wytwornie VALUES (id_uzytkownika, nazwa, kraj_pochodzenia, data_zalozenia);
  END IF;
END;
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
END;
$$ LANGUAGE plpgsql;


CREATE TABLE filmweb.Recenzje(
    id_recenzji serial PRIMARY KEY,
    ocena integer NOT NULL,
    data date default CURRENT_DATE NOT NULL,
    tresc text,
    typ_autora char(1) NOT NULL,
    id_widza integer,
    id_dziennikarza integer,
    obiekt_recenzji char(1) NOT NULL,
    id_filmu integer,
    id_serialu integer,
    id_aktora integer,
    ocena_widzow decimal(3,2),
    CHECK(typ_autora IN ('w','d')),
    CHECK((id_widza is NOT NULL AND id_dziennikarza is NULL) OR (id_widza is NULL AND id_dziennikarza is NOT NULL)),
    CHECK(((typ_autora IN ('w')) AND (id_widza IS NOT NULL)) or (typ_autora IN ('d') AND (id_dziennikarza is NOT NULL))),
    CHECK(obiekt_recenzji IN ('f','s','a')),
    CHECK(xor3(id_filmu, id_serialu, id_aktora)),
    FOREIGN KEY(id_widza) REFERENCES filmweb.Widzowie(id_widza),
    FOREIGN KEY(id_dziennikarza) REFERENCES filmweb.Dziennikarze(id_dziennikarza),
    FOREIGN KEY(id_filmu) REFERENCES filmweb.Filmy(id_filmu),
    FOREIGN KEY(id_serialu) REFERENCES filmweb.Seriale(id_serialu),
    FOREIGN KEY(id_aktora) REFERENCES filmweb.Aktorzy(id_aktora),
    CHECK((ocena_widzow >= 1) and (ocena_widzow <= 5))
);

CREATE TABLE filmweb.Newsy(
    id_newsa serial PRIMARY KEY,
    tresc text NOT NULL,
    data_publikacji date default CURRENT_DATE NOT NULL,
    id_dziennikarza integer,
    id_wytworni integer,
    FOREIGN KEY(id_dziennikarza) REFERENCES filmweb.Dziennikarze(id_dziennikarza),
    FOREIGN KEY(id_wytworni) REFERENCES filmweb.Wytwornie(id_wytworni),
    CHECK((id_wytworni is NOT NULL AND id_dziennikarza is NULL) OR (id_wytworni is NULL AND id_dziennikarza is NOT NULL)),
    CHECK(data_publikacji <= CURRENT_DATE)
);

CREATE TABLE filmweb.Postacie_filmowe(
    id_postaci serial PRIMARY KEY,
    nazwa_postaci varchar(30) NOT NULL,
    id_filmu integer NOT NULL,
    id_aktora integer NOT NULL,
    FOREIGN KEY(id_filmu) REFERENCES filmweb.Filmy(id_filmu),
    FOREIGN KEY(id_aktora) REFERENCES filmweb.Aktorzy(id_aktora),
    UNIQUE(nazwa_postaci, id_filmu, id_aktora)
);

CREATE TABLE filmweb.Postacie_serialowe(
    id_postaci serial PRIMARY KEY,
    nazwa_postaci varchar(30) NOT NULL,
    id_serialu integer NOT NULL,
    id_aktora integer NOT NULL,
    FOREIGN KEY(id_serialu) REFERENCES filmweb.Seriale(id_serialu),
    FOREIGN KEY(id_aktora) REFERENCES filmweb.Aktorzy(id_aktora),
    UNIQUE(nazwa_postaci, id_serialu, id_aktora)
);

CREATE TABLE filmweb.Gatunki(
    nazwa varchar(20) PRIMARY KEY
);

CREATE TABLE filmweb.Gatunki_filmu(
    nazwa varchar(20),
    id_filmu integer,
    PRIMARY KEY(nazwa, id_filmu),
    FOREIGN KEY(nazwa) REFERENCES filmweb.Gatunki(nazwa),
    FOREIGN KEY(id_filmu) REFERENCES filmweb.Filmy(id_filmu)
);

CREATE TABLE filmweb.Gatunki_serialu(
    nazwa varchar(20),
    id_serialu integer,
    PRIMARY KEY(nazwa, id_serialu),
    FOREIGN KEY(nazwa) REFERENCES filmweb.Gatunki(nazwa),
    FOREIGN KEY(id_serialu) REFERENCES filmweb.Seriale(id_serialu)
);

CREATE TABLE filmweb.Oceny_recenzji_dziennikarzy(
    ocena_widza integer not null,
    id_recenzji integer not null,
    id_widza integer not null,
    PRIMARY KEY(id_recenzji, id_widza),
    FOREIGN KEY(id_widza) REFERENCES filmweb.Widzowie(id_widza),
    FOREIGN KEY(id_recenzji) REFERENCES filmweb.Recenzje(id_recenzji),
    CHECK(ocena_widza <= 5 AND ocena_widza >= 1)
);



-- sample inserts
insert into filmweb.Uzytkownicy (login, haslo, typ_uzytkownika) values ('wytwornia', 'xyz', 's');
insert into filmweb.Uzytkownicy (login, haslo, typ_uzytkownika) values ('widz', 'xyz', 'w');
insert into filmweb.Uzytkownicy (login, haslo, typ_uzytkownika) values ('dziennikarz', 'xyz', 'd');

insert into filmweb.Wytwornie (id_wytworni, nazwa) values (1, 'wywtornia1');

insert into filmweb.Widzowie (id_widza, czy_publiczny, nazwa) values(2, 't','widz1');

insert into filmweb.Dziennikarze (id_dziennikarza, nazwa) values (3, 'dziennikarz1');

insert into filmweb.Rezyserowie (imie, nazwisko, data_urodzenia)
	values('janusz','iksinski','1988-02-02');

insert into filmweb.Filmy (nazwa, rok_produkcji, dlugosc, id_wytworni, id_rezysera)
	values('Le-fleur', 1998, 122, 1, 1);

insert into filmweb.Seriale (nazwa, liczba_odcinkow, liczba_sezonow, id_wytworni, id_rezysera)
	values('jakistam', 107, 13, 1, 1);

insert into filmweb.Aktorzy (imie, nazwisko, data_urodzenia) values ('John', 'Doe', '1992-02-12');

insert into filmweb.Recenzje (ocena, typ_autora, id_widza, obiekt_recenzji, id_filmu)
					values (5, 'w', 2, 'f', 1);

insert into filmweb.Newsy (tresc, id_dziennikarza) values('siema', 3);

insert into filmweb.Postacie_filmowe (nazwa_postaci, id_filmu, id_aktora) values ('batman', 1, 1);

insert into filmweb.Postacie_serialowe (nazwa_postaci, id_serialu, id_aktora) values ('hulk', 1, 1);

insert into filmweb.Gatunki (nazwa) values ('sci-fi');

insert into filmweb.Gatunki_filmu (nazwa, id_filmu) values ('sci-fi', 1);

insert into filmweb.Gatunki_serialu (nazwa, id_serialu) values ('sci-fi', 1);

insert into filmweb.Oceny_recenzji_dziennikarzy (ocena_widza, id_recenzji, id_widza) values (1, 1, 2);


CALL filmweb.nowyUzytkownik(
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


drop table filmweb.Oceny_recenzji_dziennikarzy;
drop table filmweb.Gatunki_serialu;
drop table filmweb.Gatunki_filmu;
drop table filmweb.Gatunki;
drop table filmweb.Postacie_serialowe;
drop table filmweb.Postacie_filmowe;
drop table filmweb.Newsy;
drop table filmweb.Recenzje;
drop table filmweb.Widzowie;
drop table filmweb.Dziennikarze;
drop table filmweb.Aktorzy;
drop table filmweb.Seriale;
drop table filmweb.Filmy;
drop table filmweb.Rezyserowie;
drop table filmweb.Wytwornie;
drop table filmweb.Uzytkownicy;
drop function filmweb.xor3;
drop procedure filmweb.nowyUzytkownik;
