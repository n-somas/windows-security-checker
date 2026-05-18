from pathlib import Path


STATUS_OK = "OK"
STATUS_INFO = "INFO"
STATUS_WARNUNG = "WARNUNG"
STATUS_KRITISCH = "KRITISCH"
STATUS_FEHLER = "FEHLER"


# constants.py liegt in src/core/
# parent.parent.parent führt zurück zum Projektordner.
PROJEKT_ORDNER = Path(__file__).resolve().parent.parent.parent

BERICHTE_ORDNER = PROJEKT_ORDNER / "reports"
