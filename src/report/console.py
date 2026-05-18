from core.constants import STATUS_FEHLER


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

        if pruefung.get("pruefung") == "BitLocker":
            bitlocker_laufwerke_ausgeben(pruefung)

        if pruefung.get("pruefung") == "Windows Update":
            windows_updates_ausgeben(pruefung)

        if pruefung.get("pruefung") == "Offene TCP-Ports":
            tcp_ports_ausgeben(pruefung)

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


def bitlocker_laufwerke_ausgeben(pruefung: dict) -> None:
    """
    Gibt BitLocker-Laufwerke in der Konsole aus.
    """
    volume_bewertungen = pruefung.get("volume_bewertungen", [])

    if not volume_bewertungen:
        return

    print("     BitLocker-Laufwerke:")

    for volume in volume_bewertungen:
        print(
            f"     - {volume.get('status')}: Laufwerk {volume.get('laufwerk')}, "
            f"Schutz: {volume.get('protection_status')}, "
            f"Verschlüsselung: {volume.get('encryption_percentage')} %"
        )
        print(f"       {volume.get('hinweis')}")


def windows_updates_ausgeben(pruefung: dict) -> None:
    """
    Gibt ausstehende Windows-Updates in der Konsole aus.
    """
    updates = pruefung.get("ausstehende_updates", [])

    if not updates:
        return

    print("     Ausstehende Updates:")

    for update in updates[:5]:
        if isinstance(update, dict):
            print(f"     - {update.get('Title')}")

    if len(updates) > 5:
        print(f"     ... weitere {len(updates) - 5} Updates im Bericht.")


def tcp_ports_ausgeben(pruefung: dict) -> None:
    """
    Gibt bewertete TCP-Ports in der Konsole aus.
    """
    port_bewertungen = pruefung.get("port_bewertungen", [])

    if not port_bewertungen:
        return

    print("     Bewertete Ports:")

    for port in port_bewertungen:
        print(
            f"     - {port.get('status')}: Port {port.get('port')} "
            f"({port.get('dienst')}) auf {port.get('adresse')}, "
            f"Prozess: {port.get('prozess')}"
        )
        print(f"       {port.get('hinweis')}")