import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path


# Statuswerte für die Bewertung der Prüfungen
STATUS_OK = "OK"
STATUS_INFO = "INFO"
STATUS_WARNUNG = "WARNUNG"
STATUS_KRITISCH = "KRITISCH"
STATUS_FEHLER = "FEHLER"


# Projekt-Hauptordner ermitteln
# __file__ zeigt auf src/main.py
# parent.parent geht zwei Ebenen nach oben zum Projektordner
PROJEKT_ORDNER = Path(__file__).resolve().parent.parent

# Ordner für die erzeugten Berichte
BERICHTE_ORDNER = PROJEKT_ORDNER / "reports"


def powershell_ausfuehren(befehl: str) -> dict:
    """
    Führt einen PowerShell-Befehl aus.

    Parameter:
    befehl:
        Der PowerShell-Befehl, der ausgeführt werden soll.

    Rückgabe:
        Ein Dictionary mit:
        - erfolgreich: True oder False
        - ausgabe: Ausgabe des Befehls
        - fehler: Fehlermeldung, falls vorhanden
    """
    try:
        ergebnis = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                befehl
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "erfolgreich": ergebnis.returncode == 0,
            "ausgabe": ergebnis.stdout.strip(),
            "fehler": ergebnis.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "erfolgreich": False,
            "ausgabe": "",
            "fehler": "Der PowerShell-Befehl hat zu lange gedauert und wurde abgebrochen."
        }

    except Exception as fehler:
        return {
            "erfolgreich": False,
            "ausgabe": "",
            "fehler": str(fehler)
        }


def json_ausgabe_umwandeln(rohausgabe: str):
    """
    Wandelt eine PowerShell-JSON-Ausgabe in Python-Daten um.

    Falls die Ausgabe kein gültiges JSON ist, wird der ursprüngliche Text zurückgegeben.
    """
    if not rohausgabe:
        return None

    try:
        return json.loads(rohausgabe)
    except json.JSONDecodeError:
        return rohausgabe


def liste_erzwingen(daten) -> list:
    """
    Sorgt dafür, dass Daten immer als Liste verarbeitet werden können.

    Hintergrund:
    PowerShell gibt bei einem einzelnen Objekt manchmal ein Dictionary zurück,
    bei mehreren Objekten aber eine Liste.
    """
    if daten is None:
        return []

    if isinstance(daten, list):
        return daten

    return [daten]


def ist_lokale_adresse(adresse: str) -> bool:
    """
    Prüft, ob eine Adresse nur lokal auf dem Rechner erreichbar ist.

    127.0.0.1 und ::1 sind Loopback-Adressen.
    Dienste auf diesen Adressen sind nicht direkt im Netzwerk erreichbar.
    """
    lokale_adressen = {"127.0.0.1", "::1", "localhost"}
    return adresse in lokale_adressen


def hoechsten_status_ermitteln(status_liste: list) -> str:
    """
    Ermittelt den höchsten Status aus einer Liste von Statuswerten.

    Reihenfolge:
    FEHLER > KRITISCH > WARNUNG > INFO > OK
    """
    prioritaet = {
        STATUS_OK: 1,
        STATUS_INFO: 2,
        STATUS_WARNUNG: 3,
        STATUS_KRITISCH: 4,
        STATUS_FEHLER: 5
    }

    if not status_liste:
        return STATUS_OK

    return max(status_liste, key=lambda status: prioritaet.get(status, 0))


def systeminformationen_pruefen() -> dict:
    """
    Ermittelt grundlegende Informationen zum Windows-System.

    Dazu gehören:
    - Computername
    - Windows-Version
    - Betriebssystemname
    - Systemarchitektur
    """
    powershell_befehl = """
    $betriebssystem = Get-CimInstance Win32_OperatingSystem
    $computer = Get-CimInstance Win32_ComputerSystem

    [PSCustomObject]@{
        Computername = $computer.Name
        Hersteller = $computer.Manufacturer
        Modell = $computer.Model
        Betriebssystem = $betriebssystem.Caption
        Version = $betriebssystem.Version
        BuildNummer = $betriebssystem.BuildNumber
        Architektur = $betriebssystem.OSArchitecture
        Installationsdatum = $betriebssystem.InstallDate
        LetzterStart = $betriebssystem.LastBootUpTime
    } | ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        status = STATUS_FEHLER
        bewertung = "Die Systeminformationen konnten nicht ausgelesen werden."
    else:
        status = STATUS_OK
        bewertung = "Die Systeminformationen wurden erfolgreich ausgelesen."

    return {
        "pruefung": "Systeminformationen",
        "status": status,
        "python_plattform": platform.platform(),
        "prozessor_architektur": platform.machine(),
        "prozessor": platform.processor(),
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": ergebnis["fehler"] if not ergebnis["erfolgreich"] else None
    }


def windows_defender_pruefen() -> dict:
    """
    Prüft den Status von Microsoft Defender.

    Wichtige Werte:
    - AntivirusEnabled: Virenschutz aktiv
    - RealTimeProtectionEnabled: Echtzeitschutz aktiv
    - AMServiceEnabled: Defender-Dienst aktiv
    - DefenderSignaturesOutOfDate: Signaturen veraltet
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
            "bewertung": "Microsoft Defender konnte nicht geprüft werden.",
            "fehler": ergebnis["fehler"]
        }

    if not isinstance(daten, dict):
        return {
            "pruefung": "Microsoft Defender",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die Defender-Ausgabe konnte nicht korrekt ausgewertet werden.",
            "fehler": "Unerwartetes Ausgabeformat."
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
        bewertung = "Microsoft Defender ist nicht aktiv. Prüfe, ob ein anderes Antivirus-Programm verwendet wird."
    else:
        status = STATUS_WARNUNG
        bewertung = "Der Defender-Status ist nicht eindeutig. Die Details sollten manuell geprüft werden."

    return {
        "pruefung": "Microsoft Defender",
        "status": status,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None
    }


def firewall_pruefen() -> dict:
    """
    Prüft die Windows-Firewall-Profile.

    Windows unterscheidet drei Profile:
    - Domain
    - Private
    - Public

    Für ein normales System sollten alle Profile aktiv sein.
    Besonders wichtig ist das öffentliche Profil.
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
            "fehler": ergebnis["fehler"]
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
        "fehler": None
    }


def lokale_administratoren_pruefen() -> dict:
    """
    Listet Mitglieder der lokalen Administratorengruppe auf.

    Wichtig:
    Die SID S-1-5-32-544 steht für die lokale Administratorengruppe.
    Dadurch funktioniert der Befehl auch auf deutschsprachigen Windows-Systemen.
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
            "fehler": ergebnis["fehler"]
        }

    administratoren = liste_erzwingen(daten)
    anzahl = len(administratoren)

    if anzahl <= 2:
        status = STATUS_OK
        bewertung = (
            f"Es wurden {anzahl} lokale Administratoren oder Administratorgruppen gefunden. "
            "Das ist für ein Einzelgerät nicht ungewöhnlich. "
            "Die Einträge sollten trotzdem regelmäßig geprüft werden."
        )
    else:
        status = STATUS_WARNUNG
        bewertung = (
            f"Es wurden {anzahl} lokale Administratoren oder Administratorgruppen gefunden. "
            "Viele Administratoren erhöhen das Risiko bei kompromittierten Konten."
        )

    return {
        "pruefung": "Lokale Administratoren",
        "status": status,
        "anzahl": anzahl,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None
    }


def port_risiko_bewerten(portnummer: int, adresse: str, prozess: str) -> dict:
    """
    Bewertet einen offenen TCP-Port nach Risiko.

    Die Bewertung ist bewusst konservativ:
    - Windows-Standarddienste wie RPC, NetBIOS und SMB werden als INFO markiert.
    - Remote-Admin-Dienste wie RDP, WinRM, VNC und Telnet werden als KRITISCH markiert.
    - Dienste wie FTP, SSH, SMTP oder Datenbankports werden als WARNUNG markiert.
    """
    port_katalog = {
        21: {
            "dienst": "FTP",
            "status": STATUS_WARNUNG,
            "hinweis": "FTP überträgt Daten häufig unverschlüsselt. Prüfen, ob der Dienst benötigt wird."
        },
        22: {
            "dienst": "SSH",
            "status": STATUS_WARNUNG,
            "hinweis": "SSH ist ein Fernzugriffsdienst. Prüfen, ob der Zugriff bewusst aktiviert wurde."
        },
        23: {
            "dienst": "Telnet",
            "status": STATUS_KRITISCH,
            "hinweis": "Telnet ist unsicher und sollte auf modernen Systemen nicht offen sein."
        },
        25: {
            "dienst": "SMTP",
            "status": STATUS_WARNUNG,
            "hinweis": "SMTP sollte auf einem normalen Arbeitsplatzrechner in der Regel nicht offen sein."
        },
        80: {
            "dienst": "HTTP",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Webserver auf Port 80 sollte nur offen sein, wenn er bewusst betrieben wird."
        },
        135: {
            "dienst": "RPC",
            "status": STATUS_INFO,
            "hinweis": "RPC ist ein typischer Windows-Dienst. Im Heimnetz meistens normal, aber sicherheitsrelevant."
        },
        139: {
            "dienst": "NetBIOS",
            "status": STATUS_INFO,
            "hinweis": "NetBIOS ist ein älterer Windows-Netzwerkdienst. Prüfen, ob Datei- und Druckerfreigaben benötigt werden."
        },
        443: {
            "dienst": "HTTPS",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein HTTPS-Dienst sollte nur offen sein, wenn er bewusst betrieben wird."
        },
        445: {
            "dienst": "SMB",
            "status": STATUS_INFO,
            "hinweis": "SMB wird für Windows-Dateifreigaben genutzt. Im Heimnetz oft normal, aber sicherheitsrelevant."
        },
        1433: {
            "dienst": "Microsoft SQL Server",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte auf einem Arbeitsplatzrechner nur bewusst offen sein."
        },
        3306: {
            "dienst": "MySQL",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte nicht unnötig im Netzwerk lauschen."
        },
        3389: {
            "dienst": "RDP",
            "status": STATUS_KRITISCH,
            "hinweis": "RDP erlaubt Fernzugriff. Wenn nicht benötigt, sollte der Dienst deaktiviert werden."
        },
        5432: {
            "dienst": "PostgreSQL",
            "status": STATUS_WARNUNG,
            "hinweis": "Ein Datenbankdienst sollte nicht unnötig im Netzwerk lauschen."
        },
        5900: {
            "dienst": "VNC",
            "status": STATUS_KRITISCH,
            "hinweis": "VNC erlaubt Fernzugriff und sollte nur bewusst aktiviert sein."
        },
        5985: {
            "dienst": "WinRM HTTP",
            "status": STATUS_KRITISCH,
            "hinweis": "WinRM über HTTP erlaubt Remote-Verwaltung. Auf Einzelgeräten meist nicht nötig."
        },
        5986: {
            "dienst": "WinRM HTTPS",
            "status": STATUS_KRITISCH,
            "hinweis": "WinRM erlaubt Remote-Verwaltung. Auf Einzelgeräten meist nicht nötig."
        }
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
            "hinweis": "Der Dienst lauscht nur lokal auf dem Rechner."
        }

    return {
        "port": portnummer,
        "dienst": port_info["dienst"],
        "status": port_info["status"],
        "adresse": adresse,
        "prozess": prozess,
        "hinweis": port_info["hinweis"]
    }


def offene_tcp_ports_pruefen() -> dict:
    """
    Listet offene TCP-Ports im LISTEN-Status auf.

    Wichtig:
    Ein offener Port ist nicht automatisch gefährlich.
    Er zeigt aber eine mögliche Angriffsfläche.

    Version 0.3.0 unterscheidet:
    - INFO
    - WARNUNG
    - KRITISCH
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
            "fehler": ergebnis["fehler"]
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
            prozess=process_name
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
        "fehler": None
    }


def sicherheitsbericht_erstellen() -> dict:
    """
    Führt alle Sicherheitsprüfungen aus und erstellt einen Gesamtbericht.
    """
    pruefungen = [
        systeminformationen_pruefen(),
        windows_defender_pruefen(),
        firewall_pruefen(),
        lokale_administratoren_pruefen(),
        offene_tcp_ports_pruefen()
    ]

    anzahl_ok = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_OK)
    anzahl_info = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_INFO)
    anzahl_warnungen = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_WARNUNG)
    anzahl_kritisch = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_KRITISCH)
    anzahl_fehler = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_FEHLER)

    bericht = {
        "tool": "windows-security-checker",
        "version": "0.3.0",
        "erstellt_am": datetime.now().isoformat(timespec="seconds"),
        "hinweis": "Dieses Tool dient zu Lernzwecken und ersetzt kein professionelles Sicherheitsaudit.",
        "zusammenfassung": {
            "ok": anzahl_ok,
            "info": anzahl_info,
            "warnungen": anzahl_warnungen,
            "kritisch": anzahl_kritisch,
            "fehler": anzahl_fehler
        },
        "pruefungen": pruefungen
    }

    return bericht


def json_bericht_speichern(bericht: dict) -> Path:
    """
    Speichert den Sicherheitsbericht als JSON-Datei.

    JSON eignet sich gut für:
    - spätere Weiterverarbeitung
    - Automatisierung
    - maschinenlesbare Auswertung
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

    Die Textdatei eignet sich gut für:
    - schnelle Kontrolle
    - einfache Dokumentation
    - Portfolio-Demo
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

        datei.write("Zusammenfassung\n")
        datei.write("-" * 50 + "\n")
        datei.write(f"OK: {bericht['zusammenfassung']['ok']}\n")
        datei.write(f"Info: {bericht['zusammenfassung']['info']}\n")
        datei.write(f"Warnungen: {bericht['zusammenfassung']['warnungen']}\n")
        datei.write(f"Kritisch: {bericht['zusammenfassung']['kritisch']}\n")
        datei.write(f"Fehler: {bericht['zusammenfassung']['fehler']}\n\n")

        for pruefung in bericht["pruefungen"]:
            datei.write("-" * 50 + "\n")
            datei.write(f"Prüfung: {pruefung['pruefung']}\n")
            datei.write(f"Status: {pruefung['status']}\n")
            datei.write("-" * 50 + "\n")

            if pruefung.get("bewertung"):
                datei.write(f"Bewertung: {pruefung['bewertung']}\n\n")

            if pruefung.get("fehler"):
                datei.write(f"Fehler: {pruefung['fehler']}\n\n")

            if pruefung.get("pruefung") == "Offene TCP-Ports":
                port_bewertungen = pruefung.get("port_bewertungen", [])

                if port_bewertungen:
                    datei.write("Bewertete Ports:\n")

                    for port in port_bewertungen:
                        portnummer = port.get("port")
                        dienst = port.get("dienst")
                        status = port.get("status")
                        adresse = port.get("adresse")
                        prozess = port.get("prozess")
                        hinweis = port.get("hinweis")

                        datei.write(
                            f"- {status}: Port {portnummer} ({dienst}) auf {adresse}, "
                            f"Prozess: {prozess}. {hinweis}\n"
                        )

                    datei.write("\n")

            datei.write("Details:\n")
            datei.write(json.dumps(pruefung, indent=4, ensure_ascii=False))
            datei.write("\n\n")

    return dateipfad


def zusammenfassung_ausgeben(bericht: dict) -> None:
    """
    Gibt eine kurze Zusammenfassung in der Konsole aus.
    """
    print()
    print("Windows Security Checker")
    print("=" * 30)

    print(f"Version: {bericht['version']}")
    print()

    for pruefung in bericht["pruefungen"]:
        status = pruefung.get("status", STATUS_FEHLER)
        print(f"{status} - {pruefung['pruefung']}")

        if pruefung.get("bewertung"):
            print(f"     {pruefung['bewertung']}")

        if pruefung.get("pruefung") == "Offene TCP-Ports":
            port_bewertungen = pruefung.get("port_bewertungen", [])

            if port_bewertungen:
                print("     Bewertete Ports:")

                for port in port_bewertungen:
                    portnummer = port.get("port")
                    dienst = port.get("dienst")
                    port_status = port.get("status")
                    adresse = port.get("adresse")
                    prozess = port.get("prozess")
                    hinweis = port.get("hinweis")

                    print(
                        f"     - {port_status}: Port {portnummer} ({dienst}) "
                        f"auf {adresse}, Prozess: {prozess}"
                    )
                    print(f"       {hinweis}")

    print()
    print("Zusammenfassung")
    print("-" * 30)
    print(f"OK: {bericht['zusammenfassung']['ok']}")
    print(f"Info: {bericht['zusammenfassung']['info']}")
    print(f"Warnungen: {bericht['zusammenfassung']['warnungen']}")
    print(f"Kritisch: {bericht['zusammenfassung']['kritisch']}")
    print(f"Fehler: {bericht['zusammenfassung']['fehler']}")

    print()
    print("Bericht wurde erstellt.")


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