# Windows Security Checker

Ein kleines Python-Tool zur PrÃ¼fung grundlegender Windows-Sicherheitsparameter.

Das Projekt dient als Lern- und Portfolio-Projekt im Bereich **Cybersecurity**, **Windows-Sicherheit** und **IT-Support**.

---

## Beschreibung

Der **Windows Security Checker** sammelt grundlegende Sicherheitsinformationen eines Windows-Systems und erstellt daraus lokale Berichte.

Das Tool prÃ¼ft aktuell:

- Systeminformationen
- Microsoft Defender
- Windows-Firewall
- lokale Administratoren
- BitLocker-Status
- Windows-Update-Status
- offene TCP-Ports
- Risikobewertung bekannter Ports

Die Ergebnisse werden in der Konsole angezeigt und zusÃ¤tzlich als Bericht gespeichert.

Seit Version **0.6.0** ist der Code modular aufgebaut. Die einzelnen PrÃ¼fungen, Hilfsfunktionen und Berichtsfunktionen sind in getrennte Module ausgelagert.

Version **1.0.0** ist die erste stabile Version des Projekts.

---

## Ziel des Projekts

Dieses Projekt wurde erstellt, um praktische Grundlagen im Bereich Blue Team und Windows Security zu Ã¼ben.

Es zeigt Kenntnisse in:

- Python-Scripting
- PowerShell-Integration
- Windows-SicherheitsprÃ¼fung
- Auswertung von Systeminformationen
- PrÃ¼fung von Windows-Sicherheitsfunktionen
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

Im Projektordner ausfÃ¼hren:

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
Version: 1.0.0

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
| OK | PrÃ¼fung erfolgreich und unauffÃ¤llig |
| INFO | sicherheitsrelevante Information, aber nicht direkt problematisch |
| WARNUNG | prÃ¼fbedÃ¼rftiger Zustand |
| KRITISCH | potenziell gefÃ¤hrlicher Zustand |
| FEHLER | PrÃ¼fung konnte nicht ausgefÃ¼hrt werden |

---

## Aktuelle PrÃ¼fungen

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

PrÃ¼ft unter anderem:

- ob Microsoft Defender aktiv ist
- ob der Echtzeitschutz aktiv ist
- ob Signaturen veraltet sind

Beispiel fÃ¼r eine Warnung:

```text
Microsoft Defender ist aktiv, aber der Echtzeitschutz ist deaktiviert.
```

---

### Windows-Firewall

PrÃ¼ft die drei Windows-Firewall-Profile:

- Domain
- Private
- Public

Alle Profile sollten im Normalfall aktiv sein.

---

### Lokale Administratoren

Listet Mitglieder der lokalen Administratorengruppe auf.

Das ist wichtig, weil zu viele lokale Administratoren das Risiko bei kompromittierten Konten erhÃ¶hen.

---

### BitLocker

PrÃ¼ft den BitLocker-Status vorhandener Laufwerke.

BitLocker schÃ¼tzt Daten bei Verlust oder Diebstahl des GerÃ¤ts. Besonders wichtig ist die VerschlÃ¼sselung des Systemlaufwerks.

Das Tool bewertet unter anderem:

- ob BitLocker-Volumes vorhanden sind
- ob Laufwerke vollstÃ¤ndig verschlÃ¼sselt sind
- ob der BitLocker-Schutz aktiv ist
- ob die VerschlÃ¼sselung noch lÃ¤uft oder pausiert ist

Beispiel fÃ¼r eine Warnung:

```text
Es wurden keine BitLocker-Volumes gefunden.
```

---

### Windows Update

PrÃ¼ft, ob ausstehende Windows-Softwareupdates vorhanden sind.

Die PrÃ¼fung nutzt die Windows-Update-Schnittstelle und erkennt unter anderem:

- Anzahl ausstehender Updates
- potenziell sicherheitsrelevante Updates
- zuletzt installiertes Hotfix-Update
- Update-Titel und Kategorien

Beispiel fÃ¼r eine Warnung:

```text
Es wurden 1 ausstehende Windows-Updates gefunden. Davon wirken 1 sicherheitsrelevant.
```

Hinweis: Die Windows-Update-PrÃ¼fung kann etwas lÃ¤nger dauern, weil Windows aktiv nach Updates sucht.

---

### Offene TCP-Ports

Listet offene TCP-Ports im Status `LISTEN` auf.

ZusÃ¤tzlich bewertet das Tool bekannte Ports nach Risiko.

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

Die erzeugten Berichte kÃ¶nnen Systeminformationen enthalten.

Dazu gehÃ¶ren zum Beispiel:

- Computername
- Windows-Version
- offene Ports
- laufende Dienste
- lokale Administratoren
- BitLocker-Status
- ausstehende Windows-Updates
- zuletzt installierte Hotfixes

Deshalb werden Berichte nicht ins Git-Repository aufgenommen.

Der Ordner `reports` ist Ã¼ber `.gitignore` ausgeschlossen.

---

## Projektstruktur

```text
windows-security-checker/
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ main.py
â”‚   â”‚
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ constants.py
â”‚   â”‚   â”œâ”€â”€ helpers.py
â”‚   â”‚   â””â”€â”€ powershell.py
â”‚   â”‚
â”‚   â”œâ”€â”€ checks/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ system_info.py
â”‚   â”‚   â”œâ”€â”€ defender.py
â”‚   â”‚   â”œâ”€â”€ firewall.py
â”‚   â”‚   â”œâ”€â”€ local_admins.py
â”‚   â”‚   â”œâ”€â”€ bitlocker.py
â”‚   â”‚   â”œâ”€â”€ windows_update.py
â”‚   â”‚   â””â”€â”€ open_ports.py
â”‚   â”‚
â”‚   â””â”€â”€ report/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ console.py
â”‚       â””â”€â”€ writer.py
â”‚
â”œâ”€â”€ reports/
â”‚   â””â”€â”€ erzeugte Berichte
â”‚
â”œâ”€â”€ README.md
â””â”€â”€ .gitignore
```

---

## ModulÃ¼bersicht

### `src/main.py`

Zentraler Einstiegspunkt des Programms.

Aufgaben:

- startet alle PrÃ¼fungen
- erstellt die Gesamtzusammenfassung
- ruft die Berichtsausgabe auf
- speichert JSON- und TXT-Berichte

---

### `src/core/`

EnthÃ¤lt zentrale Hilfsfunktionen und Konstanten.

| Datei | Aufgabe |
|---|---|
| `constants.py` | Statuswerte und Projektpfade |
| `helpers.py` | JSON-Parsing, Listen-Normalisierung, Statusbewertung |
| `powershell.py` | AusfÃ¼hren von PowerShell-Befehlen mit UTF-8-Ausgabe |

---

### `src/checks/`

EnthÃ¤lt die einzelnen SicherheitsprÃ¼fungen.

| Datei | PrÃ¼fung |
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

EnthÃ¤lt Funktionen fÃ¼r Ausgabe und Berichte.

| Datei | Aufgabe |
|---|---|
| `console.py` | Konsolenausgabe |
| `writer.py` | JSON- und TXT-Berichte speichern |

---

## Versionen

### Version 0.1.0

Erste lauffÃ¤hige Version mit grundlegenden Checks.

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

BitLocker-PrÃ¼fung ergÃ¤nzt.

Das Tool prÃ¼ft zusÃ¤tzlich, ob BitLocker-Volumes vorhanden sind und ob Laufwerke verschlÃ¼sselt und geschÃ¼tzt sind.

### Version 0.5.0

Windows-Update-PrÃ¼fung ergÃ¤nzt.

Das Tool prÃ¼ft zusÃ¤tzlich, ob ausstehende Windows-Softwareupdates vorhanden sind und ob diese sicherheitsrelevant wirken.

### Version 0.6.0

Code modularisiert.

Die PrÃ¼fungen, Hilfsfunktionen und Berichtsfunktionen wurden in getrennte Module aufgeteilt. Dadurch ist das Projekt Ã¼bersichtlicher, wartbarer und besser erweiterbar.

### Version 1.0.0

Erste stabile Version des Windows Security Checkers.

Das Tool enthÃ¤lt alle bisherigen KernprÃ¼fungen, eine modulare Code-Struktur sowie eine vollstÃ¤ndige deutsche Projektdokumentation.

---

## Rechtlicher Hinweis

Dieses Tool ist ausschlieÃŸlich fÃ¼r Lernzwecke und defensive SicherheitsprÃ¼fungen gedacht.

Es ersetzt kein professionelles Sicherheitsaudit.

Das Tool darf nur auf eigenen Systemen oder auf Systemen verwendet werden, fÃ¼r die eine ausdrÃ¼ckliche Erlaubnis vorliegt.
