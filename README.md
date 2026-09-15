# gira-hsl3

Eigene HSL3-Logikbausteine (Python 3.9) für den Gira HomeServer/FacilityServer (ab Firmware 4.13).

## Projektstruktur

- `docs/` — HSL3-SDK-Dokumentation (PDF) und offizielle Gira-Beispiele
- `generator/` — HSL3-Generator (`generator3.cpython-39.pyc`), wandelt Konfiguration + Quellcode in `.hsl` um
- `src/<modul_name>/` — eigene Logikbausteine (ein Verzeichnis pro Baustein: `config_*.json` + `hsl3_<id>_*.py`)
- `dist/` — generierte, importierbare `.hsl`-Dateien
- `.venv/` — Python-3.9-Umgebung für den Generator

## Erstellen der .hsl Dateien

```console
source .venv/bin/activate
python3 ./generator/generator3.cpython-39.pyc --source src/<modul_name>/config_<modul_name>.json --target dist/<id>_<modul_name>.hsl --debug
```

Beispiel (offizielles Gira-Beispiel):
```console
python3 ./generator/generator3.cpython-39.pyc --source docs/examples/http_request/config_http_request.json --target dist/10701_http_request.hsl --debug
```

Die erzeugte `.hsl`-Datei kann ab Experte 4.13.0 importiert werden.

## Entwicklung mit Claude

Ausführliche Anweisungen zur Entwicklung neuer HSL3-Bausteine (LogicModule-API, Konfigurationsschema,
Fallstricke, Workflow) stehen in [`CLAUDE.md`](./CLAUDE.md).
