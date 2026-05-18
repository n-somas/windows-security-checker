import json
from datetime import datetime
from pathlib import Path

from core.constants import BERICHTE_ORDNER


def json_bericht_speichern(bericht: dict) -> Path:
    """
    Speichert den Sicherheitsbericht als JSON-Datei.
    """
    BERICHTE_ORDNER.mkdir(exist_ok=True)

    zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dateipfad = BERICHTE_ORDNER / f"sicherheitsbericht_{zeitstempel}.json"

    with open(dateipfad, "w", encoding="utf-8") as datei:
        json.dump(bericht, datei, indent=4, ensure_ascii=False)

    return dateipfad


def text_bericht_speichern(bericht: dict) -> Path:
    """
    Speichert den Sicherheitsbericht als lesbare Textdatei.
    """
    BERICHTE_ORDNER.mkdir(exist_ok=True)

    zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dateipfad = BERICHTE_ORDNER / f"sicherheitsbericht_{zeitstempel}.txt"

    with open(dateipfad, "w", encoding="utf-8") as datei:
        datei.write("Windows Security Checker - Sicherheitsbericht\n")
        datei.write("=" * 50 + "\n\n")

        datei.write(f"Tool: {bericht['tool']}\n")
        datei.write(f"Version: {bericht['version']}\n")
        datei.write(f"Erstellt am: {bericht['erstellt_am']}\n")
        datei.write(f"Hinweis: {bericht['hinweis']}\n\n")

        zusammenfassung_schreiben(datei, bericht)
        pruefungen_schreiben(datei, bericht)

    return dateipfad


def zusammenfassung_schreiben(datei, bericht: dict) -> None:
    """
    Schreibt die Zusammenfassung in den Textbericht.
    """
    datei.write("Zusammenfassung\n")
    datei.write("-" * 50 + "\n")
    datei.write(f"OK: {bericht['zusammenfassung']['ok']}\n")
    datei.write(f"Info: {bericht['zusammenfassung']['info']}\n")
    datei.write(f"Warnungen: {bericht['zusammenfassung']['warnungen']}\n")
    datei.write(f"Kritisch: {bericht['zusammenfassung']['kritisch']}\n")
    datei.write(f"Fehler: {bericht['zusammenfassung']['fehler']}\n\n")


def pruefungen_schreiben(datei, bericht: dict) -> None:
    """
    Schreibt alle Prüfungen in den Textbericht.
    """
    for pruefung in bericht["pruefungen"]:
        datei.write("-" * 50 + "\n")
        datei.write(f"Prüfung: {pruefung['pruefung']}\n")
        datei.write(f"Status: {pruefung['status']}\n")
        datei.write("-" * 50 + "\n")

        if pruefung.get("bewertung"):
            datei.write(f"Bewertung: {pruefung['bewertung']}\n\n")

        if pruefung.get("fehler"):
            datei.write(f"Fehler: {pruefung['fehler']}\n\n")

        if pruefung.get("pruefung") == "BitLocker":
            bitlocker_laufwerke_schreiben(datei, pruefung)

        if pruefung.get("pruefung") == "Windows Update":
            windows_updates_schreiben(datei, pruefung)

        if pruefung.get("pruefung") == "Offene TCP-Ports":
            tcp_ports_schreiben(datei, pruefung)

        datei.write("Details:\n")
        datei.write(json.dumps(pruefung, indent=4, ensure_ascii=False))
        datei.write("\n\n")


def bitlocker_laufwerke_schreiben(datei, pruefung: dict) -> None:
    """
    Schreibt BitLocker-Laufwerke in den Textbericht.
    """
    volume_bewertungen = pruefung.get("volume_bewertungen", [])

    if not volume_bewertungen:
        return

    datei.write("BitLocker-Laufwerke:\n")

    for volume in volume_bewertungen:
        datei.write(
            f"- {volume.get('status')}: Laufwerk {volume.get('laufwerk')}, "
            f"VolumeStatus: {volume.get('volume_status')}, "
            f"ProtectionStatus: {volume.get('protection_status')}, "
            f"Verschlüsselung: {volume.get('encryption_percentage')} %. "
            f"{volume.get('hinweis')}\n"
        )

    datei.write("\n")


def windows_updates_schreiben(datei, pruefung: dict) -> None:
    """
    Schreibt Windows-Updates in den Textbericht.
    """
    updates = pruefung.get("ausstehende_updates", [])

    if not updates:
        return

    datei.write("Ausstehende Windows-Updates:\n")

    for update in updates:
        if isinstance(update, dict):
            datei.write(
                f"- {update.get('Title')} | "
                f"Schweregrad: {update.get('MsrcSeverity')} | "
                f"Pflichtupdate: {update.get('IsMandatory')}\n"
            )

    datei.write("\n")


def tcp_ports_schreiben(datei, pruefung: dict) -> None:
    """
    Schreibt bewertete TCP-Ports in den Textbericht.
    """
    port_bewertungen = pruefung.get("port_bewertungen", [])

    if not port_bewertungen:
        return

    datei.write("Bewertete Ports:\n")

    for port in port_bewertungen:
        datei.write(
            f"- {port.get('status')}: Port {port.get('port')} "
            f"({port.get('dienst')}) auf {port.get('adresse')}, "
            f"Prozess: {port.get('prozess')}. {port.get('hinweis')}\n"
        )

    datei.write("\n")
