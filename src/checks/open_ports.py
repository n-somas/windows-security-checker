from core.constants import STATUS_OK, STATUS_INFO, STATUS_WARNUNG, STATUS_KRITISCH, STATUS_FEHLER
from core.helpers import (
    json_ausgabe_umwandeln,
    liste_erzwingen,
    ist_lokale_adresse,
    hoechsten_status_ermitteln,
)
from core.powershell import powershell_ausfuehren


def port_risiko_bewerten(portnummer: int, adresse: str, prozess: str) -> dict:
    """
    Bewertet einen offenen TCP-Port nach Risiko.
    """
    port_katalog = {
        21: {
            "dienst": "FTP",
            "status": STATUS_WARNUNG,
            "hinweis": "FTP überträgt Daten häufig unverschlüsselt. Prüfen, ob der Dienst benötigt wird.",
        },
        22: {
            "dienst": "SSH",
            "status": STATUS_WARNUNG,
            "hinweis": "SSH ist ein Fernzugriffsdienst. Prüfen, ob der Zugriff bewusst aktiviert wurde.",
        },
        23: {
            "dienst": "Telnet",
            "status": STATUS_KRITISCH,
            "hinweis": "Telnet ist unsicher und sollte auf modernen Systemen nicht offen sein.",
        },
        25: {
            "dienst": "SMTP",
            "status": STATUS_WARNUNG,
            "hinweis": "SMTP sollte auf einem normalen Arbeitsplatzrechner in der Regel nicht offen sein.",
        },
        80: {
            "dienst": "HTTP",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Webserver auf Port 80 sollte nur offen sein, wenn er bewusst betrieben wird.",
        },
        135: {
            "dienst": "RPC",
            "status": STATUS_INFO,
            "hinweis": "RPC ist ein typischer Windows-Dienst. Im Heimnetz meistens normal, aber sicherheitsrelevant.",
        },
        139: {
            "dienst": "NetBIOS",
            "status": STATUS_INFO,
            "hinweis": "NetBIOS ist ein älterer Windows-Netzwerkdienst. Prüfen, ob Datei- und Druckerfreigaben benötigt werden.",
        },
        443: {
            "dienst": "HTTPS",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein HTTPS-Dienst sollte nur offen sein, wenn er bewusst betrieben wird.",
        },
        445: {
            "dienst": "SMB",
            "status": STATUS_INFO,
            "hinweis": "SMB wird für Windows-Dateifreigaben genutzt. Im Heimnetz oft normal, aber sicherheitsrelevant.",
        },
        1433: {
            "dienst": "Microsoft SQL Server",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte auf einem Arbeitsplatzrechner nur bewusst offen sein.",
        },
        3306: {
            "dienst": "MySQL",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte nicht unnötig im Netzwerk lauschen.",
        },
        3389: {
            "dienst": "RDP",
            "status": STATUS_KRITISCH,
            "hinweis": "RDP erlaubt Fernzugriff. Wenn nicht benötigt, sollte der Dienst deaktiviert werden.",
        },
        5432: {
            "dienst": "PostgreSQL",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte nicht unnötig im Netzwerk lauschen.",
        },
        5900: {
            "dienst": "VNC",
            "status": STATUS_KRITISCH,
            "hinweis": "VNC erlaubt Fernzugriff und sollte nur bewusst aktiviert sein.",
        },
        5985: {
            "dienst": "WinRM HTTP",
            "status": STATUS_KRITISCH,
            "hinweis": "WinRM über HTTP erlaubt Remote-Verwaltung. Auf Einzelgeräten meist nicht nötig.",
        },
        5986: {
            "dienst": "WinRM HTTPS",
            "status": STATUS_KRITISCH,
            "hinweis": "WinRM erlaubt Remote-Verwaltung. Auf Einzelgeräten meist nicht nötig.",
        },
    }

    port_info = port_katalog.get(portnummer)

    if not port_info:
        return {}

    if ist_lokale_adresse(adresse):
        return {
            "port": portnummer,
            "dienst": port_info["dienst"],
            "status": STATUS_INFO,
            "adresse": adresse,
            "prozess": prozess,
            "hinweis": "Der Dienst lauscht nur lokal auf dem Rechner.",
        }

    return {
        "port": portnummer,
        "dienst": port_info["dienst"],
        "status": port_info["status"],
        "adresse": adresse,
        "prozess": prozess,
        "hinweis": port_info["hinweis"],
    }


def offene_tcp_ports_pruefen() -> dict:
    """
    Listet offene TCP-Ports im LISTEN-Status auf.
    """
    powershell_befehl = """
    $verbindungen = Get-NetTCPConnection -State Listen | Sort-Object LocalPort

    $ergebnisse = foreach ($verbindung in $verbindungen) {
        $prozess = Get-Process -Id $verbindung.OwningProcess -ErrorAction SilentlyContinue

        [PSCustomObject]@{
            LocalAddress = $verbindung.LocalAddress
            LocalPort = $verbindung.LocalPort
            OwningProcess = $verbindung.OwningProcess
            ProcessName = $prozess.ProcessName
        }
    }

    @($ergebnisse) | ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "Offene TCP-Ports",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die offenen TCP-Ports konnten nicht ausgelesen werden.",
            "fehler": ergebnis["fehler"],
        }

    ports = liste_erzwingen(daten)
    anzahl = len(ports)
    port_bewertungen = []

    for port_eintrag in ports:
        if not isinstance(port_eintrag, dict):
            continue

        local_port = port_eintrag.get("LocalPort")
        local_address = str(port_eintrag.get("LocalAddress"))
        process_name = port_eintrag.get("ProcessName")

        try:
            local_port = int(local_port)
        except (TypeError, ValueError):
            continue

        bewertung = port_risiko_bewerten(
            portnummer=local_port,
            adresse=local_address,
            prozess=process_name,
        )

        if bewertung:
            port_bewertungen.append(bewertung)

    status_liste = [eintrag["status"] for eintrag in port_bewertungen]
    status = hoechsten_status_ermitteln(status_liste)

    anzahl_info = sum(1 for eintrag in port_bewertungen if eintrag["status"] == STATUS_INFO)
    anzahl_warnung = sum(1 for eintrag in port_bewertungen if eintrag["status"] == STATUS_WARNUNG)
    anzahl_kritisch = sum(1 for eintrag in port_bewertungen if eintrag["status"] == STATUS_KRITISCH)

    if not port_bewertungen:
        status = STATUS_OK
        bewertung_text = (
            f"Es wurden {anzahl} offene TCP-Ports gefunden. "
            "Es wurden keine bekannten prüfbedürftigen Standardports erkannt."
        )
    else:
        bewertung_text = (
            f"Es wurden {anzahl} offene TCP-Ports gefunden. "
            f"Davon wurden {len(port_bewertungen)} bekannte Ports bewertet: "
            f"{anzahl_info} Info, {anzahl_warnung} Warnung, {anzahl_kritisch} Kritisch."
        )

    return {
        "pruefung": "Offene TCP-Ports",
        "status": status,
        "anzahl": anzahl,
        "port_bewertungen": port_bewertungen,
        "ergebnis": daten,
        "bewertung": bewertung_text,
        "fehler": None,
    }
