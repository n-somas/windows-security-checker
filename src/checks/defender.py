from core.constants import STATUS_OK, STATUS_WARNUNG, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln
from core.powershell import powershell_ausfuehren


def windows_defender_pruefen() -> dict:
    """
    PrÃ¼ft den Status von Microsoft Defender.
    """
    powershell_befehl = """
    Get-MpComputerStatus |
    Select-Object `
        AMServiceEnabled, `
        AntivirusEnabled, `
        AntispywareEnabled, `
        RealTimeProtectionEnabled, `
        DefenderSignaturesOutOfDate, `
        AntivirusSignatureLastUpdated |
    ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "Microsoft Defender",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Microsoft Defender konnte nicht geprÃ¼ft werden.",
            "fehler": ergebnis["fehler"],
        }

    if not isinstance(daten, dict):
        return {
            "pruefung": "Microsoft Defender",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die Defender-Ausgabe konnte nicht korrekt ausgewertet werden.",
            "fehler": "Unerwartetes Ausgabeformat.",
        }

    antivirus_aktiv = daten.get("AntivirusEnabled")
    echtzeitschutz_aktiv = daten.get("RealTimeProtectionEnabled")
    signaturen_veraltet = daten.get("DefenderSignaturesOutOfDate")

    if antivirus_aktiv and echtzeitschutz_aktiv and not signaturen_veraltet:
        status = STATUS_OK
        bewertung = (
            "Microsoft Defender ist aktiv, der Echtzeitschutz ist eingeschaltet "
            "und die Signaturen sind aktuell."
        )
    elif antivirus_aktiv and echtzeitschutz_aktiv and signaturen_veraltet:
        status = STATUS_WARNUNG
        bewertung = "Microsoft Defender ist aktiv, aber die Signaturen sind veraltet."
    elif antivirus_aktiv and not echtzeitschutz_aktiv:
        status = STATUS_WARNUNG
        bewertung = "Microsoft Defender ist aktiv, aber der Echtzeitschutz ist deaktiviert."
    elif not antivirus_aktiv:
        status = STATUS_WARNUNG
        bewertung = "Microsoft Defender ist nicht aktiv. PrÃ¼fe, ob ein anderes Antivirus-Programm verwendet wird."
    else:
        status = STATUS_WARNUNG
        bewertung = "Der Defender-Status ist nicht eindeutig. Die Details sollten manuell geprÃ¼ft werden."

    return {
        "pruefung": "Microsoft Defender",
        "status": status,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None,
    }
