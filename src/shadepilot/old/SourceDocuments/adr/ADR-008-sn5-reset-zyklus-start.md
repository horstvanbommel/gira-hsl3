# ADR-008: SN[5]-Reset bei Zyklus-Start von SN[3] entkoppelt

**Status:** Accepted
**Datum:** 08/2026
**Autor:** gira-hs Anpassung

---

## Kontext

Ein Raffstore wurde beim Beenden des Beschattungszyklus nicht nach oben gefahren (vermuteter Grund: Ausgang 3 im GPA-Projekt nicht auf die Behang-Position verknüpft, außerhalb dieser Datei). Der Behang blieb dadurch über Nacht in einer Position stehen (z. B. Lamelle bei 50 %, Behang bei 100 %), die er während des Tagesbetriebs regulär eingenommen hatte.

`SN[3]` (Flag: Behang in Zielposition) wird **jeden Zyklus unconditional** aus `abs(EN[9]-EN[10])<=3` berechnet (Abschnitt 2, `.hsl` Zeile 59) — unabhängig davon, ob gerade eine Automatikfahrt läuft oder der Zyklus überhaupt aktiv ist. Bleibt der Behang zufällig in einer Position stehen, die diese Toleranzbedingung erfüllt, wird `SN[3]` am nächsten Tag bereits `1` sein, **bevor** die Zyklus-Start-Regeln (Abschnitt 4) überhaupt auswerten.

Die bisherigen Zyklus-Start-Regeln, die `SN[5]` (Automatik-Flag) auf 1 zurücksetzen (`.hsl` Zeilen 89/95, jetzt 93/99), waren an `SN[3]==0` gekoppelt:

```
5012|0|"EC[3] and EN[3]==1 and EA[3]==0 and SN[3]==0 and EN[12]>0"|"1"|""|0|0|5|0
```

Ist `SN[3]` bereits `1`, feuert diese Regel nicht — und damit auch nicht der `SN[5]=1`-Reset. War `SN[5]` aus irgendeinem Grund (z. B. Manuell-Vorrang-Erkennung während der fehlgeschlagenen nächtlichen Auffahrt) auf 0 gefallen, bleibt es **dauerhaft** auf 0 hängen. Die Lamellennachführung (Abschnitte 7/8, beide mit `SN[5]>0`-Bedingung) findet dann am nächsten Tag nicht mehr statt, obwohl der Zyklus regulär startet.

**Symptom:** `SN[5]==0` nach Zyklus-Start trotz laufender Beschattung; keine Lamellennachführung; Statustext zeigt `A:0` dauerhaft.

---

## Entscheidung

Eine neue, von `SN[3]` unabhängige Regel setzt `SN[5]` bei **jedem** Zyklus-Start unconditional auf 1 zurück, direkt am Anfang des Abschnitts "Automatiksteuerung Behang" (`.hsl`, vor den Jalousie-/Raffstore-spezifischen Regeln):

```
5012|0|"EC[3] and EN[3]==1 and EA[3]==0"|"1"|""|0|0|5|0
```

`EC[3] and EN[3]==1 and EA[3]==0` ist exakt die steigende Flanke von `EN[3]` (Zyklus-Start), dieselbe Flankenbedingung wie bei den bestehenden `SN[3]==0`-gebundenen Regeln, nur ohne die zusätzliche Positions-Voraussetzung. Die bestehenden `SN[3]==0`-Regeln (Abfahrt-Flag `SN[6]`, Ziel-Percentage auf Ausgang 2, Lamellen-Zielwert `SN[7]`) bleiben unverändert — sie steuern weiterhin, ob tatsächlich eine Fahrt ausgelöst wird. Nur der Automatik-Flag-Reset wird von dieser Bedingung entkoppelt: Jeder neue Zyklus beginnt damit garantiert mit aktiver Automatik, unabhängig vom (potenziell durch einen externen Fehler verfälschten) Positions-Zustand vom Vortag.

Die Regel steht in der Auswertungsreihenfolge nach Abschnitt 3 (Manuell-Vorrang-Erkennung). Feuert die Manuell-Erkennung im selben Zyklus wie der Zyklus-Start (praktisch nicht zu erwarten, da beide auf unterschiedliche Eingänge reagieren), gewinnt die später ausgewertete Zyklus-Start-Regel — das ist das gewünschte Verhalten.

---

## Konsequenzen

**Positiv:**
- `SN[5]` kann nicht mehr über einen kompletten Beschattungstag hinweg auf 0 hängen bleiben, nur weil `SN[3]` durch eine zufällig passende Behang-Position fälschlich `1` anzeigt.
- Kein zusätzlicher State/Timer nötig — nutzt dieselbe Flankenerkennung (`EC[3]`/`EA[3]`) wie die bestehenden Zyklus-Start-Regeln.
- Deckt sowohl Jalousie- als auch Raffstore-Pfad ab (Bedingung enthält keine `EN[12]`-Abfrage).

**Negativ/Risiken:**
- Behebt nicht die eigentliche Ursache (Ausgang 3 beim Zyklus-Ende nicht mit der Behang-Position verknüpft) — das bleibt eine GPA-Projektaufgabe außerhalb dieser Datei. Ohne diese Verknüpfung fährt der Behang weiterhin nicht zuverlässig hoch; ADR-008 sorgt nur dafür, dass die interne Automatik-Logik sich davon nicht dauerhaft lahmlegen lässt.
- Ein am selben Zyklus-Start-Zeitpunkt bereits laufender, legitimer manueller Eingriff (SN[5] durch Abschnitt 3 im selben Zyklus auf 0 gesetzt) würde durch diese Regel sofort wieder überschrieben. Dieses Zeitfenster ist wie bei ADR-005/007 auf einen einzelnen Zyklus begrenzt und wird als vernachlässigbar eingestuft.

**Betroffene Stellen im Code:**
- Automatiksteuerung Behang (Abschnitt 4, `.hsl`): neue Regel `EC[3] and EN[3]==1 and EA[3]==0` → `SN[5]=1`, eingefügt vor den Jalousie-/Raffstore-spezifischen Zyklus-Start-Regeln.
- Versionsstand auf v3.3.2 angehoben.

**Verwandte Entscheidungen:** ADR-001 (Jalousie/Raffstore-Unterscheidung, betrifft beide Pfade gleichermaßen), ADR-002/003 (SN[6] Abfahrt-Flag, unverändert), ADR-007 (analoge Entkopplungs-Logik für die Manuell-Erkennung bei Sonnenstand-Sprüngen — dieselbe Grundidee: eine zu eng gefasste Bedingung verhindert einen notwendigen Reset).
