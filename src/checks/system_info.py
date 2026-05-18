import platform

from core.constants import STATUS_OK, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln
from core.powershell import powershell_ausfuehren


def systeminformationen_pruefen() -> dict:
    """
    Ermittelt grundlegende Informationen zum Windows-System.
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
        "fehler": ergebnis["fehler"] if not ergebnis["erfolgreich"] else None,
    }