# §12 Glossar

(Source: CLAUDE.md § Variablenreferenz; ADR-001; SourceDocuments/SpecsAndRequirments/anforderungen.md)

---

## Fachliche Begriffe

| Begriff | Definition |
|---------|-----------|
| **Jalousie** | Innenjalousie mit horizontalen Lamellen. Kein Lamellen-Positions-Feedback über den Gira-Bus; `EN[12]` bleibt dauerhaft 0. (ADR-001) |
| **Raffstore** | Außenjalousie (Markisolette) mit verstellbaren Lamellen und Positions-Feedback; `EN[12]` meldet die IST-Position aktiv. (ADR-001) |
| **Lamelle** | Einzelner Lamellenstab einer Jalousie oder eines Raffstores; das Element, dessen Winkel durch den Baustein gesteuert wird. |
| **Behang** | Der gesamte Vorhang-/Bedeckungsbestand (alle Lamellen als Einheit), im Unterschied zu einzelnen Lamellen. Wird über `EN[10]` als IST-Position und `EN[9]` als Zielposition beschrieben. |
| **Inklination** | Sonnenelevationswinkel (0–90°), vom Baustein als Prozentwert empfangen (`EN[1]`). 0 % = Sonne am Horizont, 90 % = Sonne im Zenit. |
| **Abfahrt** | Motorgesteuerte Bewegung des Behangs auf eine Zielposition. Während einer Abfahrt ist das Abfahrt-Flag (`SN[6]`) gesetzt. |
| **Endlage** | Endposition des Behangs oder der Lamelle. Hier relevant: 100 % = vollständig eingezogen/geschlossen. Werte ≥ 98 % gelten als Endlage (ADR-004). |
| **Manuell-Vorrang** | Zustand, in dem der Benutzer die Lamelle oder den Behang manuell verstellt hat; die Automatik ist deaktiviert (`SN[5]=0`). Wird automatisch aufgehoben, wenn die IST-Position wieder in den Sollwertbereich zurückkehrt. |
| **Sonnepur** | Externer Gira-Homeserver-Dienst, der den Sonnenstand berechnet und die Inklination etwa alle 2 Minuten an verbundene Bausteine sendet. (CLAUDE.md § Variablenreferenz) |
| **GPA** | Gira Project Assistant — die proprietäre Entwicklungsumgebung und das Upload-Tool für Gira-Homeserver-Bausteine. |
| **Sollwert** | Ziel-/Steuerwert, den der Baustein berechnet und an die Motorsteuerung ausgibt. |
| **IST / Istwert** | Aktuell gemessener Wert eines Sensors oder der Motorpositionsrückmeldung. |

---

## HSL- und Laufzeit-Begriffe

| Begriff | Definition |
|---------|-----------|
| **HSL** | Homeserver Script Language — das proprietäre, pipe-getrennte Regelformat des Gira Homeservers. |
| **5012-Regel** | Der zentrale HSL-Opcode für Logikregeln: `5012\|0\|"Bedingung"\|"Wert"\|"Timeout"\|out_idx\|0\|sn_idx\|0`. Feuert, wenn die Bedingung wahr ist; setzt dann einen Ausgang (`out_idx`) oder Speicher (`sn_idx`). (CLAUDE.md § HSL-Dateiformat) |
| **EN[N]** | Eingang (Eingabe-Register) N — liest Werte vom Gira-Automatisierungsbus. |
| **SN[N]** | Speicher (Storage-Register) N — interner flüchtiger Zustandsspeicher; wird pro Zyklus oben nach unten ausgewertet, nicht über Homeserver-Neustarts hinweg persistiert. |
| **EC[N]** | Flanken-/Änderungs-Trigger — wahr genau in dem Zyklus, in dem sich `EN[N]` ändert. Danach wieder falsch. (CLAUDE.md § Variablenreferenz) |
| **EA[N]** | Vorheriger Wert von `EN[N]` aus dem vorangegangenen Zyklus. |
| **Automatik-Flag** | `SN[5]`: 1 = Automatik aktiv, 0 = Manuell-Vorrang aktiv. |
| **Abfahrt-Flag** | `SN[6]`: 1 = Behang oder Lamelle fährt gerade (Manuell-Erkennung pausiert), 0 = keine Abfahrt aktiv. (ADR-002) |
| **Lamellen-Sollwertformel** | `round(((90 - EN[1]) * (EN[6] - EN[5]) / 90) + EN[5] + EN[8])` — berechnet den optimalen Lamellenwinkel aus Sonneninklination und konfigurierten Grenzwerten. (CLAUDE.md § Designentscheidungen) |
| **sbC / sBC / send** | Gira-interne Kennungen für analoge Ausgangs-Signaltypen. |

---

## Eingänge (EN) — Kurzreferenz

| Register | Beschreibung | Typ |
|----------|-------------|-----|
| `EN[1]` | Sonnen-Inklination (%) — Trigger von Sonnepur ca. alle 2 Min. | Analogwert |
| `EN[2]` | Beschattung Ein (1) / Aus (0) | Binär |
| `EN[3]` | Zyklus Ein (1) / Aus (0) — aktiviert Behang-Automatik | Binär |
| `EN[4]` | Mindeständerung / Toleranz (%) für Manuell-Erkennung und EC[1]-Schwelle | Analogwert |
| `EN[5]` | Lamellenstellung waagrecht (%) — untere Grenze | Analogwert |
| `EN[6]` | Lamellenstellung senkrecht (%) — obere Grenze | Analogwert |
| `EN[7]` | Lamellenstellung bei Beschattung Aus (%) — Ruheposition | Analogwert |
| `EN[8]` | Offset Lamellenwinkel +/- (%) | Analogwert |
| `EN[9]` | Behang-Zielposition bei Sonnenschutz (%) | Analogwert |
| `EN[10]` | Behang IST-Position (%) | Analogwert |
| `EN[11]` | Steuerung Behang: 1 = Behang AUF bei Beschattung AUS | Binär |
| `EN[12]` | Lamelle IST-Position (%); **0 bei Jalousie**, **>0 bei Raffstore** | Analogwert / Typ-Diskriminator |

## Speicher (SN) — Kurzreferenz

| Register | Beschreibung |
|----------|-------------|
| `SN[1]` | Zuletzt gesendeter Lamellen-Sollwert (für EC[1]-Schwellwertvergleich) |
| `SN[2]` | Aktuell berechneter Lamellen-Sollwert |
| `SN[3]` | Flag: Behang in Zielposition (1 = ja, Toleranz ±3 %) |
| `SN[4]` | Flag: Lamelle weicht vom Sollwert ab (1 = ja; derzeit nur diagnostisch genutzt) |
| `SN[5]` | Automatik-Flag: 1 = aktiv, 0 = Manuell-Vorrang |
| `SN[6]` | Abfahrt-Flag: 1 = Behang/Lamelle fährt, Manuell-Erkennung pausiert |
| `SN[7]` | Lamellen-Zielwert während der Abfahrt (für Reset-Prüfung) |
