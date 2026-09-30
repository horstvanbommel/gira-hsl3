# §01 Einführung und Ziele

(Source: CLAUDE.md § Projektübersicht; SourceDocuments/SpecsAndRequirments/anforderungen.md)

---

## Aufgabenstellung

Der Baustein **Jalousie Lamellennachführung** (HSL-Baustein, ID 19822, Version 3.2.5) implementiert
die automatische Sonnenstandsnachführung für [Jalousien](12-glossary.md) und [Raffstoren](12-glossary.md)
am Gira Homeserver.

**Kernfunktion:** Der Baustein empfängt die aktuelle Sonnen-[Inklination](12-glossary.md) vom externen
Dienst [Sonnepur](12-glossary.md) (ca. alle 2 Minuten) und berechnet daraus den optimalen
[Lamellen](12-glossary.md)winkel. Er steuert [Behang](12-glossary.md) und Lamellen so, dass optimaler
Sonnenschutz bei minimalem Lichtverlust erreicht wird.

**Warum Automatisierung:** Sonnenstand und Schattenfall ändern sich kontinuierlich. Eine manuelle
Neueinstellung der Lamellenposition alle 2 Minuten ist für Bewohner nicht zumutbar; die Automatisierung
macht dauerhaft optimalen Sonnenschutz erst praktikabel.

**Manuell-Vorrang:** Weicht die tatsächliche Lamellenposition vom berechneten Sollwert ab (weil der
Benutzer manuell eingegriffen hat), deaktiviert der Baustein die Automatik und respektiert die manuell
gewählte Stellung. Die Automatik stellt sich selbst wieder her, sobald die Lamelle in den Sollwertbereich
zurückkehrt.
(Source: CLAUDE.md § Projektübersicht)

---

## Qualitätsziele

Die wichtigsten Qualitätsziele in absteigender Priorität:

| Priorität | Qualitätsziel | Szenario |
|-----------|--------------|---------|
| 1 | **Korrektheit** — Manuell-Vorrang wird zuverlässig erkannt und nicht durch Automatikbewegungen ausgelöst | Der Baustein löst keine Abfahrt aus, während er selbst eine Bewegung durchführt; keine Falsch-Erkennung beim Umschalten der Beschattung oder in der Endlage |
| 2 | **Sicherheit** — Kein dauerhaftes Einfrieren des Betriebs | Ein laufender Abfahrt-Vorgang wird spätestens nach 180 Sekunden automatisch zurückgesetzt, auch wenn das normale Feedback ausbleibt (NF-01) |
| 3 | **Gerätekompatibilität** — Einheitlicher Baustein für zwei physisch unterschiedliche Gerätetypen | Derselbe Baustein funktioniert korrekt für Jalousien (kein Lamellen-Feedback) und Raffstoren (mit Lamellen-Feedback), konfiguriert über einen einzigen Eingang (ADR-001; NF-03) |

---

## Stakeholder

(Source: SourceDocuments/SpecsAndRequirments/anforderungen.md § Stakeholder)

| Rolle | Interesse am System |
|-------|-------------------|
| **Bewohner / Nutzer** | Komfortabler Sonnenschutz ohne manuellen Eingriff; eigene Lamellenverstellungen sollen dauerhaft respektiert werden |
| **Integrator / Installateur** | Einfache Konfiguration im GPA; klare Parameterbeschreibungen; keine unerwarteten oder ungewollten Bewegungen nach der Inbetriebnahme |
| **Gira Homeserver (Plattform)** | Korrekte Einbindung als HSL-Baustein; Kompatibilität mit GPA-Upload und dem Automatisierungsbus |

---

## Abgrenzung

Folgende Funktionen liegen **außerhalb** des Bausteins:
- Wetterbedingte Übersteuerung (Wind, Regen) — Verantwortung separater Bausteine
- Gruppensteuerung mehrerer Jalousien — jede Jalousie hat eine eigene Baustein-Instanz
- Persistenz des Automatik-Flags über Homeserver-Neustarts hinaus

(Source: SourceDocuments/SpecsAndRequirments/anforderungen.md § Ausgeschlossene Anforderungen)

---

*Siehe auch:* [§03 Kontext und Abgrenzung](03-context-and-scope.md) | [§10 Qualitätsanforderungen](10-quality-requirements.md)
