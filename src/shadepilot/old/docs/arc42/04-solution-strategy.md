# §04 Lösungsstrategie

(Source: CLAUDE.md § HSL-Dateiformat, § Logik-Architektur, § Designentscheidungen;
ADR-001 bis ADR-006)

---

## Grundprinzip: Regelbasierte deklarative Ausführung

Der Baustein verwendet das HSL-5012-Regelmodell: Jede Logikregel beschreibt eine Bedingung
und einen Wert. Der Gira-Homeserver wertet alle Regeln **sequenziell von oben nach unten**
aus und führt jede Regel aus, deren Bedingung in diesem Zyklus wahr ist.

```
5012|0|"Bedingung"|"Wert"|"Timeout"|out_idx|0|sn_idx|0
         ▲           ▲        ▲          ▲          ▲
         │           │        │          │          └─ Speicherziel (SN[N])
         │           │        │          └──────────── Ausgangsziel (Ausgang N)
         │           │        └─────────────────────── Optionaler Timeout (Sek.)
         │           └──────────────────────────────── Neuer Wert (Ausdruck)
         └──────────────────────────────────────────── Feuerbedingung (Ausdruck)
```

(Source: CLAUDE.md § HSL-Dateiformat)

---

## Polling + Flanken-Trigger

Das Gira-Homeserver-Laufzeitsystem ist ein **Polling-System**: Es wertet alle Regeln jedes
Mal aus, wenn sich ein Eingang ändert oder ein Timer abläuft. Dennoch erlaubt das
EC/EA-Mechanismus ereignisartige Steuerung innerhalb dieses Polling-Modells:

- **EC[N]** ist wahr genau in dem Zyklus, in dem sich `EN[N]` ändert → einmalige Ausführung
- **EA[N]** hält den Vorwert → Flankenrichtung erkennbar (z. B. `EN[3]==1 and EA[3]==0` = steigende Flanke)

Dadurch verhalten sich kritische Aktionen wie Ereignis-Handler, ohne dass ein gesondertes
Ereignis-Framework nötig ist.

(Source: CLAUDE.md § Variablenreferenz)

---

## Zustandsmaschine via SN-Register

Dauerhafter Zustand innerhalb eines Betriebszyklus wird in 7 Speicherregistern (`SN[1]`–`SN[7]`)
gehalten. Diese Register bilden eine implizite Zustandsmaschine:

| Register | Rolle in der Zustandsmaschine |
|----------|------------------------------|
| `SN[2]` | Aktueller Zielwert (Eingabe für alle Steuerregeln) |
| `SN[3]` | Positionsflag (Behang in Ziel?) |
| `SN[5]` | Automatik/Manuell-Modus |
| `SN[6]` | Abfahrt aktiv (schützt Manuell-Erkennung, ADR-002) |

> ⚠️ Inferred: SN-Werte sind flüchtig. Ein Homeserver-Neustart setzt alle Speicher
> auf ihre Standardwerte zurück (`SN[5]=1`, alle anderen 0).

---

## Zwei Gerätepfade (ADR-001)

Statt eines separaten Bausteins pro Gerätetyp unterscheidet der Baustein intern:

```
EN[12] == 0  →  Jalousie-Pfad (konservativ, ohne Lamellen-Feedback)
EN[12] >  0  →  Raffstore-Pfad (mit Lamellen-Feedback, bidirektional)
```

Dieser Ansatz vermeidet einen zusätzlichen Konfigurations-Eingang, setzt aber voraus,
dass Jalousie-Installationen niemals einen Wert auf `EN[12]` senden.

---

## Drei Schutzschichten für Manuell-Erkennung

Die Manuell-Vorrang-Erkennung ist die fehleranfälligste Komponente; drei unabhängige
Guards verhindern Falsch-Auslösungen:

1. **SN[6] Abfahrt-Flag** (ADR-002) — Erkennung während eigener Motorfahrten deaktiviert
2. **EN[12]<98 Endlagenausschluss** (ADR-004) — 100%-Endlage nicht als Eingriff interpretiert
3. **not EC[2] Übergangsmaskierung** (ADR-005) — Erkennung im Beschattungs-Umschaltzyklus unterdrückt

Diese Guards sind komplementär; jede schützt ein anderes Falsch-Auslöse-Szenario.

---

## Formeln

**Lamellen-Sollwert** (Source: CLAUDE.md § Designentscheidungen; anforderungen.md F-01):

```
SN[2] = round(((90 - EN[1]) * (EN[6] - EN[5]) / 90) + EN[5] + EN[8])
```

Begrenzt auf `[EN[5], EN[6]]` durch nachgelagerte Clamp-Regeln.

**Behang-Zielposition** (Source: anforderungen.md F-04):

```
Ausgang 2 = min(EN[9], 100)
```

**Positions-Toleranzcheck:**

```
SN[3] = int(abs(EN[9] - EN[10]) <= 3)   -- Behang in Zielposition (±3%)
```

---

*Siehe auch:* [§05 Bausteinsicht](05-building-block-view.md) für die 11 Logikabschnitte |
[§09 Architekturentscheidungen](09-architecture-decisions.md) für alle ADRs
