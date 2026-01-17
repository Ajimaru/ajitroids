# Version Management

Die Spielversion wird mit **setuptools-scm** aus Git-Tags automatisch verwaltet. 

## Wie funktioniert die Versionierung?

**setuptools-scm** berechnet die Version automatisch:
- Aus dem letzten Git-Tag (z.B. `v0.23.0`)
- Plus Anzahl Commits seit dem Tag (z.B. `.dev4` für 4 Commits danach)
- Ergebnis: `0.23.1.dev4`

## Neue Release-Version erstellen

```bash
# 1. VERSION-Datei aktualisieren
echo "0.24.0" > VERSION

# 2. _version.py und pyproject.toml aktualisieren
python3 update_version.py

# 3. Änderungen committen
git add VERSION modul/_version.py pyproject.toml
git commit -m "version bump to 0.24.0"

# 4. Git-Tag erstellen (wichtig!)
git tag -a v0.24.0 -m "Release v0.24.0"
git push origin main --tags
```

## Entwicklungs-Versionen

Zwischen den Tags generiert setuptools-scm automatisch Entwicklungs-Versionen:
- Nach Tag `v0.23.0` → `0.23.1.dev1`, `0.23.1.dev2`, etc.
- Diese zeigen, wie viele Commits seit dem letzten Release gemacht wurden

## Fallback-Version

Die `fallback_version` in `pyproject.toml` wird nur verwendet, wenn:
- Kein Git-Repository vorhanden ist
- Keine Tags gefunden werden
- setuptools-scm die Version nicht berechnen kann

Das `update_version.py` Script hält diese fallback_version mit der VERSION-Datei synchron.

## Manuelle Version (ohne Tags)

Falls du die automatische Versionierung umgehen willst:

```bash
# VERSION-Datei bearbeiten
echo "0.24.0" > VERSION

# Aktualisiere _version.py und pyproject.toml
python3 update_version.py

# Commit ohne Tag
git add VERSION modul/_version.py pyproject.toml
git commit -m "set version to 0.24.0"

# WICHTIG: Entferne egg-info und reinstalliere
rm -rf ajitroids.egg-info
pip install -e . --no-deps
```

⚠️ **Hinweis**: Ohne Git-Tag wird die Version aus setuptools-scm's Berechnung kommen, nicht aus der VERSION-Datei!
