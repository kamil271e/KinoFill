CREATE TABLE Uzytkownicy(
    login varchar(20) not null,
    haslo varchar(20) not null,
    opis_profilu clob,
    typ_uzytkownika char(1) not null,
    CONSTRAINT pk_uzytkownik PRIMARY KEY(login),
    CONSTRAINT chk_typ_uzytkownika check(typ_uzytkownika in ('f', 'w', 'd'))
    -- f - wytowrnia filmowa
);

CREATE TABLE Wytwornie(
    nazwa varchar(30) not null,
    kraj_pochodzenia varchar(20),
    data_zalozenia date,
    ocena_widzow number(3,2),
    login varchar(20) not null,
    CONSTRAINT fk_wytwornia_uzytkownik FOREIGN KEY(login) REFERENCES Uzytkownicy(login),
    CONSTRAINT pk_wytwornia PRIMARY KEY(nazwa)
);

CREATE TABLE Rezyserowie(
    id_rezysera number(4) not null,
    imie varchar(20) not null,
    nazwisko varchar(20) not null,
    data_urodzenia date not null,
    kraj_pochodzenia varchar(20),
    ocena number(3,2),
    nazwa_wytworni varchar(30),
    CONSTRAINT fk_rezyser_wytwornia FOREIGN KEY(nazwa_wytworni) REFERENCES Wytwornie(nazwa),
    CONSTRAINT pk_rezyser PRIMARY KEY(id_rezysera),
    CONSTRAINT uk_rezyser UNIQUE (imie, nazwisko, data_urodzenia)
);

CREATE TABLE Filmy(
    id_filmu number(4) not null,
    nazwa varchar(30) not null,
    rok_produkcji number(4) not null,
    dlugosc number(3) not null,
    ocena_widzow number(3,2),
    nazwa_wytworni varchar(30) not null,
    id_rezysera number(4) not null,
    CONSTRAINT pk_film PRIMARY KEY(id_filmu),
    CONSTRAINT uk_film UNIQUE (nazwa, rok_produkcji),
    CONSTRAINT fk_film_wytwornia FOREIGN KEY(nazwa_wytworni) REFERENCES Wytwornie(nazwa),
    CONSTRAINT fk_film_rezyser FOREIGN KEY(id_rezysera) REFERENCES Rezyserowie(id_rezysera)
);

CREATE TABLE Seriale(
    id_serialu number(4) not null,
    nazwa varchar(30) not null,
    liczba_odcinkow number(4) not null,
    liczba_sezonow number(2) not null,
    ocena_widzow number(3,2),
    nazwa_wytworni varchar(30) not null,
    id_rezysera number(4) not null,
    CONSTRAINT pk_serial PRIMARY KEY(id_serialu),
    CONSTRAINT uk_serial UNIQUE (nazwa, liczba_odcinkow),
    CONSTRAINT fk_serial_wytwornia FOREIGN KEY(nazwa_wytworni) REFERENCES Wytwornie(nazwa),
    CONSTRAINT fk_serial_rezyser FOREIGN KEY(id_rezysera) REFERENCES Rezyserowie(id_rezysera)
);


CREATE TABLE Aktorzy(
    id_aktora number(4) not null,
    imie varchar(20) not null,
    nazwisko varchar(20) not null,
    data_urodzenia date not null,
    kraj_pochodzenia varchar(20),
    ocena number(3,2),
    nazwa_wytworni varchar(30),
    CONSTRAINT pk_aktor PRIMARY KEY(id_aktora),
    CONSTRAINT fk_aktor_wytwornia FOREIGN KEY(nazwa_wytworni) REFERENCES Wytwornie(nazwa),
    CONSTRAINT uk_aktor UNIQUE (imie, nazwisko, data_urodzenia)
);


CREATE TABLE Dziennikarze(
    nazwa varchar(20) not null,
    imie varchar(20) not null,
    nazwisko varchar(20) not null,
    login varchar(20) not null,
    CONSTRAINT pk_dziennikarz PRIMARY KEY(nazwa),
    CONSTRAINT fk_dziennikarz_uzytkownik FOREIGN KEY(login) REFERENCES Uzytkownicy(login)
);


CREATE TABLE Widzowie(
    id_widza number(4) not null,
    data_dolaczenia date default CURRENT_DATE not null,
    czy_publiczny char(1) not null,
    nazwa varchar(30),
    login varchar(20) not null,
    CONSTRAINT pk_widz PRIMARY KEY(id_widza),
    CONSTRAINT fk_widz_uzytkownik FOREIGN KEY(login) REFERENCES Uzytkownicy(login)
);

CREATE TABLE Recenzje(
    id_recenzji NUMBER(4) not null,
    ocena NUMBER(1) not null,
    data date default CURRENT_DATE not null,
    tresc clob,
    typ_autora char(1) not null,
    obiekt_recenzji char(1) not null,
    id_widza number(4),
    nazwa_dziennikarza varchar(20),
    id_filmu number(4),
    id_serialu number(4),
    id_aktora number(4),
    ocena_widzow number(3,2),
    CONSTRAINT pk_recenzje PRIMARY KEY(id_recenzji),
    CONSTRAINT chk_typ_autora check(typ_autora in ('w','d')),
    CONSTRAINT chk_obiekt_recenzji check(obiekt_recenzji in ('f','s','a')),
    CONSTRAINT fk_recenzja_widz FOREIGN KEY(id_widza) REFERENCES Widzowie(id_widza),
    CONSTRAINT fk_recenzja_dziennikarz FOREIGN KEY(nazwa_dziennikarza) REFERENCES Dziennikarze(nazwa),
    CONSTRAINT fk_recenzja_film FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu),
    CONSTRAINT fk_recenzja_serial FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu),
    CONSTRAINT fk_recenzja_aktor FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora),
    CONSTRAINT chk_autor check(((id_widza is null) or (nazwa_dziennikarza is null)) and (not ((id_widza is null) and (nazwa_dziennikarza is null))))
    --CONSTRAINT chk_autor check(XOR(id_widza is null, nazwa_dziennikarza is null)),
    --CONSTRAINT chk_obiekt_recenzji check(XOR(id_filmu is null, id_serialu is null, id_aktora is null))
);



CREATE TABLE Newsy(
    id_newsa number(4) not null,
    tresc clob not null,
    data_publikacji date not null,
    nazwa_dziennikarza varchar(20),
    nazwa_wytworni varchar(30),
    CONSTRAINT fk_news_dziennikarz FOREIGN KEY(nazwa_dziennikarza) REFERENCES Dziennikarze(nazwa),
    CONSTRAINT fk_news_wytwornia FOREIGN KEY(nazwa_wytworni) REFERENCES Wytwornie(nazwa),
    CONSTRAINT pk_news PRIMARY KEY(id_newsa)
    --CONSTRAINT chk_autor check(XOR(nazwa_wytworni is null, nazwa_dziennikarza is null))
);


CREATE TABLE Postacie_filmowe(
    id_postaci number(4) not null,
    nazwa_postaci varchar(30) not null,
    id_filmu number(4) not null,
    id_aktora number(4) not null,
    CONSTRAINT pk_postac_f PRIMARY KEY(id_postaci),
    CONSTRAINT fk_postac_f_film FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu),
    CONSTRAINT fk_postac_f_aktor FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora)
);


CREATE TABLE Postacie_serialowe(
    id_postaci number(4) not null,
    nazwa_postaci varchar(30) not null,
    id_serialu number(4) not null,
    id_aktora number(4) not null,
    CONSTRAINT pk_postac_s PRIMARY KEY(id_postaci),
    CONSTRAINT fk_postac_s_serial FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu),
    CONSTRAINT fk_postac_s_aktor FOREIGN KEY(id_aktora) REFERENCES Aktorzy(id_aktora)
);


CREATE TABLE Gatunki(
    nazwa varchar(20) not null,
    CONSTRAINT pk_gatunek PRIMARY KEY(nazwa)
);


CREATE TABLE Gatunki_filmu(
    nazwa varchar(20) not null,
    id_filmu number(4) not null,
    CONSTRAINT pk_gatunek_filmu PRIMARY KEY(nazwa, id_filmu),
    CONSTRAINT fk_gatunek_f FOREIGN KEY(nazwa) REFERENCES Gatunki(nazwa),
    CONSTRAINT fk_film FOREIGN KEY(id_filmu) REFERENCES Filmy(id_filmu)
);

CREATE TABLE Gatunki_serialu(
    nazwa varchar(20) not null,
    id_serialu number(4) not null,
    CONSTRAINT pk_gatunek_serialu PRIMARY KEY(nazwa, id_serialu),
    CONSTRAINT fk_gatunek_s FOREIGN KEY(nazwa) REFERENCES Gatunki(nazwa),
    CONSTRAINT fk_serial FOREIGN KEY(id_serialu) REFERENCES Seriale(id_serialu)
);
