# CLAUDE.md — HSL3-Bausteinentwicklung für den Gira HomeServer/FacilityServer

Diese Datei enthält das Wissen, das für die Entwicklung neuer HSL3-Logikbausteine in diesem
Repository notwendig ist. Grundlage ist `docs/HSL3 SDK 3.0 Doku DE.pdf` sowie die Beispiele unter
`docs/examples/`. Lies diese Datei, bevor du einen neuen Baustein anlegst oder einen bestehenden
änderst.

## Projektüberblick

Dieses Repo dient der Entwicklung eigener HSL3-Logikbausteine (Python 3.9) für den Gira
HomeServer/FacilityServer (ab Firmware 4.13). Fertige Bausteine werden als `.hsl`-Datei generiert
und im Experte (GLE) importiert.

## Verzeichnisstruktur

```
docs/
  HSL3 SDK 3.0 Doku DE.pdf     # Vollständige SDK-Dokumentation (Referenz, siehe Zusammenfassung unten)
  examples/                    # Offizielle Gira-Beispiele, dienen als Vorlage/Referenz
    binary_trigger/
    http_request/
    communication_between_instances/
generator/
  generator3.cpython-39.pyc    # HSL3-Generator (kompiliertes Python 3.9 Modul), erzeugt .hsl aus config + Quellcode
src/
  <modul_name>/                # Ein Verzeichnis pro selbst entwickeltem Logikbaustein
    config_<modul_name>.json
    hsl3_<id>_<modul_name>.py
dist/
  <id>_<modul_name>.hsl        # Generierte, importierbare HSL3-Bausteine (Build-Output)
.venv/                         # Python-3.9-Umgebung für den Generator
```

Neue Bausteine werden ausschließlich unter `src/<modul_name>/` angelegt, ein eigenes Verzeichnis
pro Baustein. Generierte `.hsl`-Dateien landen in `dist/`.

## Entwicklungsumgebung

Der Generator benötigt Python 3.9 (`.venv` ist bereits entsprechend eingerichtet):

```console
source .venv/bin/activate
python3 generator/generator3.cpython-39.pyc --source src/<modul_name>/config_<modul_name>.json --target dist/<id>_<modul_name>.hsl --debug
```

Parameter:
- `--source` / `-s`: Pfad zur Konfigurationsdatei (JSON oder XML), Standard `config.xml`
- `--target` / `-t`: Pfad zur Ziel-`.hsl`-Datei, überschreibt `hsl_filename` aus der Konfiguration
- `--debug` / `-d`: aktiviert Debug-Ausgaben des Generators

Die erzeugte `.hsl`-Datei kann direkt über den HS/FS Experte (ab Version 4.13.0) importiert werden.

## Workflow: Neuen Logikbaustein anlegen

1. **ID vergeben.** Jeder Baustein braucht eine eindeutige 5-stellige numerische ID. Bereits
   vergebene IDs stehen in der Tabelle unten ("Vergebene Modul-IDs") — dort dokumentieren, sobald
   eine neue ID benutzt wird. Die Beispiel-IDs `10700`–`10703` sind durch Gira-Beispiele belegt und
   nicht wiederverwenden.
2. **Verzeichnis anlegen:** `src/<modul_name>/`.
3. **Quellcode-Datei(en) anlegen:** Dateiname **muss** mit `hsl3_<ID>_` beginnen und auf `.py`
   enden, z. B. `hsl3_10800_meine_logik.py`. Enthält das Projekt mehrere Dateien, darf die Klasse
   `LogicModule` nur in der Hauptdatei vorkommen.
4. **Grundgerüst schreiben** (siehe Abschnitt "LogicModule" unten).
5. **Konfigurationsdatei anlegen:** `config_<modul_name>.json` im selben Verzeichnis (Schema siehe
   unten).
6. **Generieren** (siehe Kommandozeile oben) — Ausgabe nach `dist/`.
7. **Prüfen:** Generator-Aufruf muss ohne Fehler durchlaufen ("Inhalt in Zieldatei ... geschrieben.").
   Ein automatisierter Test der Logik selbst ist nur über den Import in den Experte (außerhalb
   dieses Repos) möglich — das kann Claude nicht ausführen, daher explizit als Grenze der
   Verifikation benennen.

## Klasse `LogicModule`

Jeder Baustein basiert auf genau einer Klasse `LogicModule` in der Hauptdatei:

```python
class LogicModule:
    def __init__(self, hsl3):
        self.fw = hsl3

    def on_init(self, inputs, store):
        pass

    def on_calc(self, inputs):
        pass

    def on_timer(self, timer):
        pass
```

- `__init__(self, hsl3fw)`: Pflicht. Wird bei Instanziierung aufgerufen, läuft im **allgemeinen
  Kontext der HSL3-Umgebung** — hier **keine blockierenden Aufrufe**, da das alle HSL3-Bausteine
  verzögert. `hsl3` ist eine Instanz von `Hsl3Framework`.
- `on_init(self, inputs, store)`: Bei Initialisierung der Logik, läuft im Kontext des Bausteins.
  `inputs`/`store` sind `Hsl3Slots`-Instanzen.
- `on_calc(self, inputs)`: Wird aufgerufen, wenn ein Eingang beschrieben wurde und der Baustein neu
  berechnet wird.
- `on_timer(self, timer)`: Wird bei Timer-Auslösung aufgerufen. Ohne Timer-Nutzung kann die Methode
  entfallen.

## `Hsl3Framework` (Instanz: `self.fw`)

- `set_output(index_or_key, value)` — Setzt einen Ausgang. Nur im Kontext des Bausteins aufrufbar
  (sonst `Hsl3ContextError`). `value` muss `float`, `int` oder `bytes` sein — **nicht** `str` oder
  `None` (sonst `ValueError`). Mehrfaches Aufrufen überschreibt den Wert, es wird nur einmal
  gesendet.
- `set_store(index_or_key, value)` — analog für Speichervariablen, gleiche Typ-Regeln/Exceptions.
- `set_timer(index_or_key, seconds)` — Startet/setzt einen Timer. `None` oder `0` hält ihn an. Nur
  im Kontext des Bausteins aufrufbar.
- `run_in_context(callback, params)` — Ruft `callback(*params)` im Kontext des Bausteins auf.
  **Notwendig**, wenn aus einem fremden Thread (z. B. nach einem blockierenden HTTP-Request)
  Ergebnisse verarbeitet oder Ausgänge gesetzt werden sollen — `set_output`/`set_store`/`set_timer`
  dürfen sonst nicht aus dem fremden Thread heraus aufgerufen werden. `params` muss ein Tupel sein.
- `get_logger(host="127.0.0.1", port=65002, console=False, level=logging.INFO)` — Logger über
  Syslog (HS-eigener Syslog-Server: `127.0.0.1:65002`).
- `create_debug_section()` — Liefert `Hsl3DebugSection`-Instanz für die Debug-Anzeige im Experte.
- `get_instance(instance_id)` — Liefert die Baustein-Instanz zu einer `instance_id` (nur gleicher
  Kontext), oder `None`.
- `get_context_id()` — ID des aktuellen Kontexts (String).
- `get_instance_id()` — Laufzeit-ID der aktuellen Instanz (Int, **nicht** identisch mit der
  5-stelligen Baustein-ID).
- `get_module_id()` — ID des aktuellen Moduls.

### Kommunikation zwischen Baustein-Instanzen

Ein Baustein kann per `get_instance_id()` seine Laufzeit-ID auf einen Ausgang schreiben; ein
anderer Baustein empfängt diese ID über einen Eingang und ruft `self.fw.get_instance(instance_id)`
auf, um direkt Methoden der fremden Instanz aufzurufen (siehe
`docs/examples/communication_between_instances/`). So können eigene öffentliche Methoden auf
`LogicModule` für andere Instanzen bereitgestellt werden (z. B. `get_input_value` im Server-Beispiel).

## `Hsl3DebugSection` (via `self.fw.create_debug_section()`)

- `set(name, value)` — Feld setzen/definieren (Reihenfolge = Definitionsreihenfolge).
- `inc(name, value=1)` — Feldwert erhöhen (Exception bei nicht-numerischem `value`).
- `avg(name, value=None)` — gleitenden Durchschnitt berechnen; `None` setzt zurück.
- `timestamp(name, value=None)` — Zeitstempel setzen (Default: jetzt).
- `log(msg)` — Text ins Protokoll schreiben.
- `exception(msg)` — aktuelle Exception + Zusatztext protokollieren.

## `Hsl3Slots` / `Hsl3Slot` (Parameter `inputs`, `store`, `timer`)

Zugriff per Index oder Schlüssel (Identifier aus der Konfiguration):

```python
inputs[1]              # Hsl3Slot-Instanz
inputs[1].value         # Wert von Eingang 1
inputs.value("input")   # Wert per Identifier
inputs.changed("input") # True, wenn geändert
inputs.keys()           # alle Schlüssel
inputs.get(1)           # Hsl3Slot-Instanz (Exception, falls unbekannt)
```

- `Hsl3Slot.value` — aktueller Wert (`float`, `int` oder `bytes`).
- `Hsl3Slot.changed` — bei Eingängen: `True`, wenn Wert geändert & `on_calc` ausgelöst hat (in
  `on_init` immer `False`). Bei Store: immer `False`. Bei Timer: `True`, wenn ausgelöst.

## Konfigurationsdatei (`config_<modul_name>.json`)

Format: JSON (oder XML, hier durchgängig JSON verwenden). Struktur, siehe `docs/examples/*/config_*.json`:

```json
{
  "module": {
    "category": "MeineKategorie",
    "context": "HSL3MeinKontext",
    "id": "10800",
    "name": "Mein Baustein",
    "hsl_filename": "10800_mein_baustein.hsl",
    "version": "1.0",
    "inputs": [
      { "type": "number", "identifier": "input", "init_value": "0", "label": "I1" }
    ],
    "outputs": [
      { "type": "number", "identifier": "output", "init_value": 0, "label": "O1" }
    ],
    "stores": [],
    "timers": [],
    "scripts": [ { "filename": "hsl3_10800_mein_baustein.py" } ],
    "translations": [
      {
        "language": "de",
        "name": "Mein Baustein",
        "category": "MeineKategorie",
        "translation_inputs": [ { "label": "E1" } ],
        "translation_outputs": [ { "label": "A1" } ]
      }
    ]
  }
}
```

Attribute:
- `category` — Baustein-Kategorie im GLE.
- `context` — Kontext-String, in dem der Baustein läuft (relevant für Threading/Kommunikation
  zwischen Instanzen — Instanzen im gleichen Kontext können sich per `get_instance` erreichen).
- `id` — 5-stellige Baustein-ID.
- `name` — Anzeigename im GLE.
- `hsl_filename` — Name der generierten Datei (kann per `--target` überschrieben werden).
- `version` — Versionsbezeichnung.
- `inputs` / `outputs` — je Eintrag: `type` (`number`, `string`, `base_path`, `destination_port`
  — Letztere zwei nur für Eingänge, für externe Erreichbarkeit über einen Basis-Pfad), `identifier`
  (Name im Python-Code), `init_value`, `label` (Anzeige im GLE).
- `stores` — remanente Variablen, gleiche Attribute wie inputs/outputs (`type`: `number`/`string`).
- `timers` — je Eintrag nur `identifier`.
- `scripts` — Liste von `{ "filename": "hsl3_<id>_....py" }` (relativ zur Konfigurationsdatei);
  alternativ `folder` für ein Verzeichnis mit mehreren `hsl3_<id>_*`-Dateien.
- `translations` — pro Sprache ein Eintrag mit `language`, `name`, `category`,
  `translation_inputs`/`translation_outputs` (je Liste von `{"label": ...}` in Reihenfolge der
  Ein-/Ausgänge). Fehlt eine Sprache, verwendet der Experte die Texte aus `module`/`input`/`output`.

## Wichtige Fallstricke

- **Strings sind `bytes`.** Die Firmware kennt bei Ein-/Ausgängen/Speichervariablen nur `bytes` als
  String-Typ. Vor `set_output`/`set_store` explizit encodieren:
  `self.fw.set_output("out", text.encode("iso-8859-15"))` (siehe `http_request`-Beispiel). Beim
  Lesen ggf. `.decode(...)` verwenden.
- **Keine blockierenden Aufrufe im allgemeinen Kontext.** `__init__` läuft im globalen HSL3-Kontext
  — hier keine blockierenden Operationen (z. B. HTTP-Requests), das würde alle Bausteine verzögern.
  Für lang laufende/blockierende Aktionen: eigenen Thread starten (`threading.Thread`) und das
  Ergebnis anschließend per `self.fw.run_in_context(callback, params)` zurück in den
  Baustein-Kontext bringen, bevor `set_output`/`set_store`/`set_timer` aufgerufen wird (siehe
  `http_request`-Beispiel).
- **Kontext-Pflicht für `set_output`/`set_store`/`set_timer`.** Aufruf aus fremdem Thread löst
  `Hsl3ContextError` aus.
- **Nur begrenzte externe Bibliotheken verfügbar:** neben der Python-3-Standardbibliothek nur
  `requests`, `websockets`, `beautifulsoup4`, `pytz`, `python-dateutil`, `pymodbus`. Eigene
  pip-Pakete können nicht eingebunden werden.
- **Datei-Namenskonvention einhalten:** Quellcode-Dateien müssen mit `hsl3_<ID>` beginnen, sonst
  ignoriert sie der Generator.
- **Nur eine `LogicModule`-Klasse pro Baustein**, auch bei mehreren Quellcode-Dateien (nur im
  Hauptskript definieren).
- **Zukunftssicherheit:** Keine bereits abgekündigten Python-Funktionen verwenden, da künftige
  Firmware-Versionen die Python-Version anheben werden.

## Vergebene Modul-IDs in diesem Repo

Bei jedem neuen Baustein hier eintragen, um Kollisionen zu vermeiden (`10700`–`10703` sind durch
die Gira-Beispiele belegt):

| ID    | Verzeichnis (`src/...`)              | Beschreibung |
|-------|---------------------------------------|--------------|
| 10800 | `src/openmeteo_regenvorhersage/`     | OpenMeteo-Wetteranbindung: Regenmenge (mm) heute/morgen/Woche anhand von `lat`/`lng` |
| 10802 | `src/uptimekuma_status/`             | Uptime Kuma `/metrics` (API-Key): Fehler-Flag, Anzahl und Namen gestörter Monitore (Maintenance = OK) |

## Referenzbeispiele

- `docs/examples/binary_trigger/` — minimales Beispiel: ein Eingang, zwei Ausgänge, reine
  `on_calc`-Logik.
- `docs/examples/http_request/` — asynchroner HTTP-Request per Thread + `run_in_context`.
- `docs/examples/communication_between_instances/` — Server/Client-Kommunikation über
  `get_instance_id()` / `get_instance()`.

Vollständige Details: `docs/HSL3 SDK 3.0 Doku DE.pdf` (per `pdftotext -layout` auslesbar, falls
weitere Details benötigt werden, die hier nicht zusammengefasst sind, z. B. Migration von HSL2 zu
HSL3).
