# CLAUDE.md

Diese Datei gibt Claude Code (claude.ai/code) Orientierung beim Arbeiten in diesem Repository.

## Modellwahl

Nutze standardmäßig Sonnet 5. Wechsle zu Opus 4.8 nur, wenn Sonnet nach zwei Versuchen nicht ausreicht. Effort Level Medium.

## Projektübersicht

Dieses Repository enthält einen Gira Homeserver-Baustein in HSL (Homeserver Script Language), dem proprietären Skriptformat für Gira-Automatisierungssysteme. Der Baustein implementiert die **Jalousie Lamellennachführung** — automatische Sonnenstandsnachführung für verstellbare Jalousien mit Lamellenwinkel-Positionierung und Manuell-Vorrang-Erkennung.

Es gibt keinen Build-Prozess, keinen Paketmanager und keine Testsuite. Die `.hsl`-Datei wird direkt über das GPA (Gira Project Assistant) auf den Homeserver geladen und dort ausgeführt.

## HSL-Dateiformat

Jede Zeile verwendet ein pipe-getrenntes Format. Wichtige Opcodes:

| Opcode | Bedeutung |
|--------|-----------|
| `5000` | Baustein-Header: ID, Name, Version, Ein-/Ausgabe-Deklarationen |
| `5001` | Baustein-Parameter |
| `5002\|N\|Standard\|0` | Eingang EN[N] mit Standardwert |
| `5003\|N\|Standard\|0` | Interner Speicher SN[N] mit Standardwert |
| `5004\|N\|...\|Typ\|0` | Ausgang EA[N]/EC[N] |
| `5012\|0\|"Bedingung"\|"Wert"\|"Timeout"\|out_idx\|0\|sn_idx\|0` | Logikrege |

**5012-Logikregeln** bilden den Kern des Bausteins. Eine Regel wird ausgeführt, wenn ihre Bedingung wahr ist, und setzt dann einen Speicher- oder Ausgangswert. Der optionale Timeout-Wert gibt Sekunden an. Die letzten beiden numerischen Felder bestimmen das Ziel: `out_idx` adressiert einen Ausgang (EA/EC), `sn_idx` adressiert einen Speicher (SN).

## Variablenreferenz

**Eingänge (EN)**:
- `EN[1]` — Sonnen-Inklination (%, Trigger ca. alle 2 Min. von Sonnepur)
- `EN[2]` — Beschattung Ein/Aus (1=Ein)
- `EN[3]` — Zyklus Ein/Aus
- `EN[4]` — Mindeständerung / Toleranz (%)
- `EN[5]` — Lamellenstellung waagrecht (%)
- `EN[6]` — Lamellenstellung senkrecht (%)
- `EN[7]` — Lamellenstellung bei Beschattung Aus (%)
- `EN[8]` — Offset Lamellenwinkel +/- (%)
- `EN[9]` — Behang-Zielposition bei Sonnenschutz (%)
- `EN[10]` — Behang IST-Position (%)
- `EN[11]` — Steuerung Behang (1 = Behang AUF bei Beschattung AUS)
- `EN[12]` — Lamelle IST-Position (%). **0 bei Jalousien** (kein Lamellenrückmeldung), **>0 bei Raffstoren** (Lamellenposition bekannt). Dieser Wert unterscheidet im Code grundlegend zwischen den beiden Gerätetypen.

**Interner Zustand (SN)**:
- `SN[1]` — Zuletzt gesendeter Lamellen-Sollwert (für Schwellwertvergleich)
- `SN[2]` — Aktuell berechneter Lamellen-Sollwert
- `SN[3]` — Flag: Behang in Zielposition (1 = ja, Toleranz ±3%)
- `SN[4]` — Flag: Lamelle weicht vom Sollwert ab (1 = ja)
- `SN[5]` — Automatik-Flag (1 = aktiv, 0 = Manuell-Vorrang)
- `SN[6]` — Abfahrt-Flag (1 = Behang/Lamelle fährt; Manuell-Erkennung pausiert)
- `SN[7]` — Lamellen-Zielwert während der Abfahrt (für Reset-Prüfung)

**Ausgänge**:
- Ausgang 1 (`sbC`) — Lamellen-Sollwert (%)
- Ausgang 2 (`send`) — Behang-Sollwert (%)
- Ausgang 3 — Auf/Ab-Befehl
- Ausgang 4 — Statustext (Debug-String mit allen SN-Werten)
- Ausgang 5 — Zwangsführung-Statuscode für die Visu (2-Bit-Wert, kein 1:1-Mirror von `SN[5]`): `0` = keine Automatik im Fenster aktiv (`EN[3]==0`, oder `SN[5]==0`/Manuell-Vorrang, oder Raffstore-Lamelle noch nicht in Ruheposition); `3` = Automatik aktiv bei Beschattung Ein (`EN[2]==1 and SN[5]>0`); `2` = Automatik aktiv, Beschattung Aus und Lamelle in Ruheposition, nur für Raffstore (`EN[2]==0 and EN[12]>0 and SN[4]==0 and SN[5]>0`) — bei Jalousie (`EN[12]==0`) wird `2` nie ausgegeben, da keine Lamellen-Rückmeldung zur Bestätigung der Ruheposition existiert.

**Flanken-/Änderungs-Trigger in Bedingungen**:
- `EC[N]` — wahr in dem Zyklus, in dem sich EN[N] ändert
- `EA[N]` — vorheriger Wert von EN[N]

## Logik-Architektur

Der Baustein ist in funktionale Abschnitte gegliedert, die pro Zyklus von oben nach unten ausgewertet werden:

1. **Sollwertberechnung** — Berechnet `SN[2]` aus der Inklinationsformel oder dem Ruhewert; begrenzt auf `[EN[5], EN[6]]`
2. **Positions-Flags** — Aktualisiert `SN[3]` (Behang in Zielposition) und `SN[4]` (Lamellen-Abweichung)
3. **Manuell-Vorrang-Erkennung** — Löscht `SN[5]`, wenn die Lamellen-IST-Position die Toleranz gegenüber `SN[2]` überschreitet; ausgenommen Endlagen (≥98%), Umschaltzeitpunkte (`not EC[2]`) und Sonnenstand-Sprünge (`not EC[1]`); nur wenn keine Abfahrt läuft (`SN[6]==0`)
4. **Behang-Automatik** — Bei Zyklus-Trigger (`EC[3]`): fährt Behang auf `EN[9]`. **Jalousie (`EN[12]==0`)**: Abfahrt nur wenn `EN[10] < EN[9]` (Behang noch unterhalb der Zielposition). **Raffstore (`EN[12]>0`)**: Abfahrt immer wenn `SN[3]==0` (Behang nicht in Zielposition). Setzt Abfahrt-Flag `SN[6]`, speichert Lamellen-Zielwert in `SN[7]`; bei Zyklus-Aus: Behang AUF. Zusätzlich wird bei jedem Zyklus-Start `SN[5]` **unconditional** (unabhängig von `SN[3]`) auf 1 zurückgesetzt (siehe ADR-008).
5. **Lamellennachführung bei Behang-Ankunft** (`EC[10]`) — Wenn der Behang die Zielposition erreicht (±3%), wird die Lamelle auf den berechneten Sollwert gefahren; behandelt Beschattung-Ein, Beschattung-Aus und den Jalousie-Sonderfall (`EN[12]==0`)
6. **Abfahrt-Flag zurücksetzen** — Löscht `SN[6]`, wenn die Lamelle die 100%-Endlage verlässt, oder wenn der Behang ankommt und kein Lamellen-Feedback vorliegt
7. **Lamellennachführung bei Inklinationsänderung** (`EC[1]`) — Passt Lamellenwinkel an, wenn sich der Sonnenstand ändert; nur bei aktiver Automatik und Überschreitung des Mindeständerungs-Schwellwerts
8. **Lamellennachführung bei Beschattungsänderung** (`EC[2]`) — Fährt Lamelle sofort auf neuen Sollwert, wenn Beschattung umschaltet
9. **Manuell-Vorrang-Rücknahme** — Setzt `SN[5]=1` zurück, wenn IST-Lamelle/-Behang wieder innerhalb der Toleranz des Sollwerts liegt
10. **Timeout** — Löscht `SN[6]` automatisch nach 180 Sekunden als Sicherheitsfallback
11. **Statustext** — Immer feuernde Regel, die einen Debug-String aller SN-Werte auf Ausgang 4 schreibt

## Wichtige Designentscheidungen

- **`SN[6]` (Abfahrt-Flag)** schützt die Manuell-Erkennung: Manuelle Eingriffe werden nur erkannt, wenn keine Abfahrt läuft. Der Reset erfolgt erst nach Abschluss der Lamellenbewegung, nicht sofort bei Behang-Ankunft.
- **Endlagen-Ausschluss**: `EN[12]<98` verhindert, dass die 100%-Einfahrposition als manueller Eingriff fehlinterpretiert wird.
- **`not EC[2]`**: Unterdrückt die Manuell-Erkennung genau in dem Zyklus, in dem die Beschattung umschaltet (Übergangsmaskierung).
- **`not EC[1]`**: Analoge Übergangsmaskierung für den Sonnenstand-Sprung. `SN[2]` wird jeden Zyklus live aus der Inklination berechnet; wenn `EC[1]` feuert, springt `SN[2]` im selben Zyklus auf den neuen Wert, während `EN[12]` (Lamelle IST) noch die alte Position zeigt. Ohne `not EC[1]` würde die Manuell-Erkennung (Abschnitt 3) genau in diesem Zyklus `SN[5]` löschen, bevor die eigentliche Korrektur in Abschnitt 7 (Lamellennachführung bei Inklinationsänderung) überhaupt geprüft wird — die Automatik würde sich bei jeder Sonnenstandsänderung selbst deaktivieren (siehe ADR-007).
- **Jalousie vs. Raffstore**: `EN[12]==0` kennzeichnet eine Jalousie (kein Lamellen-Feedback), `EN[12]>0` einen Raffstore. Dieser Wert steuert an mehreren Stellen das Verhalten: bei der Behang-Automatik (Jalousie fährt nur ab wenn `EN[10]<EN[9]`, Raffstore immer bei Abweichung), bei der Lamellennachführung (Jalousie-Sonderfall in EC[10]) und bei der Manuell-Vorrang-Erkennung.
- Lamellen-Sollwertformel: `round(((90 - Inklination) * (EN[6] - EN[5]) / 90) + EN[5] + EN[8])`
- **Unconditional `SN[5]`-Reset bei Zyklus-Start**: `SN[3]` (Behang in Zielposition) wird jeden Zyklus unconditional aus `abs(EN[9]-EN[10])<=3` berechnet (Abschnitt 2) — bleibt der Behang aus irgendeinem Grund (z. B. fehlende Verknüpfung von Ausgang 3 im GPA-Projekt) über Nacht stehen und diese Position erfüllt zufällig die Toleranz, ist `SN[3]==1`, obwohl keine reguläre Zielfahrt stattgefunden hat. Die ursprüngliche Zyklus-Start-Regel für `SN[5]=1` (Abschnitt 4) war an `SN[3]==0` gekoppelt und feuerte dann nicht — `SN[5]` blieb dauerhaft auf 0 hängen, keine Lamellennachführung am nächsten Tag. Fix: eine zusätzliche, von `SN[3]` unabhängige Regel setzt `SN[5]` bei jedem Zyklus-Start (`EC[3] and EN[3]==1 and EA[3]==0`) unconditional auf 1 zurück (siehe ADR-008).

## Zeichenkodierung

Die `.hsl`-Datei verwendet **ISO-8859-1** (Latin-1). Umlaute (ä, ö, ü, ß) sind als Latin-1-Bytes gespeichert. Beim Bearbeiten diese Kodierung beibehalten — nicht als UTF-8 speichern, außer die eingesetzte Homeserver-Version unterstützt das explizit.


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
