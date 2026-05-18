from core.constants import STATUS_OK, STATUS_WARNUNG, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln, liste_erzwingen
from core.powershell import powershell_ausfuehren


def firewall_pruefen() -> dict:
    """
    Prüft die Windows-Firewall-Profile.
    """
    powershell_befehl = """
    Get-NetFirewallProfile |
    Select-Object Name, Enabled |
    ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "Windows-Firewall",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die Windows-Firewall konnte nicht geprüft werden.",
            "fehler": ergebnis["fehler"],
        }

    profile = liste_erzwingen(daten)
    deaktivierte_profile = []

    for profil in profile:
        if isinstance(profil, dict) and profil.get("Enabled") is False:
            deaktivierte_profile.append(profil.get("Name"))

    if not deaktivierte_profile:
        status = STATUS_OK
        bewertung = "Alle Windows-Firewall-Profile sind aktiv."
    else:
        status = STATUS_WARNUNG
        bewertung = f"Folgende Firewall-Profile sind deaktiviert: {', '.join(deaktivierte_profile)}"

    return {
        "pruefung": "Windows-Firewall",
        "status": status,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None,
    }
