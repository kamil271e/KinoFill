CREATE TABLE Uzytkownicy(
    id_uzytkownika serial PRIMARY KEY,
    login varchar(20) NOT NULL UNIQUE,
    haslo varchar(20) NOT NULL,
    data_dolaczenia date NOT NULL DEFAULT CURRENT_DATE,
    opis_profilu text,
    typ_uzytkownika char(1) NOT NULL CHECK (typ_uzytkownika IN ('d', 's', 'w'))
);

CREATE TABLE Wytwornie(
    id_wytworni serial PRIMARY KEY,
    nazwa varchar(30) NOT NULL UNIQUE,
    kraj_pochodzenia varchar(20),
    data_zalozenia date,
    ocena_widzow decimal(3, 2),
    FOREIGN KEY(id_wytworni) REFERENCES Uzytkownicy(id_uzytkownika)
);

CREATE TABLE Rezyserowie(
    id_rezysera serial PRIMARY KEY,
    imie varchar(20) NOT NULL,
    nazwisko varchar(20) NOT NULL,
    data_urodzenia date NOT NULL,
    kraj_pochodzenia varchar(20),
    ocena decimal(3, 2),
    id_wytworni integer,
    FOREIGN KEY(id_wytworni) REFERENCES Wytwornie(id_wytworni),
    UNIQUE(imie, nazwisko, data_urodzenia)
);

CREATE TABLE Filmy(
    id_filmu serial PRIMARY KEY,
    nazwa varchar(30) NOT NULL,
    rok_produkcji integer NOT NULL,
    dlugosc integer NOT NULL,
    ocena_widzow decimal(3,2),
    id_wytworni integer NOT NULL,
    id_rezysera integer NOT NULL,
    UNIQUE(nazwa, rok_produkcji),
    FOREIGN KEY(id_wytworni) REFERENCES Wytwornie(id_wytworni),
    FOREIGN KEY(id_rezysera) REFERENCES Rezyserowie(id_rezysera)
);

CREATE TABLE Seriale(
    id_serialu serial PRIMARY KEY,
    nazwa varchar(30) NOT NULL,
    liczba_odcinkow integer NOT NULL,
    liczba_sezonow integer NOT NULL,
    ocena_widzow decimal(3,2),
    id_wytworni integer NOT NULL,
    id_rezysera integer NOT NULL,
    UNIQUE(nazwa, liczba_odcinkow),
    FOREIGN KEY(id_wytworni) REFERENCES Wytwornie(id_wytworni),
    FOREIGN KEY(id_rezysera) REFERENCES Rezyserowie(id_rezysera)
);

CREATE TABLE Aktorzy(
    id_aktora serial PRIMARY KEY,
    imie varchar(20) NOT NULL,
    nazwisko varchar(20) NOT NULL,
    data_urodzenia date NOT NULL,
    kraj_pochodzenia varchar(20),
    ocena decimal(3, 2),
    id_wytworni integer,
    FOREIGN KEY(id_wytworni) REFERENCES Wytwornie(id_wytworni),
    UNIQUE(imie, nazwisko, data_urodzenia)
);

CREATE TABLE Dziennikarze(
    id_dziennikarza serial PRIMARY KEY,
    nazwa varchar(20) NOT NULL,
    imie varchar(20),
    nazwisko varchar(20),
    data_urodzenia date,
    FOREIGN KEY(id_dziennikarza) REFERENCES Uzytkownicy(id_uzytkownika),
    UNIQUE(nazwa)
);

CREATE TABLE Widzowie(
    id_widza serial PRIMARY KEY,
    czy_publiczny char(1) NOT NULL,
    nazwa varchar(30),
    FOREIGN KEY(id_widza) REFERENCES Uzytkownicy(id_uzytkownika)
);

CREATE OR REPLACE FUNCTION xor3(a int, b int, c int)
RETURNS boolean AS $$
BEGIN
  -- Check if exactly one of the input values is NOT NULL
  IF (a IS NOT NULL AND b IS NULL AND c IS NULL) OR
     (a IS NULL AND b IS NOT NULL AND c IS NULL) OR
     (a IS NULL AND b IS NULL AND c IS NOT NULL) THEN
    -- Return true if exactly one input value is NOT NULL
    RETURN true;
  ELSE
    -- Return false if zero or more than one input values are NOT NULL
    RETURN false;
  END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TABLE Recenzje(
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
    CHECK( (id_widza is NOT NULL AND id_dziennikarza is NULL) OR (id_widza is NULL AND id_dziennikarza is NOT NULL)),
    CHECK(obiekt_recenzji IN ('f','s','a')),
    CHECK( xor3(id_filmu, id_serialu, id_aktora) ),
    FOREIGN KEY(id_widza) REFERENCES Widzowie(id_widza),
    FOREIGN KEY(id_dziennikarza) REFERENCES Dziennikarze(id_dziennikarza),
    FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu),
    FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu),
    FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora)
);

CREATE TABLE Newsy(
    id_newsa serial PRIMARY KEY,
    tresc text NOT NULL,
    data_publikacji date default CURRENT_DATE NOT NULL,
    id_dziennikarza integer,
    id_wytworni integer,
    FOREIGN KEY(id_dziennikarza) REFERENCES Dziennikarze(id_dziennikarza),
    FOREIGN KEY(id_wytworni) REFERENCES Wytwornie(id_wytworni),
    CHECK( (id_wytworni is NOT NULL AND id_dziennikarza is NULL) OR (id_wytworni is NULL AND id_dziennikarza is NOT NULL) )
);

CREATE TABLE Postacie_filmowe(
    id_postaci serial PRIMARY KEY,
    nazwa_postaci varchar(30) NOT NULL,
    id_filmu integer NOT NULL,
    id_aktora integer NOT NULL,
    FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu),
    FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora),
    UNIQUE(nazwa_postaci, id_filmu, id_aktora)
);

CREATE TABLE Postacie_serialowe(
    id_postaci serial PRIMARY KEY,
    nazwa_postaci varchar(30) NOT NULL,
    id_serialu integer NOT NULL,
    id_aktora integer NOT NULL,
    FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu),
    FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora),
    UNIQUE(nazwa_postaci, id_serialu, id_aktora)
);

CREATE TABLE Gatunki(
    nazwa varchar(20) PRIMARY KEY
);

CREATE TABLE Gatunki_filmu(
    nazwa varchar(20),
    id_filmu integer,
    PRIMARY KEY(nazwa, id_filmu),
    FOREIGN KEY(nazwa) REFERENCES Gatunki(nazwa),
    FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu)
);

CREATE TABLE Gatunki_serialu(
    nazwa varchar(20),
    id_serialu integer,
    PRIMARY KEY(nazwa, id_serialu),
    FOREIGN KEY(nazwa) REFERENCES Gatunki(nazwa),
    FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu)
);

CREATE TABLE Oceny_recenzji_dziennikarzy(
    ocena_widza integer not null,
    id_recenzji integer not null,
    id_widza integer not null,
    PRIMARY KEY(id_recenzji, id_widza),
    FOREIGN KEY(id_widza) REFERENCES Widzowie(id_widza),
    FOREIGN KEY(id_recenzji) REFERENCES Recenzje(id_recenzji),
    CHECK(ocena_widza < 6 AND ocena_widza > 0)
);
