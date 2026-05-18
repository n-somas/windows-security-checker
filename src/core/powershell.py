import subprocess


def powershell_ausfuehren(befehl: str, timeout: int = 30) -> dict:
    """
    Führt einen PowerShell-Befehl aus.

    Die PowerShell-Ausgabe wird bewusst als UTF-8 verarbeitet.
    Dadurch werden Encoding-Probleme mit deutschen oder speziellen Zeichen vermieden.
    """
    try:
        powershell_befehl = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$OutputEncoding = [System.Text.Encoding]::UTF8; "
            + befehl
        )

        ergebnis = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_befehl,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        return {
            "erfolgreich": ergebnis.returncode == 0,
            "ausgabe": ergebnis.stdout.strip(),
            "fehler": ergebnis.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "erfolgreich": False,
            "ausgabe": "",
            "fehler": "Der PowerShell-Befehl hat zu lange gedauert und wurde abgebrochen.",
        }

    except Exception as fehler:
        return {
            "erfolgreich": False,
            "ausgabe": "",
            "fehler": str(fehler),
        }
