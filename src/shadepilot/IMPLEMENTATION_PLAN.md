# Implementierungsplan: Migration `shadepilot` (HSL2 → HSL3)

**Status:** Entwurf zur Abstimmung — **kein Code in diesem Schritt**, siehe Auftrag.
**Quelle:** `src/shadepilot/old/19822_Jalousie Lamellennachführung_optimiert.hsl` (v3.3.2)
**Ziel:** Neuer HSL3-Baustein unter `src/shadepilot/` gemäß Root-`CLAUDE.md`-Konventionen.

---

## 1. Zielsetzung und Geltungsbereich

Der bestehende Baustein 19822 ("Jalousie-Rolladen-Trennwand / Lamellen-Nachführung") soll
funktional **unverändert** von der HSL2-artigen Regel-Engine (Opcode `5012`, 47 Regeln, 11
funktionale Abschnitte) in einen modernen HSL3-`LogicModule` überführt werden.

Leitplanken für diesen Plan:

- **Verhaltenstreue vor Eleganz.** Jede der 47 Legacy-Regeln muss sich einer neuen Codestelle
  eindeutig zuordnen lassen (siehe Abschnitt 5). Keine stillschweigenden Verhaltensänderungen.
- **Die ADRs sind die Autorität**, nicht die (teilweise veraltete) arc42-Dokumentation. Die
  arc42-Unterlagen unter `old/docs/arc42/09-architecture-decisions.md` kennen ADR-007/ADR-008
  noch nicht — dieser Plan berücksichtigt alle 8 ADRs sowie `anforderungen.md`.
- **Testbarkeit ist ein Designziel**, kein nachträglicher Wunsch. Die Kernlogik wird so
  strukturiert, dass sie ohne Homeserver-Hardware und ohne Experte/GLE-Import per `pytest`
  geprüft werden kann.
- Es wird **keine neue fachliche Funktionalität** ergänzt. Der Baustein soll auf dem
  Homeserver exakt das tun, was `19822_..._optimiert.hsl` heute tut.
- **Zwei Phasen:** Phase 1 portiert 1:1 und sichert das Verhalten durch Tests ab (Abschnitte
  4–8). Phase 2 modernisiert die interne Struktur per Refactoring, ohne das Verhalten zu
  ändern (Abschnitt 11). Die Test-Suite aus Phase 1 ist so gebaut, dass sie Phase 2
  unverändert übersteht und als Sicherheitsnetz dient.

---

## 2. Quellenlage

| Dokument | Rolle |
|---|---|
| `old/19822_Jalousie Lamellennachführung_optimiert.hsl` | Ground Truth der Logik (47 Regeln, ISO-8859-1) |
| `old/CLAUDE.md` | Kompakte Variablen-/Architekturreferenz (deckt sich mit ADRs, aber ADR-007/008 dort bereits eingearbeitet) |
| `old/docs/arc42/00`–`12` | Strukturelle Dokumentation; **§09 veraltet** (fehlt ADR-007/008), Rest verwendbar für Kontext, Laufzeit-Szenarien (§06) und Risiken (§11) |
| `old/SourceDocuments/adr/ADR-001` … `ADR-008` | **Maßgebliche, aktuelle Entscheidungsgrundlage** |
| `old/SourceDocuments/SpecsAndRequirments/anforderungen.md` | Funktionale/nichtfunktionale Anforderungen (Draft-Status, aber inhaltlich konsistent zu ADRs) |
| Root `/CLAUDE.md` | Verbindliche HSL3-Zielarchitektur-Konventionen für dieses Repo |
| `docs/examples/*` | Referenzimplementierungen (Struktur-Vorbild) |
| `src/openmeteo_regenvorhersage/` | Bereits migrierter Schwester-Baustein — nächstliegendes Strukturvorbild |
| HSL3-SDK-Doku (`docs/HSL3 SDK 3.0 Doku DE.pdf`) | API-Referenz `Hsl3Framework`/`Hsl3Slots`; bestätigt: **kein natives `EC[N]`/`EA[N]`-Äquivalent in HSL3** |

---

## 3. IST-Analyse: Legacy-Logik in Kürze

### 3.1 Ein-/Ausgänge

12 Eingänge `EN[1..12]`, 7 Speicher `SN[1..7]`, 5 Ausgänge (Lamelle%, Behang%, Auf/Ab,
Statustext, Zwangsführungs-Statuscode). `EN[12]` ist der Gerätetyp-Diskriminator
(`==0` → Jalousie ohne Lamellenrückmeldung, `>0` → Raffstore mit Lamellenrückmeldung, ADR-001).

### 3.2 Elf funktionale Abschnitte (Auswertungsreihenfolge pro Zyklus)

1. **Sollwertberechnung** `SN[2]` aus Inklinationsformel `round(((90−EN1)·(EN6−EN5)/90)+EN5+EN8)`
   bzw. Ruhewert `EN[7]`, geklammert auf `[EN5, EN6]`.
2. **Positions-Flags** `SN[3]` (Behang in Ziel, ±3 %, **unconditional jeden Zyklus**) und `SN[4]`
   (Lamellenabweichung, nur diagnostisch — TD-01, keine steuernde Wirkung).
3. **Manuell-Vorrang-Erkennung**: löscht `SN[5]`, geschützt durch drei Guards
   (`SN[6]==0`, Endlagenausschluss `EN[12]<98` + Endlagen-Sonderregel via `EC[12]`, ADR-004;
   `not EC[2]`, ADR-005; `not EC[1]`, ADR-007).
4. **Behang-Automatik** bei Zyklus-Start (`EC[3] and EN[3]==1 and EA[3]==0`): Jalousie fährt nur
   ab, wenn `EN[10]<EN[9]` (ADR-006); Raffstore immer bei `SN[3]==0`. Setzt `SN[6]`, `SN[7]`.
   Zusätzlich **unconditional** `SN[5]=1`-Reset, entkoppelt von `SN[3]` (ADR-008).
5. **Lamellennachführung bei Behang-Ankunft** (`EC[10]`), getrennt nach Beschattung Ein/Aus und
   Jalousie-Sonderfall.
6. **Abfahrt-Flag-Reset** (`SN[6]=0`) beim Verlassen der 100 %-Endlage bzw. bei Behang-Ankunft
   ohne Lamellenrückmeldung.
7. **Lamellennachführung bei Inklinationsänderung** (`EC[1]`), nur bei `SN[5]>0`, `SN[3]==1`,
   `SN[6]==0`; Raffstore zusätzlich mit Mindeständerungsschwelle `EN[4]`.
8. **Lamellennachführung bei Beschattungsänderung** (`EC[2]`), inkl. optionalem Behang-Auf bei
   `EN[11]==1`.
9. **Manuell-Vorrang-Rücknahme**: `SN[5]=1`, sobald IST wieder innerhalb Toleranz.
10. **Sicherheits-Timeout**: `SN[6]==1` mit 180 s Timeout → `SN[6]=0`.
11. **Statustext**: jeden Zyklus feuernde Regel, baut Debug-String aus `SN[1..7]`, `EN[12]`.

### 3.3 Zentrale Eigenschaft des Legacy-Modells

Alle 47 Regeln werden **jeden Zyklus vollständig, sequenziell, von oben nach unten** ausgewertet;
später stehende Regeln lesen bereits in diesem Durchlauf aktualisierte Werte (z. B. liest
Abschnitt 3 das in Abschnitt 1 berechnete `SN[2]`). Dies ist **die zentrale Übersetzungsfrage**
für HSL3 (siehe Abschnitt 4.1).

---

## 4. Architekturentscheidungen für die Portierung

### 4.1 "Single-Recompute-Pass"-Muster als Antwort auf das Zyklus-Problem

**Problem:** HSL3s `on_calc(self, inputs)` feuert ereignisbasiert, wenn (mindestens) ein Eingang
neu beschrieben wurde — nicht als fester "jeden Zyklus alles neu berechnen"-Takt wie die
Legacy-Engine. `Hsl3Slot.changed` ist bei `store`-Slots laut SDK **immer `False`**; es gibt somit
kein eingebautes "Speicher X hat sich geändert, folge daraus Y" — die verketteten
Abhängigkeiten zwischen `SN[2]→SN[3]→SN[5]→...` innerhalb eines Legacy-Zyklus lassen sich nicht
über verkettete Store-Trigger nachbilden.

**Entscheidung:** `on_calc` (und `on_init`) rufen bei **jedem** Aufruf eine einzige private
Methode `_recompute()` auf, die **alle 11 Abschnitte in der Original-Reihenfolge** als reine
Sequenz von Python-Anweisungen durchläuft — unabhängig davon, *welcher* Eingang konkret die
Neuberechnung ausgelöst hat. Dadurch:

- wird exakt das Legacy-Verhalten "alle Regeln jeden Zyklus, sequenziell" reproduziert, ganz
  gleich ob HSL3 mehrere gleichzeitig geschriebene Eingänge zu einem oder zu mehreren
  `on_calc`-Aufrufen bündelt (das SDK spezifiziert dieses Detail nicht eindeutig; das gewählte
  Muster ist gegen beide Interpretationen robust, da jeder Aufruf ohnehin den vollen Pass fährt);
- bleiben Zwischenwerte (z. B. `SN[2]` für Abschnitt 3) als **lokale Variablen innerhalb des
  Pass-Durchlaufs** verfügbar, exakt wie in der Legacy-Engine — kein Store-Round-Trip nötig;
- werden `store`/`set_output` erst **am Ende** jedes betroffenen Abschnitts mit dem jeweils
  finalen Wert beschrieben (Root-`CLAUDE.md`: "Mehrfaches Aufrufen überschreibt den Wert, es
  wird nur einmal gesendet" — unkritisch, aber bewusst sauber gehalten).

`_recompute()` wird intern in 11 private Hilfsmethoden gegliedert (siehe Mapping-Tabelle,
Abschnitt 5), die exakt den 11 Legacy-Abschnitten entsprechen und in derselben Reihenfolge
aufgerufen werden. Das ist zugleich die Grundlage der Testbarkeit (Abschnitt 7): jede
Hilfsmethode ist einzeln mit einem präparierten Pass-Zustand aufrufbar.

### 4.2 Rekonstruktion von `EC[N]`/`EA[N]`

HSL3 kennt laut SDK kein natives Flanken-Primitive. Nachbildung:

- Für jeden Eingang, der in einer `EC[N]`/`EA[N]`-Bedingung verwendet wird
  (`EN[1], EN[2], EN[3], EN[10], EN[12]`), wird der **Vorwert als Instanzattribut**
  (`self._prev_inklination`, `self._prev_beschattung`, `self._prev_zyklus`, `self._prev_behang_ist`,
  `self._prev_lamelle_ist`) gehalten.
- Am **Anfang** von `_recompute()` werden `ecN = (aktueller Wert != self._prev_...)` und
  `eaN = self._prev_...` bestimmt; am **Ende** von `_recompute()` werden die `self._prev_...`
  auf die aktuellen Werte aktualisiert (exakt einmal pro Pass, nach allen 11 Abschnitten —
  damit alle Abschnitte innerhalb *eines* Passes denselben `EC`/`EA`-Stand sehen, wie im Original).
- **Bewusste Design-Entscheidung zur Persistenz:** Diese Vorwerte werden als reine
  Python-Instanzattribute (nicht als `store`) gehalten. Sie gehen bei einem Neustart der
  Baustein-Instanz verloren und werden in `on_init` mit den dann aktuellen `inputs`-Werten
  initialisiert (→ `ecN=False` im allerersten Pass, analog zum Legacy-Verhalten, bei dem nach
  einem Neustart ebenfalls kein "Vorwert" existiert). Das deckt sich mit der in
  `old/docs/arc42/04-solution-strategy.md` dokumentierten Annahme, dass Zustand grundsätzlich
  flüchtig ist.

### 4.3 SN-Register: `store`-Slots mit erzwungenem Reset in `on_init`

**Spannungsfeld:** Root-`CLAUDE.md` beschreibt `store` als *"remanente Variablen"* (persistieren
über Neustarts). Die Legacy-Analyse (`old/docs/arc42/04-solution-strategy.md`,
Risiko R-03 in `11-risks-and-technical-debt.md`) geht davon aus, dass `SN[1..7]` beim
Homeserver-Neustart auf ihre Defaults zurückfallen (`SN[5]=1`, Rest `0`) — die Legacy-Engine
verhält sich hier also **nicht remanent**.

**Entscheidung:** `SN[1..7]` werden als `store`-Slots modelliert (Sichtbarkeit im Experte/Debug
bleibt erhalten, konsistent mit dem Schwester-Baustein-Stil), aber **`on_init` setzt sie in
jedem Fall explizit auf die Legacy-Defaults**, unabhängig vom zuvor remanent gespeicherten Wert.
Damit wird das dokumentierte Legacy-Verhalten ("Neustart = Reset") bewusst nachgebildet, obwohl
die HSL3-Store-Semantik technisch Remanenz erlauben würde. Dies wird explizit als Design-Entscheidung
im Code kommentiert, da sie von der "üblichen" Store-Nutzung abweicht.

Mapping (Name im neuen Modul ↔ Legacy):

| Legacy | Neuer Store-Identifier | Default |
|---|---|---|
| `SN[1]` | `store_lamelle_letzter_sollwert` | `0` |
| `SN[2]` | `store_lamelle_sollwert` | `0` |
| `SN[3]` | `store_behang_in_ziel` | `0` |
| `SN[4]` | `store_lamelle_abweicht` | `0` (nur diagnostisch, TD-01 bleibt bestehen) |
| `SN[5]` | `store_automatik_aktiv` | `1` |
| `SN[6]` | `store_abfahrt_aktiv` | `0` |
| `SN[7]` | `store_lamelle_ziel_abfahrt` | `0` |

### 4.4 Sicherheits-Timeout (180 s) via `set_timer`/`on_timer`

Legacy: Regel mit `Timeout="180"` auf Bedingung `SN[6]==1` — feuert, wenn die Bedingung
180 s ununterbrochen wahr bleibt. HSL3-Äquivalent:

- Beim **Setzen** von `store_abfahrt_aktiv = 1` (Abschnitt 4, Behang-Automatik) wird
  `self.fw.set_timer("timer_abfahrt_timeout", 180)` gestartet.
- Beim **Zurücksetzen** von `store_abfahrt_aktiv = 0` an jeder anderen Stelle (Abschnitt 6,
  regulärer Abfahrt-Ende-Pfad) wird der Timer explizit mit `self.fw.set_timer("timer_abfahrt_timeout", None)`
  angehalten (verhindert ein verspätetes, gegenstandsloses Timer-Feuern).
- `on_timer(self, timer)` prüft `timer.changed` für `timer_abfahrt_timeout` und setzt bei
  Auslösung `store_abfahrt_aktiv = 0` über denselben `_recompute()`-Pfad wie Abschnitt 6 (kein
  Sonderpfad, um Divergenz zu vermeiden) — d. h. `on_timer` ruft ebenfalls `_recompute()` mit
  einem Signal "Timeout ausgelöst" auf.

### 4.5 Statustext- und Debug-Ausgänge

- Ausgang 4 (Statustext) ist `type: string`. Gemäß Root-`CLAUDE.md` **muss** vor `set_output`
  explizit kodiert werden: `self.fw.set_output("output_status", text.encode("iso-8859-15"))`
  (gleiche Kodierung wie im `http_request`-Beispiel dieses Repos verwendet).
- Ausgang 5 (Zwangsführungs-Statuscode, 2-Bit-Wert 0/2/3) bleibt `number`, keine Kodierung nötig.
- Zusätzlich wird — wie im `openmeteo_regenvorhersage`-Baustein üblich — `self.debug = self.fw.create_debug_section()`
  in `__init__` angelegt und in `_recompute()` mit den wichtigsten Zwischenwerten (`SN[1..7]`,
  erkannte `EC`-Flags, Gerätetyp) befüllt — rein zur Diagnose im Experte, ohne Einfluss auf die
  Fachlogik.

### 4.6 Gerätetyp-Unterscheidung

Unverändert: `inputs.value("input_lamelle_ist") == 0` → Jalousie-Zweig,
`> 0` → Raffstore-Zweig (ADR-001). Keine neue Konfigurationsoption, wie im Original.

### 4.7 Geplante Modulstruktur

```
src/shadepilot/
  IMPLEMENTATION_PLAN.md          # dieses Dokument
  config_shadepilot.json          # neu (Abschnitt 6)
  hsl3_<ID>_shadepilot.py         # LogicModule (Hauptdatei, einzige Datei geplant)
  tests/
    fakes.py                      # Fake Hsl3Framework/Hsl3Slots für Tests
    harness.py                    # Treiber: spielt Eingangssequenzen gegen LogicModule ab
    legacy_reference.py           # Referenz-Interpreter für die Original-.hsl (Abschnitt 7.6)
    test_scenarios.py             # Black-Box-Szenarien arc42 §06 (Abschnitt 7.2)
    test_adr_regressions.py       # Black-Box-Regressionstests ADR-004…008 (Abschnitt 7.3)
    test_differential.py          # Neu vs. Legacy, gleiche Eingangssequenzen (Abschnitt 7.6)
    test_steps.py                 # optionale Hilfstests pro _stepN, in Phase 2 verwerfbar
  old/                            # unverändert, bleibt als Referenz erhalten (inkl. SourceDocuments/)
```

Da die Logik überschaubar bleibt (kein blockierendes I/O, keine Threads nötig — im Unterschied
zu `openmeteo_regenvorhersage`), wird **eine** Hauptdatei mit `LogicModule` als ausreichend
eingeschätzt; keine Mehrdateien-Aufteilung vorgesehen (Root-`CLAUDE.md`: bei mehreren Dateien
darf `LogicModule` nur in der Hauptdatei stehen — hier ohnehin nur eine Datei).

---

## 5. Regel-zu-Methode-Mapping (Legacy-Abschnitt → geplante Methode)

| # | Legacy-Abschnitt | Legacy-Zeilen | Geplante private Methode | Betroffene ADRs |
|---|---|---|---|---|
| 1 | Sollwertberechnung `SN[2]` | 54–57 | `_step1_sollwert_berechnen()` | — |
| 2 | Positions-Flags `SN[3]`/`SN[4]` | 60–65 | `_step2_positions_flags()` | ADR-008 (Kontext für Bug) |
| 3 | Manuell-Vorrang-Erkennung | 75–79 | `_step3_manuell_erkennung()` | ADR-004, ADR-005, ADR-007 |
| 4 | Behang-Automatik + `SN[5]`-Reset | 89–107 | `_step4_behang_automatik()` | ADR-006, ADR-008 |
| 5 | Lamellennachführung bei Ankunft (`EC[10]`) | 116–127 | `_step5_lamelle_bei_ankunft()` | — |
| 6 | Abfahrt-Flag-Reset | 134–135 | `_step6_abfahrt_reset()` | ADR-002, ADR-003 |
| 7 | Lamellennachführung bei Inklinationsänderung (`EC[1]`) | 144–146 | `_step7_lamelle_bei_inklination()` | ADR-007 |
| 8 | Lamellennachführung bei Beschattungsänderung (`EC[2]`) | 153–156 | `_step8_lamelle_bei_beschattung()` | ADR-005 |
| 9 | Manuell-Vorrang-Rücknahme | 165–172 | `_step9_manuell_ruecknahme()` | ADR-005 |
| 10 | Sicherheits-Timeout | 178 | `_step10_timeout()` + `on_timer` | — |
| 11 | Statustext / Debug-Ausgang | 187, 194 | `_step11_status_ausgeben()` | — |

`_recompute()` ruft `_step1` … `_step11` strikt in dieser Reihenfolge auf. Jede Methode erhält
und mutiert ein gemeinsames, innerhalb des Passes lebendes Zustandsobjekt (z. B. ein einfaches
`dataclass`/`SimpleNamespace` `pass_state`), das am Ende in `store`/`set_output` geschrieben wird.
Diese 1:1-Rückverfolgbarkeit ist die Grundlage, um bei einer späteren Änderung an der Legacy-Datei
(sollte es sie geben) den Diff gezielt einer Methode zuordnen zu können.

---

## 6. Entwurf der Konfigurationsdatei

Geplanter Dateiname: `config_shadepilot.json`. **Modul-ID-Vorschlag: `10801`** (nächste freie ID
nach `10800`; verbindliche Registrierung in der Root-`CLAUDE.md`-Tabelle erfolgt erst bei
tatsächlicher Umsetzung, siehe Abschnitt 10 — in diesem Planungsschritt wird noch keine ID
reserviert/eingetragen).

Geplante Struktur (Auszug, ohne `translations` der Übersicht halber):

```json
{
  "module": {
    "category": "Beschattung",
    "context": "HSL3Shadepilot",
    "id": "10801",
    "name": "Shadepilot – Jalousie-/Raffstore-Lamellennachführung",
    "hsl_filename": "10801_shadepilot.hsl",
    "version": "1.0",
    "inputs": [
      { "type": "number", "identifier": "input_inklination", "init_value": "0", "label": "Inklination %" },
      { "type": "number", "identifier": "input_beschattung", "init_value": "0", "label": "Beschattung Ein/Aus" },
      { "type": "number", "identifier": "input_zyklus", "init_value": "0", "label": "Zyklus Ein/Aus" },
      { "type": "number", "identifier": "input_toleranz", "init_value": "0", "label": "Mindeständerung/Toleranz %" },
      { "type": "number", "identifier": "input_lamelle_waagrecht", "init_value": "0", "label": "Lamelle waagrecht %" },
      { "type": "number", "identifier": "input_lamelle_senkrecht", "init_value": "0", "label": "Lamelle senkrecht %" },
      { "type": "number", "identifier": "input_lamelle_ruhe", "init_value": "0", "label": "Lamelle bei Beschattung Aus %" },
      { "type": "number", "identifier": "input_offset", "init_value": "0", "label": "Offset Lamellenwinkel" },
      { "type": "number", "identifier": "input_behang_ziel", "init_value": "0", "label": "Behang-Zielposition %" },
      { "type": "number", "identifier": "input_behang_ist", "init_value": "0", "label": "Behang IST %" },
      { "type": "number", "identifier": "input_steuerung_behang", "init_value": "0", "label": "Steuerung Behang (1=Auf bei Aus)" },
      { "type": "number", "identifier": "input_lamelle_ist", "init_value": "0", "label": "Lamelle IST % (0=Jalousie)" }
    ],
    "outputs": [
      { "type": "number", "identifier": "output_lamelle", "init_value": 0, "label": "Lamelle %" },
      { "type": "number", "identifier": "output_behang", "init_value": 0, "label": "Behang %" },
      { "type": "number", "identifier": "output_auf_ab", "init_value": 0, "label": "Auf/Ab" },
      { "type": "string", "identifier": "output_status", "init_value": "", "label": "Statustext" },
      { "type": "number", "identifier": "output_automatik_status", "init_value": 0, "label": "Automatik-Status" }
    ],
    "stores": [
      { "type": "number", "identifier": "store_lamelle_letzter_sollwert", "init_value": 0 },
      { "type": "number", "identifier": "store_lamelle_sollwert", "init_value": 0 },
      { "type": "number", "identifier": "store_behang_in_ziel", "init_value": 0 },
      { "type": "number", "identifier": "store_lamelle_abweicht", "init_value": 0 },
      { "type": "number", "identifier": "store_automatik_aktiv", "init_value": 1 },
      { "type": "number", "identifier": "store_abfahrt_aktiv", "init_value": 0 },
      { "type": "number", "identifier": "store_lamelle_ziel_abfahrt", "init_value": 0 }
    ],
    "timers": [
      { "identifier": "timer_abfahrt_timeout" }
    ],
    "scripts": [ { "filename": "hsl3_10801_shadepilot.py" } ],
    "translations": [ /* de-Label analog zu labels oben, in Eingabereihenfolge */ ]
  }
}
```

Diese Struktur ist ein Entwurf zur Abstimmung — Feinschliff (exakte Labels/Kategorie-Namen)
erfolgt im Umsetzungsschritt.

---

## 7. Unit-Test-Strategie

**Antwort auf die Frage "kannst du unit tests erstellen?": Ja** — die Kernlogik wird bewusst so
geschnitten, dass sie ganz ohne Homeserver, Experte oder GLE-Import mit `pytest` prüfbar ist.

### 7.1 Testbarkeits-Design: Black-Box zuerst

**Grundsatz:** Die maßgeblichen Tests prüfen den Baustein **ausschließlich über seine
öffentliche HSL3-Schnittstelle** — `on_init`, `on_calc`, `on_timer` rein, beobachtete
`set_output`/`set_timer`-Aufrufe raus. Sie kennen keine internen Methoden, keine
`_prev_...`-Attribute und keine Pass-Zustandsobjekte. Nur so überstehen sie das Refactoring in
Phase 2 unverändert.

- **Fake-Framework** (`tests/fakes.py`): `FakeHsl3Framework` zeichnet
  `set_output`/`set_store`/`set_timer`-Aufrufe auf und ruft `run_in_context`-Callbacks synchron
  auf; `FakeHsl3Slots`/`FakeHsl3Slot` implementieren `.value`, `.changed`, `.get()`, `.keys()`
  wie in der SDK-Doku beschrieben.
- **Test-Harness** (`tests/harness.py`): nimmt eine Sequenz von Ereignissen entgegen
  (`set_input(name, wert)`, `fire_timer(name)`), ruft die passenden `LogicModule`-Methoden auf
  und liefert pro Schritt die gesendeten Ausgänge und Timer-Aktionen. Szenarien werden damit als
  lesbare Tabellen "Eingang → erwartete Ausgänge" formuliert.
- **Was die Tests beobachten dürfen:** Ausgänge 1–5 und Timer-Aktionen. **Nicht** die
  Store-Werte — sie sind in Phase 1 zwar 1:1 zu `SN[1..7]`, gelten aber als Implementierungsdetail,
  das Phase 2 umbauen darf. Wo ein Szenario einen internen Zustand belegen muss (z. B.
  "Automatik ist aus"), wird das über beobachtbares Verhalten geprüft (Ausgang 5, oder: eine
  folgende Inklinationsänderung führt zu keiner Lamellenfahrt).
- **Hilfstests pro Schritt** (`tests/test_steps.py`) sind erlaubt, um beim Portieren einzelne
  `_stepN`-Methoden schnell zu prüfen. Sie sind ausdrücklich als **verwerfbar** markiert und
  werden in Phase 2 gelöscht oder angepasst, sobald sich die interne Struktur ändert.
- Der Entscheidungsteil (Formel, Guards, Zustandsübergänge) bleibt trotzdem frei von
  `self.fw`-Aufrufen; Framework-Aufrufe erfolgen gebündelt am Ende von `_recompute()`. Das hält
  auch die Hilfstests einfach.
- Kein echter Import in den Experte wird hierdurch ersetzt oder vorgetäuscht — geprüft wird
  ausschließlich die Python-Logik (siehe Abschnitt 8).

### 7.2 Testszenarien aus dokumentiertem Laufzeitverhalten (arc42 §06)

Die vier in `old/docs/arc42/06-runtime-view.md` dokumentierten Sequenzdiagramme werden zu
konkreten Black-Box-Testfällen (`tests/test_scenarios.py`). Die Angaben in Klammern nennen den
fachlichen Legacy-Zustand zur Orientierung; geprüft wird jeweils das beobachtbare Verhalten
(Ausgänge 1–5):

1. **Normaler Raffstore-Zyklus**: Zyklus-Start → Abfahrt → Ankunft → Lamellennachführung.
2. **Manuell-Vorrang-Erkennung + automatische Rücknahme**: manuelle Abweichung erkannt
   (`SN[5]→0`; beobachtbar: Ausgang 5 = 0, keine Lamellenfahrt bei Inklinationsänderung),
   anschließende Rückkehr in Toleranz (`SN[5]→1`; Nachführung läuft wieder).
3. **Beschattungs-Umschaltung mit Übergangsmaskierung**: der `EC[2]`-Zyklus darf die Automatik
   **nicht** abschalten, obwohl `EN[12]` kurzzeitig vom neuen Sollwert abweicht.
4. **Inklinationsänderung während Automatikbetrieb**: Lamellennachführung erfolgt, Automatik
   bleibt aktiv (`not EC[1]`-Maskierung greift).

### 7.3 Regressionstests aus den ADRs (höchste Priorität)

Diese Fälle sind explizit als frühere, real auf Hardware aufgetretene Fehler dokumentiert und
müssen als **permanente Black-Box-Regressionstests** in die Suite
(`tests/test_adr_regressions.py`). Auch hier gilt: SN-Bezeichnungen beschreiben die fachliche
Situation, die Prüfung erfolgt über Ausgänge und Folgeverhalten.

- **ADR-004** (Endlagen-Erkennung): Test, dass die 06/2026-Regression (`EN[12]<98` allein ohne
  Flankenbedingung entfernt → Lamellennachführung nach Endlage bricht) **nicht** wieder auftritt —
  d. h. Test für den 07/2026-Fix (`EC[12]`-basierte Endlagenregel) UND Test, der die
  ursprüngliche Problemsituation (Automatik korrekt weiterläuft, wenn die Lamelle die 100 %-Endlage
  regulär anfährt) abdeckt.
- **ADR-007**: Sonnenstandssprung (`EC[1]`) im selben Pass, in dem `SN[2]` sich ändert, darf
  `SN[5]` **nicht** löschen — sonst deaktiviert sich die Automatik bei jeder
  Inklinationsänderung selbst (das historische Symptom).
- **ADR-008**: Zyklus-Start mit bereits zufällig `SN[3]==1` (Behang "zufällig" in Toleranz
  stehend) muss `SN[5]` trotzdem unconditional auf 1 zurücksetzen.
- **ADR-005**: Beschattungs-Umschaltung (`EC[2]`) darf im selben Zyklus keine
  Manuell-Erkennung auslösen.
- **ADR-006**: Jalousie fährt bei Zyklus-Start **nur** ab, wenn `EN[10] < EN[9]`; Test für
  beide Fälle (`EN[10]>EN[9]` → keine Abfahrt, `EN[10]<EN[9]` → Abfahrt), inkl. Kontrolltest,
  dass Raffstore in derselben Situation **bidirektional** abfährt (asymmetrisches Verhalten,
  ADR-006 "Negativ/Risiken").

### 7.4 Weitere Testmatrix (Auswahl, nicht abschließend)

- Sollwertformel: Referenzwerte für mehrere `EN[1]`/`EN[5]`/`EN[6]`/`EN[8]`-Kombinationen inkl.
  Clamping an `[EN5, EN6]`.
- Gerätetyp-Verzweigung: identische Eingangssequenz einmal mit `EN[12]==0` (Jalousie), einmal
  mit `EN[12]>0` (Raffstore) → unterschiedliches erwartetes Verhalten gemäß ADR-001/ADR-006.
- Sicherheits-Timeout: eine Abfahrt startet einen 180-s-Timer (`set_timer(..., 180)`);
  ein simuliertes Timer-Ereignis beendet den Abfahrt-Schutz (beobachtbar: Manuell-Erkennung
  greift danach wieder); ein regulärer Abfahrt-Reset vor Ablauf hält den Timer an
  (`set_timer(..., None)`). Timer-Aktionen gelten als Teil der beobachtbaren Schnittstelle.
- String-Ausgabe: Statustext wird als `bytes` (ISO-8859-15) gesendet, nie als `str`.
- `SN[4]` ist im Original rein diagnostisch (TD-01): Test, dass zwei Eingangssequenzen, die sich
  nur in der Lamellenabweichung unterscheiden, bei Ausgängen 1–3 identisch reagieren. Dieser
  Test belegt auch, dass die Bereinigung von `SN[4]` in Phase 2 gefahrlos ist. (Achtung:
  Ausgang 5 und der Statustext lesen `SN[4]`, siehe Abschnitt 11.3.)

### 7.5 Testinfrastruktur

- `pytest` (Standard-Testrunner, keine zusätzliche Abhängigkeit nötig — bereits Teil der
  `.venv`-fähigen Toolchain oder leicht ergänzbar, unabhängig vom Generator-`.venv`, da Tests
  nicht den kompilierten Generator benötigen).
- Testverzeichnis `src/shadepilot/tests/`, lauffähig unabhängig vom `.hsl`-Build
  (`python3 -m pytest src/shadepilot/tests/`).
- Die Tests sind **kein** Ersatz für einen echten Test im Experte/GLE — siehe Abschnitt 8.

### 7.6 Differenztest gegen die Original-`.hsl` (Referenz-Interpreter)

**Ziel:** Verhaltenstreue nicht nur gegen meine Lesart der Legacy-Logik prüfen, sondern gegen
den echten Legacy-Code. Die Tests aus 7.2–7.4 kodieren mein Verständnis — ein Lesefehler würde
sich sowohl in Implementierung als auch Test wiederfinden. Der Differenztest schließt diese Lücke.

**Referenz-Interpreter** (`tests/legacy_reference.py`, reine Testhilfe, wird nicht deployed):

- Liest `old/19822_Jalousie Lamellennachführung_optimiert.hsl` (ISO-8859-1) direkt ein und
  extrahiert die Opcodes `5002` (Eingangs-Defaults), `5003` (Store-Defaults), `5004`
  (Ausgangsdeklarationen) und alle 47 `5012`-Regeln.
- Wertet pro Zyklus alle Regeln sequenziell aus. Bedingung und Wert sind im Kern
  Python-Ausdrücke über `EN`, `SN`, `EC`, `EA` sowie `round`, `abs`, `int`, `float`, `min`,
  `str` (per `ast.parse` an allen 47 Regeln verifiziert: alle sind gültige Python-Ausdrücke,
  andere Namen kommen nicht vor). Ausgewertet wird per `eval` in einem eingeschränkten
  Namensraum (keine Builtins außer den genannten). Da nur die eigene, versionierte Datei im
  Repo ausgewertet wird, ist `eval` hier vertretbar; der Interpreter lädt keine fremden Dateien.
- Bildet die Legacy-Semantik nach, die der Differenztest braucht:
  - `EC[N]`/`EA[N]` pro Zyklus, Vorwerte werden nach dem vollständigen Durchlauf aktualisiert;
  - Regeln schreiben sofort in `SN`, spätere Regeln im selben Zyklus sehen den neuen Wert;
  - Regel-Timeout (nur Regel 45, `SN[6]==1` → nach 180 s `SN[6]=0`) als simulierte Zeit, die
    der Harness explizit vorstellt;
  - Ausgangs-Sendeverhalten laut `5004`: Ausgänge 1 und 4 sind als "senden bei Änderung"
    deklariert, 2, 3 und 5 als "immer senden". Das exakte Feldlayout von `5004` ist im Repo
    nicht dokumentiert und wird beim Bau des Interpreters an den Kommentaren in der `.hsl`
    (Zeilen 35–39) festgemacht; Unsicherheiten dazu werden im Code als solche markiert.
- **Wichtig:** Der Interpreter bildet die Legacy-Semantik so nach, wie sie in `old/CLAUDE.md`
  und arc42 §04 dokumentiert ist. Er ist keine Firmware-Emulation. Weicht die echte
  Homeserver-Engine in Details ab (z. B. Timeout-Verhalten bei zwischenzeitlich falscher
  Bedingung), würde der Differenztest das nicht erkennen.

**Differenztest** (`tests/test_differential.py`):

- Dieselbe Eingangssequenz läuft durch Referenz-Interpreter und neues `LogicModule`
  (über den Harness). Verglichen werden die gesendeten Werte der Ausgänge 1–5 pro Schritt.
- **Deterministische Sequenzen:** alle Szenarien aus 7.2/7.3 zusätzlich im Differenzmodus.
- **Zufallssequenzen:** Generator für plausible Eingangsfolgen (Zyklus an/aus, Inklination in
  kleinen Schritten, Behang/Lamelle bewegen sich Richtung Soll oder springen "manuell", Timeout
  wird gelegentlich ausgelöst, beide Gerätetypen). Fester Seed, damit Fehlschläge
  reproduzierbar sind; bei Abweichung gibt der Test die minimale Sequenz bis zum ersten
  Unterschied aus. Standardmäßig einige hundert Sequenzen, per Umgebungsvariable erweiterbar.
  Kein `hypothesis`, um keine neue Abhängigkeit einzuführen; ein kleiner eigener Generator reicht.
- **Statustext (Ausgang 4):** wird ebenfalls verglichen. Er ist in Phase 1 bytegleich zu halten.
  Soll er in Phase 2 geändert werden, ist das eine bewusste, sichtbare Verhaltensänderung, die
  der Test explizit ausnimmt (nicht stillschweigend).
- **Bekannte, gewollte Abweichungen** (falls sich welche ergeben, z. B. durch
  Sendeverhalten, das HSL3 anders regelt) werden in einer expliziten Ausnahmeliste im Test
  geführt, jeweils mit Begründung. Die Liste ist am Ende von Phase 1 leer oder vom Nutzer
  abgenommen.

**Selbsttest des Interpreters:** Bevor er als Referenz dient, wird er gegen die Szenarien aus
7.2 geprüft (die erwarteten Werte stammen aus den arc42-Sequenzdiagrammen, also unabhängig von
meiner Implementierung). So ist er nicht nur "zweite Kopie meiner Lesart".

---

## 8. Grenzen der Verifikation (gemäß Root-`CLAUDE.md`)

- Ein automatisierter Test des Bausteins **auf dem echten Homeserver/im Experte** ist mir
  (Claude) nicht möglich — das ist eine harte, im Root-`CLAUDE.md` benannte Grenze.
- Verifizierbar durch mich sind ausschließlich: (a) der erfolgreiche, fehlerfreie Lauf des
  Generators (`generator3.cpython-39.pyc`) zu einer importierbaren `.hsl`-Datei, und (b) das
  Bestehen der in Abschnitt 7 beschriebenen `pytest`-Suite gegen die reine Python-Logik.
- Der Differenztest (7.6) belegt Gleichheit gegenüber der **dokumentierten** Legacy-Semantik,
  nicht gegenüber der echten Firmware-Engine des alten Bausteins.
- Die pytest-Suite prüft die **Entscheidungslogik**, nicht das reale Zusammenspiel mit
  Motorsteuerung, Sonnepur-Timing oder Bus-Latenzen. Restrisiken (z. B. reales Timing-Verhalten
  der Lamellen-Rückmeldung, siehe ADR-007 "Negativ/Risiken") bleiben nur durch echten
  Hardwaretest querprüfbar — das ist explizit ein akzeptiertes Verifikationsloch dieses Plans.

---

## 9. Offene Punkte, die in die Umsetzung mitgenommen werden müssen

- **OQ-03** (`anforderungen.md`): Mehrfachinstanz-Unterstützung — da SN-Register künftig
  instanzlokale `store`-Slots sind (kein globaler Zustand), ist Mehrfachinstanzfähigkeit
  strukturell weiterhin gegeben; sollte im Umsetzungsschritt kurz verifiziert werden.
- **OQ-02**: Kein dokumentierter Wert für die maximale reale Fahrzeit — der 180-s-Timeout wird
  unverändert 1:1 übernommen, ohne ihn fachlich zu validieren (außerhalb des Scopes dieser
  Migration).
- **TD-01** (`SN[4]` diagnostisch, ungenutzt): wird in Phase 1 unverändert mitgeführt, nicht
  bereinigt — Verhaltenstreue hat Vorrang vor Aufräumen. Bereinigung ist Kandidat für Phase 2
  (Abschnitt 11).
- **Sendeverhalten der Ausgänge:** Legacy deklariert Ausgänge 1 und 4 als "senden bei
  Änderung". Ob HSL3s `set_output` bei unverändertem Wert erneut sendet, ist in der SDK-Doku
  nicht beschrieben. Phase 1 bildet "senden bei Änderung" für diese beiden Ausgänge daher
  explizit im Code nach (letzten gesendeten Wert merken), statt sich auf ein Framework-Verhalten
  zu verlassen.
- **arc42 §09 ist veraltet** (ADR-007/008 fehlen dort) — Aktualisierung von `old/docs/arc42/09-architecture-decisions.md`
  wurde nicht angefordert und ist nicht Teil dieses Plans; nur zur Kenntnis genommen.
- Exakte Kategorie-/Label-Texte in `config_shadepilot.json` (Abschnitt 6) sind ein Entwurf und
  sollten bei Umsetzung final mit dem Nutzer abgestimmt werden (z. B. GLE-Kategoriename).

---

## 10. Nächste Schritte Phase 1 (nach Freigabe dieses Plans)

Reihenfolge bewusst "Sicherheitsnetz zuerst":

1. Neue Modul-ID (Vorschlag `10801`) in der Root-`CLAUDE.md`-Tabelle "Vergebene Modul-IDs"
   eintragen.
2. `tests/fakes.py`, `tests/harness.py` und `tests/legacy_reference.py` anlegen;
   Referenz-Interpreter gegen die Szenarien aus 7.2 selbst prüfen (7.6 "Selbsttest").
3. `config_shadepilot.json` gemäß Abschnitt 6 final anlegen.
4. `hsl3_10801_shadepilot.py` mit `LogicModule` gemäß Abschnitt 4 und 5 implementieren.
5. `tests/test_scenarios.py`, `tests/test_adr_regressions.py`, `tests/test_differential.py`
   implementieren. **Abschlusskriterium Phase 1:** alle Black-Box-Tests grün, Differenztest ohne
   Abweichung (bzw. nur mit vom Nutzer abgenommenen Ausnahmen).
6. Generator-Lauf (`generator3.cpython-39.pyc --source ... --target dist/10801_shadepilot.hsl --debug`)
   verifizieren (fehlerfreier Durchlauf, siehe Abschnitt 8 für die Grenze dieser Prüfung).
7. Verifikation im Experte/GLE und auf der Hardware durch den Nutzer — außerhalb meiner
   Möglichkeiten. Dieser Stand ist die abgenommene Referenz für Phase 2.

Dieser Plan wird **nicht automatisch umgesetzt** — Schritt 1 ff. beginnt erst nach expliziter
Freigabe durch den Nutzer.

---

## 11. Phase 2: Refactoring bei gleichem Verhalten

### 11.1 Ziel

Nach abgenommener Phase 1 wird die interne Struktur modernisiert: lesbarer, fachlich benannt,
weniger Duplikation. Das beobachtbare Verhalten (Ausgänge 1–5, Timer-Aktionen) bleibt gleich.

### 11.2 Sicherheitsnetz

- **Unverändert bleiben:** `test_scenarios.py`, `test_adr_regressions.py`,
  `test_differential.py`, `harness.py`, `fakes.py`, `legacy_reference.py`. Wer in Phase 2 einen
  dieser Tests ändern muss, ändert Verhalten — das ist dann kein Refactoring mehr und wird
  separat entschieden.
- **Verwerfbar:** `test_steps.py` (Hilfstests der internen `_stepN`-Methoden).
- Refactoring in kleinen Schritten, nach jedem Schritt komplette Suite grün.
- Die Konfiguration (`config_shadepilot.json`: Identifier und Reihenfolge von Ein-/Ausgängen)
  bleibt stabil, damit bestehende Verknüpfungen im GPA-Projekt nicht brechen. Store-Identifier
  dürfen sich ändern (siehe 11.4).

### 11.3 Refactoring-Kandidaten (Vorschläge, Reihenfolge = empfohlene Abfolge)

1. **Fachliche Benennung:** `_stepN`-Methoden und lokale Variablen nach Fachbegriffen
   (`_berechne_lamellen_sollwert`, `_erkenne_manuellen_eingriff`, …) statt Abschnittsnummern.
2. **Gerätetyp als Enum** (`Geraetetyp.JALOUSIE` / `RAFFSTORE`), einmal pro Pass aus
   `EN[12]` abgeleitet statt verstreuter `== 0`/`> 0`-Prüfungen (ADR-001 bleibt inhaltlich
   gleich).
3. **Flankenerkennung kapseln:** kleine Hilfsklasse (z. B. `Flanke` mit `geaendert`,
   `vorher`, `steigend`), statt fünf lose `_prev_...`-Attribute.
4. **Duplikation Jalousie/Raffstore auflösen:** die fast identischen Regelpaare in den
   Abschnitten 4, 5 und 9 zu parametrisierten Pfaden zusammenführen.
5. **Explizite Zustandsmaschine:** `SN[5]`/`SN[6]` beschreiben zusammen einen Modus
   (Automatik / Manuell-Vorrang / Abfahrt, siehe arc42 §08 stateDiagram). Diesen als Enum mit
   benannten Übergängen modellieren; die Guards aus ADR-004/005/007 werden zu sprechenden
   Übergangsbedingungen.
6. **`SN[4]` bereinigen (TD-01):** steuert nichts, wird aber von Ausgang 5 und dem Statustext
   gelesen. Der Wert wird daher nicht gelöscht, sondern nur noch dort berechnet, wo diese
   beiden Ausgänge ihn brauchen; der eigene Store entfällt.
7. **Konstanten benennen:** `TOLERANZ_BEHANG_PROZENT = 3`, `ENDLAGE_SCHWELLE = 98`,
   `ENDLAGE_FLANKE = 99`, `ABFAHRT_TIMEOUT_S = 180`, statt Magic Numbers.
8. **Typannotationen und Docstrings** in knapper Form; Python-3.9-kompatibel (keine
   `match`-Anweisung, keine `X | Y`-Typsyntax).

### 11.4 Bewusst getrennte, verhaltensändernde Punkte

Folgende Punkte sind **kein** Refactoring, weil sie beobachtbares Verhalten ändern. Sie werden
nicht nebenbei umgesetzt, sondern nur einzeln nach Freigabe, jeweils mit angepasstem Test:

- Store-Remanenz über Neustart nutzen (statt Reset in `on_init`, Abschnitt 4.3).
- Format des Statustexts (Ausgang 4) modernisieren.
- Aufräumen der Store-Liste (Identifier/Anzahl) — ändert nichts an den Ausgängen, verwirft
  aber beim Update gespeicherte Werte im Experte; daher kurz mit dem Nutzer abstimmen.
- Fachliche Änderungen wie ein konfigurierbarer Gerätetyp oder ein validierter Timeout
  (OQ-02).

### 11.5 Abschluss Phase 2

Suite grün (ohne Änderung an den Black-Box- und Differenztests), Generator-Lauf fehlerfrei,
danach **erneuter Test im Experte und auf der Hardware** durch den Nutzer — die Tests prüfen nur
die Entscheidungslogik, nicht das reale Timing (Abschnitt 8).
