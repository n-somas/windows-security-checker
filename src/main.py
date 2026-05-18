import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path


# Statuswerte für die Bewertung der Prüfungen
STATUS_OK = "OK"
STATUS_WARNUNG = "WARNUNG"
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


def offene_tcp_ports_pruefen() -> dict:
    """
    Listet offene TCP-Ports im LISTEN-Status auf.

    Wichtig:
    Ein offener Port ist nicht automatisch gefährlich.
    Er zeigt aber eine mögliche Angriffsfläche.

    Diese Prüfung bewertet besonders sensible Ports,
    wenn sie nicht nur lokal auf 127.0.0.1 oder ::1 lauschen.
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

    sensible_ports = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        80: "HTTP",
        135: "RPC",
        139: "NetBIOS",
        445: "SMB",
        3389: "RDP",
        5900: "VNC",
        5985: "WinRM HTTP",
        5986: "WinRM HTTPS"
    }

    lokale_adressen = {"127.0.0.1", "::1"}
    auffaellige_ports = []

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

        if local_port in sensible_ports and local_address not in lokale_adressen:
            auffaellige_ports.append(
                {
                    "port": local_port,
                    "dienst": sensible_ports[local_port],
                    "adresse": local_address,
                    "prozess": process_name
                }
            )

    if auffaellige_ports:
        status = STATUS_WARNUNG
        bewertung = (
            f"Es wurden {anzahl} offene TCP-Ports gefunden. "
            f"Davon sind {len(auffaellige_ports)} sensible Ports nicht nur lokal gebunden. "
            "Diese Ports sollten geprüft werden."
        )
    else:
        status = STATUS_OK
        bewertung = (
            f"Es wurden {anzahl} offene TCP-Ports im LISTEN-Status gefunden. "
            "Es wurden keine besonders sensiblen Ports außerhalb lokaler Adressen erkannt."
        )

    return {
        "pruefung": "Offene TCP-Ports",
        "status": status,
        "anzahl": anzahl,
        "auffaellige_ports": auffaellige_ports,
        "ergebnis": daten,
        "bewertung": bewertung,
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
    anzahl_warnungen = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_WARNUNG)
    anzahl_fehler = sum(1 for pruefung in pruefungen if pruefung.get("status") == STATUS_FEHLER)

    bericht = {
        "tool": "windows-security-checker",
        "version": "0.2.1",
        "erstellt_am": datetime.now().isoformat(timespec="seconds"),
        "hinweis": "Dieses Tool dient zu Lernzwecken und ersetzt kein professionelles Sicherheitsaudit.",
        "zusammenfassung": {
            "ok": anzahl_ok,
            "warnungen": anzahl_warnungen,
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
        datei.write(f"Warnungen: {bericht['zusammenfassung']['warnungen']}\n")
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
                auffaellige_ports = pruefung.get("auffaellige_ports", [])

                if auffaellige_ports:
                    datei.write("Auffällige Ports:\n")

                    for port in auffaellige_ports:
                        portnummer = port.get("port")
                        dienst = port.get("dienst")
                        adresse = port.get("adresse")
                        prozess = port.get("prozess")

                        datei.write(
                            f"- Port {portnummer} ({dienst}) auf {adresse}, Prozess: {prozess}\n"
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

        # Auffällige Ports direkt in der Konsole anzeigen
        if pruefung.get("pruefung") == "Offene TCP-Ports":
            auffaellige_ports = pruefung.get("auffaellige_ports", [])

            if auffaellige_ports:
                print("     Auffällige Ports:")

                for port in auffaellige_ports:
                    portnummer = port.get("port")
                    dienst = port.get("dienst")
                    adresse = port.get("adresse")
                    prozess = port.get("prozess")

                    print(
                        f"     - Port {portnummer} ({dienst}) auf {adresse}, Prozess: {prozess}"
                    )

    print()
    print("Zusammenfassung")
    print("-" * 30)
    print(f"OK: {bericht['zusammenfassung']['ok']}")
    print(f"Warnungen: {bericht['zusammenfassung']['warnungen']}")
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