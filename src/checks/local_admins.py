from core.constants import STATUS_OK, STATUS_WARNUNG, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln, liste_erzwingen
from core.powershell import powershell_ausfuehren


def lokale_administratoren_pruefen() -> dict:
    """
    Listet Mitglieder der lokalen Administratorengruppe auf.
    """
    powershell_befehl = """
    $mitglieder = Get-LocalGroupMember -SID 'S-1-5-32-544' |
    Select-Object Name, ObjectClass, PrincipalSource

    @($mitglieder) | ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "Lokale Administratoren",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die lokalen Administratoren konnten nicht ausgelesen werden.",
            "fehler": ergebnis["fehler"],
        }

    administratoren = liste_erzwingen(daten)
    anzahl = len(administratoren)

    if anzahl <= 2:
        status = STATUS_OK
        bewertung = (
            f"Es wurden {anzahl} lokale Administratoren oder Administratorgruppen gefunden. "
            "Das ist fÃ¼r ein EinzelgerÃ¤t nicht ungewÃ¶hnlich. "
            "Die EintrÃ¤ge sollten trotzdem regelmÃ¤ÃŸig geprÃ¼ft werden."
        )
    else:
        status = STATUS_WARNUNG
        bewertung = (
            f"Es wurden {anzahl} lokale Administratoren oder Administratorgruppen gefunden. "
            "Viele Administratoren erhÃ¶hen das Risiko bei kompromittierten Konten."
        )

    return {
        "pruefung": "Lokale Administratoren",
        "status": status,
        "anzahl": anzahl,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None,
    }
