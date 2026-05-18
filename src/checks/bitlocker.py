from core.constants import STATUS_OK, STATUS_INFO, STATUS_WARNUNG, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln, liste_erzwingen, hoechsten_status_ermitteln
from core.powershell import powershell_ausfuehren


def bitlocker_pruefen() -> dict:
    """
    Prüft den BitLocker-Status der vorhandenen Laufwerke.
    """
    powershell_befehl = """
    $volumes = Get-BitLockerVolume |
    Select-Object `
        MountPoint, `
        VolumeStatus, `
        ProtectionStatus, `
        EncryptionPercentage, `
        LockStatus

    @($volumes) | ConvertTo-Json -Depth 4
    """

    ergebnis = powershell_ausfuehren(powershell_befehl)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "BitLocker",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": (
                "Der BitLocker-Status konnte nicht geprüft werden. "
                "Möglicherweise ist BitLocker auf dieser Windows-Edition nicht verfügbar "
                "oder der Befehl benötigt erhöhte Rechte."
            ),
            "fehler": ergebnis["fehler"],
        }

    volumes = liste_erzwingen(daten)

    if not volumes:
        return {
            "pruefung": "BitLocker",
            "status": STATUS_WARNUNG,
            "anzahl_volumes": 0,
            "ergebnis": daten,
            "bewertung": "Es wurden keine BitLocker-Volumes gefunden.",
            "fehler": None,
        }

    volume_bewertungen = []

    for volume in volumes:
        if not isinstance(volume, dict):
            continue

        mountpoint = volume.get("MountPoint")
        volume_status = volume.get("VolumeStatus")
        protection_status = volume.get("ProtectionStatus")
        lock_status = volume.get("LockStatus")
        encryption_percentage = volume.get("EncryptionPercentage")

        try:
            encryption_percentage = int(encryption_percentage)
        except (TypeError, ValueError):
            encryption_percentage = 0

        if (
            volume_status == "FullyEncrypted"
            and protection_status == "On"
            and encryption_percentage == 100
        ):
            status = STATUS_OK
            hinweis = "Das Laufwerk ist vollständig verschlüsselt und der Schutz ist aktiv."
        elif volume_status in {"EncryptionInProgress", "EncryptionPaused"}:
            status = STATUS_INFO
            hinweis = "Die Verschlüsselung ist gestartet, aber noch nicht vollständig abgeschlossen."
        elif protection_status == "Off":
            status = STATUS_WARNUNG
            hinweis = "Der BitLocker-Schutz ist deaktiviert oder das Laufwerk ist nicht geschützt."
        elif volume_status == "FullyDecrypted":
            status = STATUS_WARNUNG
            hinweis = "Das Laufwerk ist nicht verschlüsselt."
        else:
            status = STATUS_WARNUNG
            hinweis = "Der BitLocker-Status ist nicht eindeutig und sollte manuell geprüft werden."

        volume_bewertungen.append(
            {
                "laufwerk": mountpoint,
                "status": status,
                "volume_status": volume_status,
                "protection_status": protection_status,
                "encryption_percentage": encryption_percentage,
                "lock_status": lock_status,
                "hinweis": hinweis,
            }
        )

    status_liste = [volume["status"] for volume in volume_bewertungen]
    gesamtstatus = hoechsten_status_ermitteln(status_liste)

    anzahl_ok = sum(1 for volume in volume_bewertungen if volume["status"] == STATUS_OK)
    anzahl_info = sum(1 for volume in volume_bewertungen if volume["status"] == STATUS_INFO)
    anzahl_warnung = sum(1 for volume in volume_bewertungen if volume["status"] == STATUS_WARNUNG)

    if gesamtstatus == STATUS_OK:
        bewertung = "Alle geprüften Laufwerke sind vollständig verschlüsselt und geschützt."
    else:
        bewertung = (
            f"Es wurden {len(volume_bewertungen)} Laufwerke geprüft: "
            f"{anzahl_ok} OK, {anzahl_info} Info, {anzahl_warnung} Warnung."
        )

    return {
        "pruefung": "BitLocker",
        "status": gesamtstatus,
        "anzahl_volumes": len(volume_bewertungen),
        "volume_bewertungen": volume_bewertungen,
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None,
    }