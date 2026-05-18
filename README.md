# Windows Security Checker

Ein kleines Python-Tool zur Prüfung grundlegender Windows-Sicherheitsparameter.

## Beschreibung

Der Windows Security Checker sammelt grundlegende Sicherheitsinformationen eines Windows-Systems und erstellt daraus einen lokalen Bericht.

Das Tool prüft unter anderem:

- Systeminformationen
- Status von Microsoft Defender
- Status der Windows-Firewall
- lokale Administratoren
- offene TCP-Ports im LISTEN-Status

## Ziel des Projekts

Dieses Projekt dient als Lern- und Portfolio-Projekt im Bereich Cybersecurity und IT-Support.

Es zeigt grundlegende Kenntnisse in:

- Python-Scripting
- PowerShell-Integration
- Windows-Sicherheit
- automatisierter Systemprüfung
- einfacher Berichtserstellung
- Blue-Team-Grundlagen

## Voraussetzungen

- Windows 10 oder Windows 11
- Python 3.10 oder neuer
- PowerShell

Es werden keine externen Python-Bibliotheken benötigt.

## Projekt starten

Im Projektordner folgenden Befehl ausführen:

```powershell
python src/main.py