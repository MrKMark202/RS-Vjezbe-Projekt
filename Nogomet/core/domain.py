#Nogomet/core/domain.py

from typing import TypedDict


# MODELI PODATAKA (tipovi, čisto za preglednost)

class Liga(TypedDict):
    id: int
    naziv: str


class Klub(TypedDict):
    id: int
    naziv: str
    liga_id: int


class Utakmica(TypedDict):
    id: int
    liga_id: int
    domaci_id: int
    gosti_id: int
    domaci_goals: int
    gosti_goals: int


# KONSTANTE ZA BODOVANJE

POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0