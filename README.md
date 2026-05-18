# Windows Security Checker

Ein kleines Python-Tool zur Prüfung grundlegender Windows-Sicherheitsparameter.

Das Projekt dient als Lern- und Portfolio-Projekt im Bereich **Cybersecurity**, **Windows-Sicherheit** und **IT-Support**.

---

## Beschreibung

Der **Windows Security Checker** sammelt grundlegende Sicherheitsinformationen eines Windows-Systems und erstellt daraus lokale Berichte.

Das Tool prüft aktuell:

- Systeminformationen
- Microsoft Defender
- Windows-Firewall
- lokale Administratoren
- BitLocker-Status
- Windows-Update-Status
- offene TCP-Ports
- Risikobewertung bekannter Ports

Die Ergebnisse werden in der Konsole angezeigt und zusätzlich als Bericht gespeichert.

Seit Version **0.6.0** ist der Code modular aufgebaut. Die einzelnen Prüfungen, Hilfsfunktionen und Berichtsfunktionen sind in getrennte Module ausgelagert.

---

## Ziel des Projekts

Dieses Projekt wurde erstellt, um praktische Grundlagen im Bereich Blue Team und Windows Security zu üben.

Es zeigt Kenntnisse in:

- Python-Scripting
- PowerShell-Integration
- Windows-Sicherheitsprüfung
- Auswertung von Systeminformationen
- Prüfung von Windows-Sicherheitsfunktionen
- Windows-Update-Auswertung
- Port-Analyse
- Berichtserstellung
- modularem Codeaufbau
- Git- und GitHub-Projektstruktur

---

## Voraussetzungen

- Windows 10 oder Windows 11
- Python 3.10 oder neuer
- PowerShell
- keine externen Python-Bibliotheken erforderlich

---

## Projekt starten

Im Projektordner ausführen:

```powershell
python src/main.py
```

Beispiel:

```powershell
cd C:\Users\nsoma\Documents\windows-security-checker
python src/main.py
```

---

## Beispielausgabe

```text
Windows Security Checker
==============================
Version: 0.6.0

OK - Systeminformationen
     Die Systeminformationen wurden erfolgreich ausgelesen.

WARNUNG - Microsoft Defender
     Microsoft Defender ist aktiv, aber der Echtzeitschutz ist deaktiviert.

OK - Windows-Firewall
     Alle Windows-Firewall-Profile sind aktiv.

OK - Lokale Administratoren
     Es wurden 2 lokale Administratoren oder Administratorgruppen gefunden.

WARNUNG - BitLocker
     Es wurden keine BitLocker-Volumes gefunden.

OK - Windows Update
     Es wurden keine ausstehenden Windows-Softwareupdates gefunden.

INFO - Offene TCP-Ports
     Es wurden offene TCP-Ports gefunden. Bekannte Ports wurden bewertet.

Zusammenfassung
------------------------------
OK: 4
Info: 1
Warnungen: 2
Kritisch: 0
Fehler: 0
```

---

## Statuskategorien

Das Tool unterscheidet mehrere Statuswerte.

| Status | Bedeutung |
|---|---|
| OK | Prüfung erfolgreich und unauffällig |
| INFO | sicherheitsrelevante Information, aber nicht direkt problematisch |
| WARNUNG | prüfbedürftiger Zustand |
| KRITISCH | potenziell gefährlicher Zustand |
| FEHLER | Prüfung konnte nicht ausgeführt werden |

---

## Aktuelle Prüfungen

### Systeminformationen

Ermittelt grundlegende Informationen zum System:

- Computername
- Hersteller
- Modell
- Betriebssystem
- Windows-Version
- Build-Nummer
- Architektur
- letzter Systemstart

---

### Microsoft Defender

Prüft unter anderem:

- ob Microsoft Defender aktiv ist
- ob der Echtzeitschutz aktiv ist
- ob Signaturen veraltet sind

Beispiel für eine Warnung:

```text
Microsoft Defender ist aktiv, aber der Echtzeitschutz ist deaktiviert.
```

---

### Windows-Firewall

Prüft die drei Windows-Firewall-Profile:

- Domain
- Private
- Public

Alle Profile sollten im Normalfall aktiv sein.

---

### Lokale Administratoren

Listet Mitglieder der lokalen Administratorengruppe auf.

Das ist wichtig, weil zu viele lokale Administratoren das Risiko bei kompromittierten Konten erhöhen.

---

### BitLocker

Prüft den BitLocker-Status vorhandener Laufwerke.

BitLocker schützt Daten bei Verlust oder Diebstahl des Geräts. Besonders wichtig ist die Verschlüsselung des Systemlaufwerks.

Das Tool bewertet unter anderem:

- ob BitLocker-Volumes vorhanden sind
- ob Laufwerke vollständig verschlüsselt sind
- ob der BitLocker-Schutz aktiv ist
- ob die Verschlüsselung noch läuft oder pausiert ist

Beispiel für eine Warnung:

```text
Es wurden keine BitLocker-Volumes gefunden.
```

---

### Windows Update

Prüft, ob ausstehende Windows-Softwareupdates vorhanden sind.

Die Prüfung nutzt die Windows-Update-Schnittstelle und erkennt unter anderem:

- Anzahl ausstehender Updates
- potenziell sicherheitsrelevante Updates
- zuletzt installiertes Hotfix-Update
- Update-Titel und Kategorien

Beispiel für eine Warnung:

```text
Es wurden 1 ausstehende Windows-Updates gefunden. Davon wirken 1 sicherheitsrelevant.
```

Hinweis: Die Windows-Update-Prüfung kann etwas länger dauern, weil Windows aktiv nach Updates sucht.

---

### Offene TCP-Ports

Listet offene TCP-Ports im Status `LISTEN` auf.

Zusätzlich bewertet das Tool bekannte Ports nach Risiko.

Beispiele:

| Port | Dienst | Bewertung |
|---:|---|---|
| 135 | RPC | INFO |
| 139 | NetBIOS | INFO |
| 445 | SMB | INFO |
| 3306 | MySQL | WARNUNG |
| 3389 | RDP | KRITISCH |
| 5985 | WinRM HTTP | KRITISCH |
| 5900 | VNC | KRITISCH |
| 23 | Telnet | KRITISCH |

---

## Berichte

Das Tool erstellt automatisch Berichte im Ordner:

```text
reports
```

Es werden zwei Formate erzeugt:

- JSON-Bericht
- TXT-Bericht

Beispiel:

```text
reports/sicherheitsbericht_2026-05-18_10-14-42.json
reports/sicherheitsbericht_2026-05-18_10-14-42.txt
```

---

## Datenschutzhinweis

Die erzeugten Berichte können Systeminformationen enthalten.

Dazu gehören zum Beispiel:

- Computername
- Windows-Version
- offene Ports
- laufende Dienste
- lokale Administratoren
- BitLocker-Status
- ausstehende Windows-Updates
- zuletzt installierte Hotfixes

Deshalb werden Berichte nicht ins Git-Repository aufgenommen.

Der Ordner `reports` ist über `.gitignore` ausgeschlossen.

---

## Projektstruktur

```text
windows-security-checker/
│
├── src/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── helpers.py
│   │   └── powershell.py
│   │
│   ├── checks/
│   │   ├── __init__.py
│   │   ├── system_info.py
│   │   ├── defender.py
│   │   ├── firewall.py
│   │   ├── local_admins.py
│   │   ├── bitlocker.py
│   │   ├── windows_update.py
│   │   └── open_ports.py
│   │
│   └── report/
│       ├── __init__.py
│       ├── console.py
│       └── writer.py
│
├── reports/
│   └── erzeugte Berichte
│
├── README.md
└── .gitignore
```

---

## Modulübersicht

### `src/main.py`

Zentraler Einstiegspunkt des Programms.

Aufgaben:

- startet alle Prüfungen
- erstellt die Gesamtzusammenfassung
- ruft die Berichtsausgabe auf
- speichert JSON- und TXT-Berichte

---

### `src/core/`

Enthält zentrale Hilfsfunktionen und Konstanten.

| Datei | Aufgabe |
|---|---|
| `constants.py` | Statuswerte und Projektpfade |
| `helpers.py` | JSON-Parsing, Listen-Normalisierung, Statusbewertung |
| `powershell.py` | Ausführen von PowerShell-Befehlen mit UTF-8-Ausgabe |

---

### `src/checks/`

Enthält die einzelnen Sicherheitsprüfungen.

| Datei | Prüfung |
|---|---|
| `system_info.py` | Systeminformationen |
| `defender.py` | Microsoft Defender |
| `firewall.py` | Windows-Firewall |
| `local_admins.py` | lokale Administratoren |
| `bitlocker.py` | BitLocker |
| `windows_update.py` | Windows Update |
| `open_ports.py` | offene TCP-Ports |

---

### `src/report/`

Enthält Funktionen für Ausgabe und Berichte.

| Datei | Aufgabe |
|---|---|
| `console.py` | Konsolenausgabe |
| `writer.py` | JSON- und TXT-Berichte speichern |

---

## Versionen

### Version 0.1.0

Erste lauffähige Version mit grundlegenden Checks.

### Version 0.2.0

Statusbewertung mit:

- OK
- WARNUNG
- FEHLER

### Version 0.3.0

Erweiterte Portbewertung mit:

- INFO
- WARNUNG
- KRITISCH

### Version 0.4.0

BitLocker-Prüfung ergänzt.

Das Tool prüft zusätzlich, ob BitLocker-Volumes vorhanden sind und ob Laufwerke verschlüsselt und geschützt sind.

### Version 0.5.0

Windows-Update-Prüfung ergänzt.

Das Tool prüft zusätzlich, ob ausstehende Windows-Softwareupdates vorhanden sind und ob diese sicherheitsrelevant wirken.

### Version 0.6.0

Code modularisiert.

Die Prüfungen, Hilfsfunktionen und Berichtsfunktionen wurden in getrennte Module aufgeteilt. Dadurch ist das Projekt übersichtlicher, wartbarer und besser erweiterbar.

---

## Rechtlicher Hinweis

Dieses Tool ist ausschließlich für Lernzwecke und defensive Sicherheitsprüfungen gedacht.

Es ersetzt kein professionelles Sicherheitsaudit.

Das Tool darf nur auf eigenen Systemen oder auf Systemen verwendet werden, für die eine ausdrückliche Erlaubnis vorliegt.