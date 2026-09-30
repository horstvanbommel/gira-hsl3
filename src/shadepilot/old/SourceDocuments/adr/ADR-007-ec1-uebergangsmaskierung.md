# ADR-007: EC[1] Übergangsmaskierung für Manuell-Vorrang-Erkennung

**Status:** Accepted
**Datum:** 07/2026
**Autor:** gira-hs Anpassung

---

## Kontext

`SN[2]` (Lamellen-Sollwert) wird **jeden Zyklus** live aus der aktuellen Inklination (`EN[1]`) berechnet (Abschnitt 1, Bedingung nur `EN[2]==1`) — nicht erst, wenn `EC[1]` feuert. Wenn sich der Sonnenstand ändert und `EC[1]` in genau diesem Zyklus wahr wird, springt `SN[2]` sofort auf den neuen Wert. `EN[12]` (Lamelle IST) spiegelt diesen neuen Wert naturgemäß noch nicht wider, da die Lamelle erst danach in Bewegung gesetzt wird (Abschnitt 7, Lamellennachführung bei Inklinationsänderung).

Die Regeln eines Bausteins werden pro Zyklus von oben nach unten ausgewertet. Die Manuell-Vorrang-Erkennung (Abschnitt 3) steht **vor** Abschnitt 7. Ohne Schutz sieht die Manuell-Erkennung im selben Zyklus, in dem `EC[1]` feuert, bereits eine Abweichung zwischen `EN[12]` (alt) und `SN[2]` (neu) über der Toleranz `EN[4]` — und löscht `SN[5]` (Automatik-Flag), **bevor** die eigentliche Korrektur in Abschnitt 7 geprüft wird. Da Abschnitt 7 `SN[5]>0` voraussetzt, wird die Korrektur dadurch im selben Zyklus unterdrückt.

**Symptom:** Die Lamellennachführung funktioniert nur beim ersten Mal (über den durch `SN[6]` geschützten Behang-Ankunfts-Pfad, `EC[10]`, siehe ADR-002/003). Sobald `SN[6]` zurückgesetzt ist und die normale, inklinationsgetriebene Nachführung übernimmt, deaktiviert die nächste nennenswerte Sonnenstandsänderung die Automatik selbst — `SN[5]` bleibt auf 0, bis ein externes Ereignis (Beschattungs-Umschaltung, Zyklus-Neustart) es zurücksetzt.

Dieselbe Race Condition wurde für die Beschattungs-Umschaltung bereits in ADR-005 gelöst (`not EC[2]`). Für den analogen Fall bei Sonnenstandsänderungen (`EC[1]`) fehlte die entsprechende Maskierung.

---

## Entscheidung

Die Bedingung `not EC[1]` wird zur Manuell-Vorrang-Erkennung (Abschnitt 3, `.hsl` Zeile 74) hinzugefügt, analog zu `not EC[2]`:

```
Vorher:  5012|0|"EN[12]>0 and SN[6]==0 and EN[12]<98 and abs(EN[12]-SN[2])>EN[4] and not EC[2]"|"0"|""|0|0|5|0
Nachher: 5012|0|"EN[12]>0 and SN[6]==0 and EN[12]<98 and abs(EN[12]-SN[2])>EN[4] and not EC[2] and not EC[1]"|"0"|""|0|0|5|0
```

`EC[1]` ist per Definition nur in dem einen Zyklus wahr, in dem sich `EN[1]` ändert — danach ist die Maskierung automatisch aufgehoben, genau wie bei `EC[2]`.

Die flankenbasierte Endlagen-Erkennung (ADR-004, Amendment 07/2026, `.hsl` Zeile 77) bleibt unverändert. Sie schützt sich bereits selbst über `abs(EN[12]-SN[2])>EN[4]`: fährt die Automatik selbst legitim in Richtung 100 % (`SN[2]≈100`), ist die Abweichung ≈ 0, ein zusätzlicher `not EC[1]`-Ausschluss ist dort nicht nötig.

---

## Konsequenzen

**Positiv:**
- Kein Falsch-Auslösen der Manuell-Erkennung bei Sonnenstandsänderungen; die inklinationsgetriebene Lamellennachführung (Abschnitt 7) funktioniert dauerhaft, nicht nur beim ersten Mal.
- Keine zusätzlichen Timer oder Flags nötig — `EC[N]` ist eine eingebettete Eigenschaft des HSL-Runtimes, gleiches Muster wie ADR-005.

**Negativ/Risiken:**
- Wenn ein Benutzer in exakt demselben Zyklus, in dem `EN[1]` sich ändert, manuell eingreift, wird dieser Eingriff nicht erkannt. Vernachlässigbares Zeitfenster (ein Zyklus ≈ Millisekunden), analog zur bereits akzeptierten Risikobewertung in ADR-005.
- Deckt nur die Race Condition im Auslöse-Zyklus ab. Sollte die physische Lamellen-Rückmeldung (`EN[12]`) während der Fahrt mehrfach zwischenzeitlich Werte melden, die noch über der Toleranz zu `SN[2]` liegen, bevor die Zielposition erreicht ist, würde die Manuell-Erkennung in diesen späteren Zyklen wieder greifen (dort ist `not EC[1]` nicht mehr wahr). Bisheriges Hardwareverhalten (siehe ADR-002/003/004) deutet darauf hin, dass die Lamellen-Positionsrückmeldung in der Praxis nicht so feingranular zwischenmeldet, sondern erst nahe der Zielposition wieder feuert — sollte sich das als falsch erweisen, ist eine Erweiterung des `SN[6]`-Schutzes auf Abschnitt 7 (statt der reinen Zyklusmaskierung) die nächste Eskalationsstufe.

**Betroffene Stellen im Code:**
- Manuell-Vorrang-Erkennung (Abschnitt 3, `.hsl` Zeile 74): `and not EC[1]` ergänzt.

**Verwandte Entscheidungen:** ADR-002 (SN[6] Abfahrt-Flag), ADR-003 (SN[6] Reset-Zeitpunkt), ADR-004 (Endlagen-Ausschluss), ADR-005 (EC[2] Übergangsmaskierung, das direkte Vorbild für diese Entscheidung).
