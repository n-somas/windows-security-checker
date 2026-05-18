from datetime import datetime

from checks.bitlocker import bitlocker_pruefen
from checks.defender import windows_defender_pruefen
from checks.firewall import firewall_pruefen
from checks.local_admins import lokale_administratoren_pruefen
from checks.open_ports import offene_tcp_ports_pruefen
from checks.system_info import systeminformationen_pruefen
from checks.windows_update import windows_updates_pruefen
from core.constants import (
    STATUS_OK,
    STATUS_INFO,
    STATUS_WARNUNG,
    STATUS_KRITISCH,
    STATUS_FEHLER,
)
from report.console import zusammenfassung_ausgeben
from report.writer import json_bericht_speichern, text_bericht_speichern


VERSION = "0.6.0"


def sicherheitsbericht_erstellen() -> dict:
    """
    Führt alle Sicherheitsprüfungen aus und erstellt einen Gesamtbericht.
    """
    pruefungen = [
        systeminformationen_pruefen(),
        windows_defender_pruefen(),
        firewall_pruefen(),
        lokale_administratoren_pruefen(),
        bitlocker_pruefen(),
        windows_updates_pruefen(),
        offene_tcp_ports_pruefen(),
    ]

    bericht = {
        "tool": "windows-security-checker",
        "version": VERSION,
        "erstellt_am": datetime.now().isoformat(timespec="seconds"),
        "hinweis": "Dieses Tool dient zu Lernzwecken und ersetzt kein professionelles Sicherheitsaudit.",
        "zusammenfassung": zusammenfassung_erstellen(pruefungen),
        "pruefungen": pruefungen,
    }

    return bericht


def zusammenfassung_erstellen(pruefungen: list) -> dict:
    """
    Erstellt die Status-Zusammenfassung aller Prüfungen.
    """
    return {
        "ok": sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_OK),
        "info": sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_INFO),
        "warnungen": sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_WARNUNG),
        "kritisch": sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_KRITISCH),
        "fehler": sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_FEHLER),
    }


def main() -> None:
    """
    Einstiegspunkt des Programms.

    Ablauf:
    1. Sicherheitsprüfungen ausführen
    2. JSON-Bericht speichern
    3. Text-Bericht speichern
    4. Zusammenfassung in der Konsole anzeigen
    """
    bericht = sicherheitsbericht_erstellen()

    json_pfad = json_bericht_speichern(bericht)
    text_pfad = text_bericht_speichern(bericht)

    zusammenfassung_ausgeben(bericht)

    print()
    print(f"JSON-Bericht: {json_pfad}")
    print(f"Text-Bericht: {text_pfad}")


if __name__ == "__main__":
    main()