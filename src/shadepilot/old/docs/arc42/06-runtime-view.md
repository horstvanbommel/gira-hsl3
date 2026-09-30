# §06 Laufzeitsicht

(Source: CLAUDE.md § Logik-Architektur;
`19822_Jalousie Lamellennachführung_optimiert.hsl` Zeilen 80–170;
ADR-002, ADR-003, ADR-005, ADR-006)

Vier Schlüsselszenarien zeigen das Laufzeitverhalten des Bausteins.

---

## Szenario 1 — Normalbetrieb Raffstore: Zyklus-Trigger → Abfahrt → Lamellen-Nachführung

Ausgelöst durch steigende Flanke von EN[3] (Zyklus-Ein), wenn Behang nicht in Zielposition.

```mermaid
sequenceDiagram
    participant HS as Homeserver-Bus
    participant B as Baustein (HSL)
    participant M as Motorsteuerung

    HS->>B: EN[3]=1 (Zyklus-Ein, EC[3] wahr)
    note over B: §4 Behang-Automatik prüft:<br/>SN[3]==0 (Behang nicht in Ziel)<br/>EN[12]>0 (Raffstore)
    B->>B: SN[6]=1 (Abfahrt-Flag setzen)
    B->>B: SN[7]=SN[2] (Lamellen-Zielwert speichern)
    B->>M: Ausgang 2 = min(EN[9], 100) %

    M-->>HS: EN[10] ändert sich (Behang fährt)
    note over B: §3 Manuell-Erkennung: SN[6]==1<br/>→ deaktiviert (ADR-002)

    M-->>HS: EN[10] ≈ EN[9] (±3 %)
    HS->>B: EC[10] wahr
    note over B: §5 Lamellen-Nachführung:<br/>abs(EN[9]-EN[10])<=3<br/>kein SN[6]-Check (ADR-003)
    B->>M: Ausgang 1 = round(SN[2]) %
    B->>B: SN[5]=1 (Automatik aktiv)

    M-->>HS: EN[12] bewegt sich (Lamelle fährt)
    HS->>B: EC[12] wahr, EN[12]<98
    note over B: §6 Abfahrt-Flag Reset:<br/>SN[6]==1 → SN[6]=0 (ADR-003)
    note over B: §3 Manuell-Erkennung<br/>wieder aktiv
```

---

## Szenario 2 — Manuell-Vorrang: Erkennung und automatische Rücknahme

Ausgelöst wenn der Benutzer die Lamelle manuell verstellt (Raffstore mit Feedback).

```mermaid
sequenceDiagram
    participant HS as Homeserver-Bus
    participant B as Baustein (HSL)
    participant User as Benutzer

    User->>HS: Manuelle Lamellen-Verstellung
    HS->>B: EN[12] ändert sich (abweichend von SN[2])

    note over B: §3 Manuell-Erkennung prüft:<br/>EN[12]>0 ✓<br/>SN[6]==0 ✓ (kein Abfahrt)<br/>EN[12]<98 ✓ (kein Endlage)<br/>abs(EN[12]-SN[2])>EN[4] ✓<br/>not EC[2] ✓
    B->>B: SN[5]=0 (Manuell-Vorrang aktiv)

    note over B: §7 EC[1] (Inklination): kein Feuern<br/>weil SN[5]==0<br/>§4 EC[3]: kein Feuern wegen SN[3]

    HS->>B: EN[1] ändert sich (neue Inklination)
    B->>B: SN[2] = neue Inklinationsformel
    note over B: §7 prüft SN[5]>0 → falsch<br/>→ keine Lamellen-Verstellung

    note over HS: Benutzer stellt Lamelle auf Sollwert zurück
    User->>HS: Lamelle ≈ SN[2] (innerhalb EN[4])
    HS->>B: EN[12] ≈ SN[2]

    note over B: §9 Manuell-Vorrang-Rücknahme:<br/>abs(EN[12]-SN[2])<=EN[4]
    B->>B: SN[5]=1 (Automatik wieder aktiv)
```

---

## Szenario 3 — Beschattungs-Umschalten (Übergangsmaskierung)

Ausgelöst wenn Beschattung von Aus auf Ein (oder umgekehrt) wechselt (EC[2]).

```mermaid
sequenceDiagram
    participant HS as Homeserver-Bus
    participant B as Baustein (HSL)
    participant M as Motorsteuerung

    HS->>B: EN[2]: 0→1 (Beschattung Ein, EC[2] wahr)

    note over B: §1 Sollwertberechnung:<br/>SN[2] = Inklinationsformel (neuer Wert)
    note over B: §3 Manuell-Erkennung:<br/>not EC[2] = falsch → deaktiviert (ADR-005)

    note over B: §8 Lamellen-Nachführung EC[2]:<br/>EC[2] wahr, EN[2]==1, SN[5]>0
    B->>M: Ausgang 1 = SN[2] (neuer Lamellen-Sollwert)

    note over B: Nächster Zyklus:<br/>EC[2] = falsch<br/>§3 Manuell-Erkennung wieder aktiv
```

---

## Szenario 4 — Inklinationsänderung während Automatikbetrieb (Raffstore)

Ausgelöst wenn Sonnepur eine neue Inklination sendet (EC[1]), ca. alle 2 Minuten.

```mermaid
sequenceDiagram
    participant HS as Homeserver-Bus
    participant B as Baustein (HSL)
    participant M as Motorsteuerung

    HS->>B: EN[1] ändert sich (neue Inklination, EC[1] wahr)

    note over B: §1 Sollwertberechnung:<br/>SN[2] = round(((90-EN[1])*(EN[6]-EN[5])/90)+EN[5]+EN[8])

    note over B: §7 Lamellen-Nachführung EC[1] prüft:<br/>SN[6]==0 ✓ (kein Abfahrt)<br/>SN[3]==1 ✓ (Behang in Ziel)<br/>EN[2]==1 ✓ (Beschattung aktiv)<br/>EN[12]>0 ✓ (Raffstore)<br/>abs(SN[2]-SN[1])>=EN[4] ✓ (Mindeständerung)<br/>SN[5]>0 ✓ (Automatik aktiv)

    B->>M: Ausgang 1 = round(SN[2]) %
    B->>B: SN[1] = SN[2] (gesendeter Wert merken)
```

> ⚠️ Inferred: Für **Jalousien** (EN[12]==0) entfällt die `abs(SN[2]-SN[1])>=EN[4]`-Prüfung
> in §7 — die Lamelle wird bei jeder Inklinationsänderung direkt nachgeführt.
> (Source: .hsl Zeilen 129–130 vs. 131)

---

## Timeout-Fallback (Sicherheitsszenario)

Falls der normale SN[6]-Reset-Pfad nicht feuert (z. B. kein Motorpositions-Feedback):

- §10 feuert nach 180 Sekunden mit `SN[6]==1` (Timeout-Bedingung in .hsl Zeile 163)
- `SN[6]` wird auf 0 gesetzt
- Manuell-Erkennung wird wieder aktiviert

(Source: ADR-002; .hsl Zeile 163)

---

*Siehe auch:* [§05 Bausteinsicht](05-building-block-view.md) für die Abschnitts-Steckbriefe |
[§09 Architekturentscheidungen](09-architecture-decisions.md) für ADR-Begründungen
