# ADR-002: SN[6] Abfahrt-Flag schützt die Manuell-Vorrang-Erkennung

**Status:** Accepted
**Datum:** 03/2026 (überarbeitet; Originalkonzept älter)
**Autor:** gira-hs Anpassung

---

## Kontext

Die Manuell-Vorrang-Erkennung beobachtet, ob die Lamellen-IST-Position (`EN[12]`) vom berechneten Sollwert (`SN[2]`) abweicht. Wenn der Baustein selbst eine Abfahrt ausgelöst hat, bewegen sich Behang und Lamelle motorisch — die IST-Position ändert sich dabei zwangsläufig. Ohne Schutzmaßnahme würde die Manuell-Erkennung jede automatische Bewegung als manuellen Eingriff interpretieren und `SN[5]` (Automatik-Flag) löschen.

---

## Entscheidung

Einführung von `SN[6]` als **Abfahrt-Flag**:

- `SN[6] = 1`: Eine automatisch ausgelöste Abfahrt ist aktiv; Manuell-Erkennung ist deaktiviert.
- `SN[6] = 0`: Kein automatischer Lauf aktiv; Manuell-Erkennung ist aktiviert.

`SN[6]` wird gesetzt, wenn der Baustein eine Abfahrt startet (EC[3]-Trigger, Behang-Automatik-Abschnitt). Es wird erst zurückgesetzt, wenn die Bewegung abgeschlossen ist (siehe ADR-003), nicht sofort.

Als Sicherheitsfallback wird `SN[6]` nach 180 Sekunden automatisch gelöscht, falls der normale Reset-Pfad nicht feuert.

---

## Konsequenzen

**Positiv:**
- Automatische Bewegungen werden nicht fälschlicherweise als manuelle Eingriffe erkannt.
- Die Manuell-Erkennung ist während der gesamten Fahrtdauer zuverlässig deaktiviert.

**Negativ/Risiken:**
- Manuelle Eingriffe während einer laufenden Abfahrt werden nicht erkannt. Das ist gewollt, kann aber dazu führen, dass ein Eingriff direkt beim Losfahren unbemerkt bleibt.
- Wenn der Reset-Pfad nicht feuert (z. B. durch einen Fehler im Bus-Feedback), verhindert der Timeout nach 180 s ein dauerhaftes Einfrieren. Diese 180 s müssen länger sein als die längste mögliche Abfahrtsdauer.

**Supersedes:** Kein vorheriges ADR; das Konzept wurde in 03/2026 formalisiert und der Reset-Zeitpunkt in derselben Version korrigiert (→ ADR-003).
