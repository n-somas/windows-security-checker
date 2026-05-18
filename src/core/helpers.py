import json

from core.constants import (
    STATUS_OK,
    STATUS_INFO,
    STATUS_WARNUNG,
    STATUS_KRITISCH,
    STATUS_FEHLER,
)


def json_ausgabe_umwandeln(rohausgabe: str):
    """
    Wandelt eine PowerShell-JSON-Ausgabe in Python-Daten um.

    Falls die Ausgabe kein gÃ¼ltiges JSON ist, wird der ursprÃ¼ngliche Text zurÃ¼ckgegeben.
    """
    if not rohausgabe:
        return None

    try:
        return json.loads(rohausgabe)
    except json.JSONDecodeError:
        return rohausgabe


def liste_erzwingen(daten) -> list:
    """
    Sorgt dafÃ¼r, dass Daten immer als Liste verarbeitet werden kÃ¶nnen.

    Hintergrund:
    PowerShell gibt bei einem einzelnen Objekt manchmal ein Dictionary zurÃ¼ck,
    bei mehreren Objekten aber eine Liste.
    """
    if daten is None:
        return []

    if isinstance(daten, list):
        return daten

    return [daten]


def ist_lokale_adresse(adresse: str) -> bool:
    """
    PrÃ¼ft, ob eine Adresse nur lokal auf dem Rechner erreichbar ist.
    """
    lokale_adressen = {"127.0.0.1", "::1", "localhost"}
    return adresse in lokale_adressen


def hoechsten_status_ermitteln(status_liste: list) -> str:
    """
    Ermittelt den hÃ¶chsten Status aus einer Liste von Statuswerten.

    Reihenfolge:
    FEHLER > KRITISCH > WARNUNG > INFO > OK
    """
    prioritaet = {
        STATUS_OK: 1,
        STATUS_INFO: 2,
        STATUS_WARNUNG: 3,
        STATUS_KRITISCH: 4,
        STATUS_FEHLER: 5,
    }

    if not status_liste:
        return STATUS_OK

    return max(status_liste, key=lambda status: prioritaet.get(status, 0))
