# ADR-003: SN[6] Reset erst nach Lamellenbewegung, nicht sofort bei Behang-Ankunft

**Status:** Accepted
**Datum:** 03/2026
**Autor:** gira-hs Anpassung

---

## Kontext

Nachdem der Behang seine Zielposition erreicht hat (`EC[10]`, `abs(EN[9]-EN[10])<=3`), startet der Baustein die Lamellennachführung. Die Lamelle fährt anschließend auf den berechneten Sollwert. In der früheren Version wurde `SN[6]` (Abfahrt-Flag) sofort beim Behang-Ankommen zurückgesetzt — noch bevor die Lamellenbewegung abgeschlossen ist.

Das Problem: Die Manuell-Vorrang-Erkennung wird damit reaktiviert, während die Lamelle noch motorisch fährt. Da `EN[12]` (Lamelle IST) sich währenddessen ändert und von `SN[2]` abweicht, löst die Erkennung fälschlicherweise aus und löscht `SN[5]`.

---

## Entscheidung

`SN[6]` wird **nicht** beim Behang-Ankommen (EC[10]) zurückgesetzt, sondern erst wenn:

1. **Raffstore (`EN[12]>0`):** `EC[12]` feuert (Lamelle-IST ändert sich) UND `EN[12]<98` (Lamelle verlässt 100%-Endlage) UND `SN[6]==1`.
2. **Jalousie (`EN[12]==0`):** `EC[10]` feuert (Behang ankommt) UND `abs(EN[9]-EN[10])<=3` UND `SN[6]==1` — da keine Lamellen-Rückmeldung vorhanden ist, ist der Behang-Ankunftsmoment der frühestmögliche Reset-Zeitpunkt.

Die EC[10]-Lamellennachführungsregeln feuern **ohne** `SN[6]`-Prüfung, damit die Lamelle auch bei gesetztem Flag nachgeführt wird.

---

## Konsequenzen

**Positiv:**
- Die Manuell-Erkennung bleibt während der gesamten Lamellenbewegung deaktiviert; keine Falsch-Auslösungen mehr in der Fahrtphase.

**Negativ/Risiken:**
- Der Reset-Zeitpunkt ist an `EC[12]` (Lamellen-Feedback) gebunden; ein ausbleibender Feedback-Impuls verzögert den Reset bis zum Timeout (180 s).
- Die Jalousie-Variante resetzt immer beim Behang-Ankommen, was korrekt ist, aber keine Lamellenbewegungszeit abwartet.

**Supersedes:** Früheres Verhalten (vor 03/2026), bei dem `SN[6]` in den EC[10]-Regeln zurückgesetzt wurde.
