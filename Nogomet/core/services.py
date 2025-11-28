# Nogomet/core/services.py

from typing import List, Dict

from Nogomet.data.storage import load_db, save_db
from Nogomet.core.domain import (
    Liga,
    Klub,
    Utakmica,
    POINTS_WIN,
    POINTS_DRAW,
    POINTS_LOSS,
)



#   POMOĆNA FUNKCIJA ZA ID-jeve
# -------------------------------

def sljedeci_id(items: List[Dict]) -> int:

    if not items:
        return 1
    max_id = max(item["id"] for item in items)
    return max_id + 1



#            LIGE
# ==============================

def dohvati_sve_lige() -> List[Liga]:

    db = load_db()
    return db["lige"]


def kreiraj_ligu(naziv: str) -> Liga:

    db = load_db()
    lige: List[Liga] = db["lige"]

    novi_id = sljedeci_id(lige)
    liga: Liga = {
        "id": novi_id,
        "naziv": naziv,
    }

    lige.append(liga)
    save_db(db)
    return liga


def obrisi_ligu(liga_id: int) -> None:

    db = load_db()

    # obriši ligu
    db["lige"] = [
        liga for liga in db["lige"]
        if liga["id"] != liga_id
    ]

    # obriši klubove te lige
    db["klubovi"] = [
        klub for klub in db["klubovi"]
        if klub["liga_id"] != liga_id
    ]

    # obriši utakmice te lige
    db["utakmice"] = [
        utakmica for utakmica in db["utakmice"]
        if utakmica["liga_id"] != liga_id
    ]

    save_db(db)



#           KLUBOVI
# ==============================

def dohvati_klubove_za_ligu(liga_id: int) -> List[Klub]:

    db = load_db()
    return [
        klub for klub in db["klubovi"]
        if klub["liga_id"] == liga_id
    ]


def kreiraj_klub(liga_id: int, naziv: str) -> Klub:

    db = load_db()
    klubovi: List[Klub] = db["klubovi"]

    novi_id = sljedeci_id(klubovi)
    klub: Klub = {
        "id": novi_id,
        "naziv": naziv,
        "liga_id": liga_id,
    }

    klubovi.append(klub)
    save_db(db)
    return klub


def obrisi_klub(klub_id: int) -> None:

    db = load_db()

    # obriši klub
    db["klubovi"] = [
        klub for klub in db["klubovi"]
        if klub["id"] != klub_id
    ]

    # obriši utakmice gdje je klub domaćin ili gost
    db["utakmice"] = [
        utakmica for utakmica in db["utakmice"]
        if utakmica["domaci_id"] != klub_id and utakmica["gosti_id"] != klub_id
    ]

    save_db(db)



#           UTAKMICE
# ==============================

def dohvati_utakmice_za_ligu(liga_id: int) -> List[Utakmica]:

    db = load_db()
    return [
        utakmica for utakmica in db["utakmice"]
        if utakmica["liga_id"] == liga_id
    ]


def kreiraj_utakmicu(
    liga_id: int,
    domaci_id: int,
    gosti_id: int,
    domaci_goals: int,
    gosti_goals: int,
) -> Utakmica:

    if domaci_id == gosti_id:
        raise ValueError("Domaćin i gost ne mogu biti isti klub.")

    db = load_db()
    utakmice: List[Utakmica] = db["utakmice"]

    novi_id = sljedeci_id(utakmice)
    utakmica: Utakmica = {
        "id": novi_id,
        "liga_id": liga_id,
        "domaci_id": domaci_id,
        "gosti_id": gosti_id,
        "domaci_goals": domaci_goals,
        "gosti_goals": gosti_goals,
    }

    utakmice.append(utakmica)
    save_db(db)
    return utakmica


#           TABLICA
# ==============================

def dohvati_tablicu(liga_id: int) -> List[Dict]:
    
    db = load_db()

    # klubovi u toj ligi
    klubovi = [
        klub for klub in db["klubovi"]
        if klub["liga_id"] == liga_id
    ]

    # utakmice u toj ligi
    utakmice = [
        utakmica for utakmica in db["utakmice"]
        if utakmica["liga_id"] == liga_id
    ]

    # inicijalna statistika
    stats: Dict[int, Dict] = {}
    for klub in klubovi:
        stats[klub["id"]] = {
            "klub_id": klub["id"],
            "klub_naziv": klub["naziv"],
            "odigrane": 0,
            "pobjede": 0,
            "nerjesene": 0,
            "porazi": 0,
            "golovi_dani": 0,
            "golovi_primljeni": 0,
            "gol_razlika": 0,
            "bodovi": 0,
        }

    # prolaz kroz sve utakmice
    for utakmica in utakmice:
        domaci_id = utakmica["domaci_id"]
        gosti_id = utakmica["gosti_id"]
        domaci_goals = utakmica["domaci_goals"]
        gosti_goals = utakmica["gosti_goals"]

        if domaci_id not in stats or gosti_id not in stats:
            # zaštita ako su podaci nekonzistentni
            continue

        domaci = stats[domaci_id]
        gosti = stats[gosti_id]

        # odigrane
        domaci["odigrane"] += 1
        gosti["odigrane"] += 1

        # golovi
        domaci["golovi_dani"] += domaci_goals
        domaci["golovi_primljeni"] += gosti_goals

        gosti["golovi_dani"] += gosti_goals
        gosti["golovi_primljeni"] += domaci_goals

        # gol razlika
        domaci["gol_razlika"] = domaci["golovi_dani"] - domaci["golovi_primljeni"]
        gosti["gol_razlika"] = gosti["golovi_dani"] - gosti["golovi_primljeni"]

        # bodovi + W/D/L
        if domaci_goals > gosti_goals:
            # domaćin pobijedio
            domaci["pobjede"] += 1
            domaci["bodovi"] += POINTS_WIN

            gosti["porazi"] += 1
            gosti["bodovi"] += POINTS_LOSS

        elif domaci_goals < gosti_goals:
            # gosti pobijedili
            gosti["pobjede"] += 1
            gosti["bodovi"] += POINTS_WIN

            domaci["porazi"] += 1
            domaci["bodovi"] += POINTS_LOSS

        else:
            # neriješeno
            domaci["nerjesene"] += 1
            gosti["nerjesene"] += 1

            domaci["bodovi"] += POINTS_DRAW
            gosti["bodovi"] += POINTS_DRAW

    # dict -> lista
    tablica = list(stats.values())

    # sortiranje: bodovi DESC, gol_razlika DESC, golovi_dani DESC, naziv ASC
    tablica.sort(
        key=lambda red: (
            -red["bodovi"],
            -red["gol_razlika"],
            -red["golovi_dani"],
            red["klub_naziv"].lower(),
        )
    )

    return tablica