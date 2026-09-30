# Anforderungen: Jalousie Lamellennachführung

**Stand:** 2026-04-29
**Status:** Draft — aus CLAUDE.md und Implementierung abgeleitet; noch nicht formal abgenommen

---

## Stakeholder

| Rolle | Interesse |
|-------|-----------|
| Bewohner / Nutzer | Komfortabler Sonnenschutz ohne manuellen Eingriff; eigene Verstellung soll respektiert werden |
| Integrator / Installateur | Einfache Konfiguration im GPA; klare Parameterbeschreibungen; keine unerwarteten Bewegungen |
| Gira Homeserver | Korrekte Einbindung als HSL-Baustein; kompatibel mit GPA und dem Automatisierungsbus |

---

## Funktionale Anforderungen

### F-01: Automatische Sonnenstandsnachführung
Der Baustein berechnet den optimalen Lamellenwinkel aus der aktuellen Sonnen-Inklination und fährt die Lamelle auf diesen Wert, wenn die Beschattung aktiv ist (EN[2]=1) und der Zyklus aktiv ist (EN[3]=1).

**Formel:** `round(((90 - EN[1]) * (EN[6] - EN[5]) / 90) + EN[5] + EN[8])`

### F-02: Manuell-Vorrang-Erkennung
Weicht die tatsächliche Lamellenposition (EN[12]) um mehr als die Toleranz (EN[4]) vom berechneten Sollwert ab, deaktiviert der Baustein die Automatik (SN[5]=0). Dadurch werden keine weiteren automatischen Lamellenbewegungen ausgelöst, bis der Benutzer oder ein Reset die Automatik wiederherstellt.

### F-03: Manuell-Vorrang-Rücknahme
Die Automatik wird automatisch wiederhergestellt (SN[5]=1), sobald die tatsächliche Position wieder innerhalb der Toleranz des Sollwerts liegt.

### F-04: Behang-Automatik
Bei aktivem Zyklus-Trigger (EC[3], steigende Flanke) fährt der Behang auf die konfigurierte Zielposition (EN[9]). Für Jalousien nur, wenn der Behang unterhalb der Zielposition ist (ADR-006). Bei Zyklus-Aus fährt der Behang auf (Ausgang 3).

### F-05: Lamellennachführung bei Behang-Ankunft
Sobald der Behang die Zielposition erreicht (±3%), fährt die Lamelle auf den aktuell berechneten Sollwert (bei Beschattung ein) oder den Ruhewert EN[7] (bei Beschattung aus).

### F-06: Sofortanpassung bei Beschattungswechsel
Wenn die Beschattung umschaltet (EC[2]), wird die Lamelle sofort auf den neuen Sollwert gefahren, ohne auf den Zyklus-Trigger zu warten.

### F-07: Neigungsänderungs-Nachführung
Bei einer Änderung der Sonnen-Inklination (EC[1]) wird die Lamelle nachgeführt, wenn die Änderung die Mindestschwelle EN[4] überschreitet und die Automatik aktiv ist.

### F-08: Statusausgabe
Der Baustein gibt dauerhaft einen Debug-String mit allen internen Zustandswerten (SN[1]–SN[7], EN[12]) auf Ausgang 4 aus.

---

## Nicht-funktionale Anforderungen

### NF-01: Sicherheits-Timeout
Ein laufender Abfahrt-Vorgang darf nicht dauerhaft die Manuell-Erkennung blockieren. Nach spätestens 180 Sekunden wird der Bewegungsstatus automatisch zurückgesetzt.

### NF-02: Kodierung
Die .hsl-Datei muss in ISO-8859-1 (Latin-1) kodiert sein, um Kompatibilität mit dem Gira Homeserver sicherzustellen.

### NF-03: Gerätetyp-Kompatibilität
Der Baustein muss für Jalousien (kein Lamellen-Feedback) und Raffstoren (mit Lamellen-Feedback) korrekt funktionieren, konfiguriert über EN[12].

---

## Ausgeschlossene Anforderungen (Out of Scope)

- Automatische Erkennung von Wettereignissen (Wind, Regen) — separate Bausteine zuständig
- Gruppensteuerung mehrerer Jalousien — jeder Baustein steuert eine Jalousie
- Persistenz des Automatik-Flags über Homeserver-Neustart hinaus

---

## Offene Fragen

| # | Frage | Priorität |
|---|-------|-----------|
| OQ-01 | Welche Gira Homeserver Firmware-Version ist Mindestvoraussetzung? | mittel |
| OQ-02 | Was ist die maximale Fahrtzeit für Behang und Lamelle? (Relevant für 180-s-Timeout-Dimensionierung) | hoch |
| OQ-03 | Soll der Baustein mehrere Instanzen pro Homeserver-Projekt unterstützen? (Aktuell: ja, ohne Einschränkung) | niedrig |
| OQ-04 | Gibt es einen Qualitätsziel für die Falsch-Erkennungsrate des Manuell-Vorrangs? | mittel |
