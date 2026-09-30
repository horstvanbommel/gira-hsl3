# ADR-005: EC[2] Übergangsmaskierung für Manuell-Vorrang-Erkennung

**Status:** Accepted
**Datum:** vor 03/2026 (Originaldesign)
**Autor:** Matthias Schmidt (original), dokumentiert in gira-hs

---

## Kontext

Wenn die Beschattung (EN[2]) umschaltet (Ein → Aus oder Aus → Ein), sendet der Baustein sofort einen neuen Lamellen-Sollwert. In genau diesem Zyklus ändert sich `SN[2]` sprunghaft — von einem beschattungsbedingten Wert auf einen ruhezustandsbedingten Wert oder umgekehrt. `EN[12]` (Lamelle IST) spiegelt die neue Position noch nicht wider, da die Lamelle erst in Bewegung gesetzt wird.

Ohne Schutz würde die Manuell-Vorrang-Erkennung im Umschaltzyklus einen Abstand zwischen `EN[12]` und dem neuen `SN[2]` messen und `SN[5]` fälschlicherweise löschen.

---

## Entscheidung

Die Bedingung `not EC[2]` wird in alle Manuell-Vorrang-Erkennungsregeln eingefügt. Die Erkennung wird genau in dem Zyklus unterdrückt, in dem sich EN[2] ändert.

`EC[2]` ist nur für einen einzigen Auswertungszyklus wahr — danach ist die Maskierung automatisch aufgehoben.

---

## Konsequenzen

**Positiv:**
- Kein Falsch-Auslösen der Manuell-Erkennung beim Umschalten der Beschattung.
- Keine zusätzlichen Timer oder Flags nötig — EC[N] ist eine eingebettete Eigenschaft des HSL-Runtimes.

**Negativ/Risiken:**
- Wenn ein Benutzer in exakt demselben Zyklus, in dem EN[2] umschaltet, manuell eingreift, wird dieser Eingriff nicht erkannt. Das ist ein vernachlässigbares Zeitfenster (ein Zyklus ≈ Millisekunden).

**Betroffene Stellen im Code:**
- Manuell-Vorrang-Erkennung (Abschnitt 3, `.hsl` Zeile 70): `and not EC[2]`
- Manuell-Vorrang-Rücknahme (Abschnitt 9, `.hsl` Zeilen 150, 153, 156, 157): `and not EC[2]`
