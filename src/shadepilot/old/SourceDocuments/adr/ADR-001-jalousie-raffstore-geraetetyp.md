# ADR-001: Jalousie/Raffstore-Gerätetyp-Unterscheidung über EN[12]

**Status:** Accepted
**Datum:** vor 03/2026 (Originaldesign)
**Autor:** Matthias Schmidt (original), angepasst für gira-hs

---

## Kontext

Der Baustein soll zwei physisch unterschiedliche Gerätetypen steuern:

- **Jalousie** (Innenjalousie): Lamellen sind vorhanden, aber kein Positions-Feedback über den Bus.
- **Raffstore** (Außenjalousie): Lamellen sind vorhanden und melden ihre IST-Position zurück.

Beide Typen teilen dieselbe Grundlogik (Sonnenstandsnachführung, Manuell-Vorrang), unterscheiden sich aber in der Manuell-Erkennungslogik, der Initialen-Abfahrt-Bedingung und der Lamellennachführung bei Behang-Ankunft.

Der Baustein hat eine feste Anzahl von Eingängen; ein separater Typ-Schalter würde einen zusätzlichen Eingang kosten.

---

## Entscheidung

`EN[12]` (Lamelle IST-Position) dient gleichzeitig als Gerätetyp-Diskriminator:

- `EN[12] == 0` → Jalousie (kein Lamellenrückmeldung; der Wert bleibt dauerhaft 0)
- `EN[12] > 0` → Raffstore (die Lamellenposition wird aktiv gemeldet)

Ein expliziter Typ-Eingang entfällt. Der Wert 0 ist für eine Jalousie ohnehin korrekt (keine Messung vorhanden), sodass kein zusätzlicher Konfigurationsschritt nötig ist.

---

## Konsequenzen

**Positiv:**
- Kein zusätzlicher Eingang für den Gerätetyp nötig.
- Die Unterscheidung ist implizit korrekt: Jalousien liefern per Definition kein Signal auf EN[12].
- Bestehende Konfigurationen müssen nicht angepasst werden.

**Negativ/Risiken:**
- Das Verhalten unterscheidet sich je nach EN[12], ohne dass ein expliziter Typ-Parameter im GPA sichtbar ist. Integratoren müssen wissen, dass EN[12]==0 die Jalousie-Logik aktiviert.
- Falls eine Jalousie-Konfiguration versehentlich einen Wert auf EN[12] sendet, schaltet der Baustein fälschlicherweise in den Raffstore-Modus.

**Betroffene Stellen im Code:**
- Manuell-Vorrang-Erkennung: nur wenn `EN[12]>0`
- Behang-Automatik: Jalousie-Zweig (`EN[12]==0`) vs. Raffstore-Zweig (`EN[12]>0`)
- Lamellennachführung EC[10]: Jalousie-Sonderfall (`EN[12]==0`)
- Abfahrt-Flag-Reset: `EN[12]==0`-Zweig für Jalousie
