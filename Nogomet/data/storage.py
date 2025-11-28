# Nogomet/data/storage.py

import json
from pathlib import Path

from Nogomet.config import DB_FILE

DEFAULT_DB = {
    "lige": [],
    "klubovi": [],
    "utakmice": []
}


def load_db() -> dict:
    path = Path(DB_FILE)

    if not path.exists():
        return {
            "lige": [],
            "klubovi": [],
            "utakmice": []
        }

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "lige" not in data:
        data["lige"] = []
    if "klubovi" not in data:
        data["klubovi"] = []
    if "utakmice" not in data:
        data["utakmice"] = []

    return data


def save_db(db: dict) -> None:
    path = Path(DB_FILE)

    with path.open("w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
