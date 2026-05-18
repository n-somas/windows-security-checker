from core.constants import STATUS_OK, STATUS_INFO, STATUS_WARNUNG, STATUS_FEHLER
from core.helpers import json_ausgabe_umwandeln, liste_erzwingen
from core.powershell import powershell_ausfuehren


def windows_updates_pruefen() -> dict:
    """
    Prüft den Windows-Update-Status.

    Das Tool verwendet die Windows Update COM-Schnittstelle.
    Es wird geprüft, ob ausstehende Softwareupdates vorhanden sind.
    Zusätzlich wird das zuletzt installierte Hotfix-Update ausgelesen.
    """
    powershell_befehl = """
    $updateSession = New-Object -ComObject Microsoft.Update.Session
    $updateSearcher = $updateSession.CreateUpdateSearcher()
    $searchResult = $updateSearcher.Search("IsInstalled=0 and Type='Software'")

    $pendingUpdates = @()

    foreach ($update in $searchResult.Updates) {
        $categories = @()

        foreach ($category in $update.Categories) {
            $categories += $category.Name
        }

        $pendingUpdates += [PSCustomObject]@{
            Title = $update.Title
            IsDownloaded = $update.IsDownloaded
            IsMandatory = $update.IsMandatory
            MsrcSeverity = $update.MsrcSeverity
            RebootRequired = $update.RebootRequired
            Categories = $categories
        }
    }

    $latestHotfix = Get-HotFix |
        Sort-Object InstalledOn -Descending |
        Select-Object -First 1 HotFixID, Description, InstalledOn

    [PSCustomObject]@{
        PendingUpdateCount = $searchResult.Updates.Count
        PendingUpdates = $pendingUpdates
        LastInstalledHotFix = $latestHotfix
    } | ConvertTo-Json -Depth 6
    """

    ergebnis = powershell_ausfuehren(powershell_befehl, timeout=90)
    daten = json_ausgabe_umwandeln(ergebnis["ausgabe"])

    if not ergebnis["erfolgreich"]:
        return {
            "pruefung": "Windows Update",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": (
                "Der Windows-Update-Status konnte nicht geprüft werden. "
                "Möglicherweise ist der Windows-Update-Dienst nicht verfügbar "
                "oder die Prüfung hat zu lange gedauert."
            ),
            "fehler": ergebnis["fehler"],
        }

    if not isinstance(daten, dict):
        return {
            "pruefung": "Windows Update",
            "status": STATUS_FEHLER,
            "ergebnis": daten,
            "bewertung": "Die Windows-Update-Ausgabe konnte nicht korrekt ausgewertet werden.",
            "fehler": "Unerwartetes Ausgabeformat.",
        }

    pending_count = daten.get("PendingUpdateCount", 0)
    pending_updates = liste_erzwingen(daten.get("PendingUpdates"))

    try:
        pending_count = int(pending_count)
    except (TypeError, ValueError):
        pending_count = len(pending_updates)

    sicherheits_updates = []

    for update in pending_updates:
        if not isinstance(update, dict):
            continue

        titel = str(update.get("Title", ""))
        schweregrad = str(update.get("MsrcSeverity", ""))
        kategorien = update.get("Categories", [])

        if isinstance(kategorien, list):
            kategorien_text = " ".join(str(kategorie) for kategorie in kategorien)
        else:
            kategorien_text = str(kategorien)

        suchtext = f"{titel} {schweregrad} {kategorien_text}".lower()

        if (
            "security" in suchtext
            or "sicherheit" in suchtext
            or "critical" in suchtext
            or "kritisch" in suchtext
        ):
            sicherheits_updates.append(update)

    if pending_count == 0:
        status = STATUS_OK
        bewertung = "Es wurden keine ausstehenden Windows-Softwareupdates gefunden."
    elif sicherheits_updates:
        status = STATUS_WARNUNG
        bewertung = (
            f"Es wurden {pending_count} ausstehende Windows-Updates gefunden. "
            f"Davon wirken {len(sicherheits_updates)} sicherheitsrelevant."
        )
    else:
        status = STATUS_INFO
        bewertung = (
            f"Es wurden {pending_count} ausstehende Windows-Updates gefunden. "
            "Es wurde kein eindeutig sicherheitsrelevantes Update erkannt."
        )

    return {
        "pruefung": "Windows Update",
        "status": status,
        "anzahl_ausstehende_updates": pending_count,
        "anzahl_sicherheits_updates": len(sicherheits_updates),
        "ausstehende_updates": pending_updates,
        "letztes_installiertes_update": daten.get("LastInstalledHotFix"),
        "ergebnis": daten,
        "bewertung": bewertung,
        "fehler": None,
    }