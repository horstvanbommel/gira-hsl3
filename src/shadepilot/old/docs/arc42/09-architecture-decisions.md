# §09 Architekturentscheidungen

Alle Entscheidungen liegen als vollständige ADR-Dokumente unter
`SourceDocuments/adr/` vor. Diese Sektion enthält eine Übersicht mit
Kurzbegründungen und Verweisen.

---

## Entscheidungsübersicht

| ADR | Titel | Status | Datum | Betroffene Sektionen |
|-----|-------|--------|-------|---------------------|
| [ADR-001](../../SourceDocuments/adr/ADR-001-jalousie-raffstore-geraetetyp.md) | Jalousie/Raffstore-Gerätetyp-Unterscheidung über EN[12] | Accepted | pre-03/2026 | §01, §05, §06 |
| [ADR-002](../../SourceDocuments/adr/ADR-002-sn6-abfahrt-flag.md) | SN[6] Abfahrt-Flag schützt die Manuell-Vorrang-Erkennung | Accepted | 03/2026 | §05, §06, §08 |
| [ADR-003](../../SourceDocuments/adr/ADR-003-sn6-reset-zeitpunkt.md) | SN[6] Reset erst nach Lamellenbewegung, nicht sofort bei Behang-Ankunft | Accepted | 03/2026 | §05, §06 |
| [ADR-004](../../SourceDocuments/adr/ADR-004-endlagen-ausschluss.md) | Endlagen-Ausschluss (EN[12] < 98) in der Manuell-Vorrang-Erkennung | Accepted | 03/2026 | §05 |
| [ADR-005](../../SourceDocuments/adr/ADR-005-ec2-uebergangsmaskierung.md) | EC[2] Übergangsmaskierung für Manuell-Vorrang-Erkennung | Accepted | pre-03/2026 | §05, §06 |
| [ADR-006](../../SourceDocuments/adr/ADR-006-jalousie-initiale-abfahrt.md) | Jalousie — Initiale Abfahrt nur wenn EN[10] < EN[9] | Accepted | 04/2026 | §05, §06 |

---

## ADR-001: Jalousie/Raffstore-Unterscheidung via EN[12]

**Kernentscheidung:** `EN[12]` (Lamelle IST-Position) dient gleichzeitig als Gerätetyp-Diskriminator:
`EN[12]==0` → Jalousie, `EN[12]>0` → Raffstore. Ein separater Typ-Eingang entfällt.

**Begründung:** Jalousien liefern per Definition kein Lamellen-Feedback (EN[12] bleibt 0), sodass
der Wert die Geräteeigenschaft korrekt widerspiegelt ohne zusätzlichen Eingang zu benötigen.

**Hauptrisiko:** Versehentlicher Bus-Wert auf EN[12] einer Jalousie schaltet fälschlicherweise
in den Raffstore-Modus.

---

## ADR-002: SN[6] Abfahrt-Flag

**Kernentscheidung:** Während einer automatischen Abfahrt (`SN[6]=1`) ist die Manuell-Vorrang-Erkennung
deaktiviert. Fallback-Timeout: 180 Sekunden.

**Begründung:** Ohne diesen Schutz würde jede Motorposition während der eigenen Abfahrt als manueller
Eingriff interpretiert und `SN[5]` fälschlicherweise löschen.

---

## ADR-003: SN[6] Reset-Zeitpunkt

**Kernentscheidung:** `SN[6]` wird nicht beim Behang-Ankommen (`EC[10]`) zurückgesetzt, sondern erst
wenn die Lamelle die Endlage verlässt (`EC[12]` + `EN[12]<98` für Raffstore) oder der Behang ankommt
und kein Feedback vorliegt (Jalousie).

**Begründung:** Frühzeitiger Reset reaktiviert die Manuell-Erkennung während laufender Lamellenbewegung,
was zu Falsch-Auslösungen führt (beobachteter Fehler, korrigiert in 03/2026).

**Supersedes:** Reset-Verhalten vor 03/2026.

---

## ADR-004: Endlagen-Ausschluss

**Kernentscheidung:** Manuell-Erkennung prüft nur `EN[12]<98`. Werte ≥ 98 % (Endlage) werden ignoriert.

**Begründung:** Nach einer Abfahrt steht die Lamelle kurz in 100%-Position, die weit vom Sollwert
abweicht — ohne diesen Ausschluss würde das als manueller Eingriff erkannt.

---

## ADR-005: EC[2] Übergangsmaskierung

**Kernentscheidung:** `not EC[2]` in allen Manuell-Erkennungsregeln unterdrückt die Erkennung genau
in dem Zyklus, in dem die Beschattung umschaltet.

**Begründung:** Im Umschaltzyklus ändert sich `SN[2]` sprunghaft, während `EN[12]` noch den alten
Wert hält — ohne Maskierung wird dies als manueller Eingriff fehlinterpretiert.

---

## ADR-006: Jalousie Initiale Abfahrt

**Kernentscheidung:** Für Jalousien (`EN[12]==0`) fährt der Baustein nur ab, wenn `EN[10]<EN[9]`
(Behang noch unterhalb der Zielposition). Für Raffstoren bleibt die Bedingung symmetrisch (`SN[3]==0`).

**Begründung:** Ohne Lamellenrückmeldung muss der Baustein konservativer handeln; eine Abfahrt bei
überschrittener Zielposition wäre unnötig und könnte manuell platzierte Behänge stören.

**Supersedes:** Verhalten vor 04/2026 ohne Richtungsprüfung.

---

## Supersession-Kette

| Früheres Verhalten | Abgelöst durch | Zeitpunkt |
|-------------------|---------------|-----------|
| SN[6] Reset bei EC[10] | ADR-003 | 03/2026 |
| Keine Endlagenausnahme | ADR-004 | 03/2026 |
| Jalousie-Abfahrt ohne Richtungsprüfung | ADR-006 | 04/2026 |

---

*Siehe auch:* [§04 Lösungsstrategie](04-solution-strategy.md) |
[§05 Bausteinsicht](05-building-block-view.md) | [§06 Laufzeitsicht](06-runtime-view.md)
