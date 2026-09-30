# ADR-004: Endlagen-Ausschluss (EN[12] < 98) in der Manuell-Vorrang-Erkennung

**Status:** Accepted (06/2026-Amendment zurückgenommen 07/2026 — siehe unten)
**Datum:** 03/2026
**Autor:** gira-hs Anpassung

---

## Kontext

Nach einer automatischen Abfahrt bleibt die Lamelle typischerweise kurz in der 100%-Position (Endlage, vollständig eingezogen/geschlossen). In dieser Stellung weicht `EN[12]` (Lamelle IST) deutlich von `SN[2]` (berechneter Sonnenstand-Sollwert) ab. Ohne Schutzmaßnahme würde die Manuell-Vorrang-Erkennung die 100%-Endlage als manuellen Eingriff interpretieren und `SN[5]` löschen.

---

## Entscheidung

Die Manuell-Vorrang-Erkennung wird nur ausgelöst, wenn `EN[12] < 98`. Werte ≥ 98 % gelten als Endlage und werden ignoriert.

Schwelle 98 % (statt 100 %) gibt einen kleinen Puffer für Messungenauigkeiten des Lamellenpositions-Sensors.

---

## Konsequenzen

**Positiv:**
- Die 100%-Endlage nach einer Abfahrt löst keine fehlerhafte Manuell-Erkennung aus.
- Robustheit gegenüber Sensor-Jitter nahe der Endlage.

**Negativ/Risiken:**
- Eine echte manuelle Verstellung auf einen Wert ≥ 98 % (vollständige Schließung durch den Benutzer) wird nicht als manueller Eingriff erkannt. Das ist ein akzeptierter Trade-off, da vollständige Schließung typischerweise einer manuellen Abfahrt folgt, die ohnehin über `SN[6]` geschützt ist.

**Betroffene Stellen im Code:**
- Manuell-Vorrang-Erkennung (Abschnitt 3, `.hsl` Zeile 70): `EN[12]<98`
- Manuell-Vorrang-Rücknahme (Abschnitt 9, `.hsl` Zeile 150/153): `EN[12]<98`
- Abfahrt-Flag-Reset (Abschnitt 6, `.hsl` Zeile 119): `EN[12]<98`

---

## Amendment 06/2026 — Entfernung von `EN[12]<98` aus der Manuell-Erkennung

> ⚠️ **ZURÜCKGENOMMEN (07/2026).** Dieses Amendment wurde umgesetzt (Commit `05eebcb`), auf der
> Hardware getestet und hat das Nachlaufen der Lamellen defekt gemacht. Der Abschnitt bleibt als
> historischer Nachweis erhalten; die gültige Entscheidung steht im Amendment 07/2026 weiter unten.

**Anlass:** Praxisbeobachtung: Manuelle Verstellung der Lamelle auf 100 % wird nicht als manueller Eingriff erkannt, weil `EN[12]<98` false ist. `SN[5]` bleibt fälschlicherweise auf 1.

**Analyse:** Die ursprüngliche Annahme war, dass `EN[12]<98` notwendig ist, um die automatische 100%-Endlage von einer manuellen Verstellung zu unterscheiden. Diese Annahme ist falsch:

- Während einer automatischen Abfahrt gilt `SN[6]==1` — die Manuell-Erkennung ist durch `SN[6]==0` bereits vollständig deaktiviert.
- Die 100%-Endlage nach einer Automatikfahrt wird daher niemals als manueller Eingriff erkannt, unabhängig von `EN[12]<98`.
- `EN[12]<98` ist in der Manuell-Erkennung also **redundant** für seinen ursprünglichen Zweck und blockiert gleichzeitig die Erkennung eines legitimen manuellen Eingriffs auf 100 %.

**Entscheidung:** `EN[12]<98` wird aus der **Manuell-Vorrang-Erkennung** (Zeile 70) und der **Manuell-Vorrang-Rücknahme** (Zeilen 150/153) entfernt. Der Schutz vor Fehl-Erkennung während automatischer Abfahrten wird ausschließlich durch `SN[6]==0` gewährleistet.

**Ausnahme:** In der Regel zum **Abfahrt-Flag-Reset** (Abschnitt 6, Zeile 119) bleibt `EN[12]<98` erhalten. Dort hat die Bedingung eine andere Semantik: Sie erkennt, wann die Lamelle die 100%-Endlage *verlässt*, und ist für diese Funktion weiterhin korrekt.

**Betroffene Stellen nach Amendment:**
- Manuell-Vorrang-Erkennung (Zeile 70): `EN[12]<98` **entfernt**
- Manuell-Vorrang-Rücknahme (Zeilen 150/153): `EN[12]<98` **entfernt**
- Abfahrt-Flag-Reset (Zeile 119): `EN[12]<98` **bleibt** (andere Semantik)

---

## Amendment 07/2026 — 06/2026-Amendment zurückgenommen; Endlagen-Erkennung über steigende Flanke

**Anlass:** Das 06/2026-Amendment (Entfernung von `EN[12]<98` aus Zeile 70/150/153) wurde umgesetzt (Commit `05eebcb`) und auf der Hardware getestet. Ergebnis: **Das Nachlaufen der Lamellen war danach defekt.** Damit ist die Kernannahme des 06/2026-Amendments widerlegt.

**Korrigierte Analyse:** `EN[12]<98` in Zeile 70 ist **nicht** redundant. Es erfüllt eine zweite, essenzielle Funktion, die im 06/2026-Amendment übersehen wurde:

- Beim **automatischen Verlassen** der Endlage steht `EN[12]` (Lamelle IST) physikalisch noch bei ~100 %, während der Sollwert `SN[2]` bereits abgesunken ist. `EN[12]<98` maskiert genau diesen Nachlauf-Übergang.
- Ohne `EN[12]<98` wird dieser Übergang als manueller Eingriff fehlinterpretiert → `SN[5]=0` → die Nachführung stirbt.
- `SN[6]==0` deckt diesen Fall **nicht** ab: `SN[6]` ist nur während der Behang-Abfahrt gesetzt, nicht während der normalen inklinationsgetriebenen Lamellenbewegung.

Ein automatisches Endlagen-*Verlassen* und eine manuelle Verstellung *in* die Endlage sehen im selben Zyklus identisch aus (`EN[12]≥98`, Abweichung von `SN[2]`, `SN[6]==0`) — sie unterscheiden sich nur in der **Bewegungsrichtung**.

**Entscheidung:**

1. Das 06/2026-Amendment wird **zurückgenommen**. `EN[12]<98` bleibt in Zeile 70, 150 und 153 erhalten (Ausgangszustand ADR-004). Damit läuft das Nachlaufen wie zuvor.
2. Das ursprünglich adressierte Problem — manuelle bzw. Szenen-Verstellung *in* die Endlage soll die Automatik deaktivieren — wird durch eine **separate, flankenbasierte Regel** gelöst, die die Bewegungsrichtung auswertet (eingefügt direkt nach Zeile 70):

   ```
   5012|0|"EN[12]>=99 and EN[12]>EA[12] and SN[6]==0 and abs(EN[12]-SN[2])>EN[4]"|"0"|""|0|0|5|0
   ```

   - `EN[12]>EA[12]` (steigende Flanke): nur eine Verstellung *nach oben* in die Endlage löst aus; das automatische Verlassen (fallende Flanke) nicht.
   - `abs(EN[12]-SN[2])>EN[4]`: fährt die Automatik selbst legitim nach 100 % (`SN[2]=100`), ist die Abweichung ≈ 0 → kein Fehlauslösen.
   - `SN[6]==0`: während einer Abfahrt inaktiv.
   - Schwelle `>=99` (statt 98) auf der Hardware bestätigt.

**Anwendungsfall:** Automatik aktiv, Lamelle z. B. 90 %; eine Szene (z. B. Beamer) stellt 100 %. Die Regel deaktiviert die Automatik (`SN[5]=0`), sodass der Raffstore bei nachlassender Sonne nicht ungewollt auf den Ruhewert (z. B. 50 %) öffnet.

**Betroffene Stellen nach diesem Amendment:**
- Manuell-Vorrang-Erkennung (Zeile 70): `EN[12]<98` **bleibt** (06/2026-Entfernung rückgängig)
- Manuell-Vorrang-Rücknahme (Zeile 150/153): `EN[12]<98` **bleibt** (06/2026-Entfernung rückgängig)
- Abfahrt-Flag-Reset (Zeile 119): `EN[12]<98` **bleibt** (unverändert)
- **Neu:** flankenbasierte Endlagen-Erkennung direkt nach Zeile 70
