# ADR-006: Jalousie — Initiale Abfahrt nur wenn EN[10] < EN[9]

**Status:** Accepted
**Datum:** 04/2026
**Autor:** gira-hs Anpassung

---

## Kontext

Für **Raffstoren** ist die Abfahrt-Bedingung: `SN[3]==0` (Behang nicht in Zielposition). Das ist symmetrisch — der Baustein fährt ab, wenn der Behang zu hoch oder zu niedrig ist.

Für **Jalousien** (`EN[12]==0`) wurde dieselbe Bedingung verwendet. Dabei trat folgendes Problem auf: Wenn der Behang bereits **tiefer** als die Zielposition (`EN[10] > EN[9]`) ist — z. B. weil der Benutzer ihn manuell ganz heruntergefahren hat — löste der Zyklus-Trigger trotzdem eine Abfahrt aus, die den Behang weiter nach unten fuhr. Das führte zu unnötigen oder unerwünschten Bewegungen.

Der Unterschied zum Raffstore: Bei der Jalousie gibt es kein Lamellen-Feedback, das die Manuell-Vorrang-Erkennung korrekt informieren kann. Daher muss der Baustein konservativer agieren.

---

## Entscheidung

Für Jalousien (`EN[12]==0`) wird die Abfahrt-Bedingung um `EN[10] < EN[9]` ergänzt:

```
EC[3] and EN[3]==1 and EA[3]==0 and SN[3]==0 and EN[12]==0 and EN[10]<EN[9]
```

Eine initiale Abfahrt findet nur statt, wenn der Behang **unterhalb** der Zielposition ist (noch nicht weit genug heruntergefahren). Ist der Behang bereits über der Zielposition oder tiefer, wird keine Abfahrt ausgelöst.

Für Raffstoren bleibt die Bedingung unverändert (`SN[3]==0` ohne Richtungsprüfung).

---

## Konsequenzen

**Positiv:**
- Keine unerwünschten Abfahrten bei Jalousien, wenn der Behang bereits in oder unterhalb der Zielposition ist.
- Konservativeres Verhalten ohne Lamellen-Feedback.

**Negativ/Risiken:**
- Wenn der Behang über der Zielposition ist (zu hoch, z. B. 50 % statt 90 %), fährt der Baustein für Jalousien **nicht** automatisch nach. Das ist ein akzeptierter Trade-off: ohne Lamellenrückmeldung ist eine Aufwärtskorrektur risikoreicher.
- Das asymmetrische Verhalten (Jalousie nur Abfahrt nach unten, Raffstore bidirektional) ist nicht unmittelbar offensichtlich und erfordert Dokumentation (→ dieses ADR).

**Supersedes:** Früheres Verhalten (vor 04/2026), bei dem `EN[10]<EN[9]` für Jalousien nicht geprüft wurde.
