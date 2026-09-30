# §11 Risiken und technische Schulden

(Source: docs/arc42/00-source-inventory.md § Gaps, § §11 Risks;
CLAUDE.md § Projektübersicht, § Zeichenkodierung;
`19822_Jalousie Lamellennachführung_optimiert.hsl` Header)

> ⚠️ **Alle Einträge dieses Abschnitts sind inferred** — kein formales Risikoregister
> existiert in den Quelldokumenten. Die Risiken wurden aus dem Code, den Constraints und
> der Dokumentation abgeleitet.

---

## Risikoregister

| # | Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|---|--------|-------------------|-----------|-----------
| R-01 | Kein automatisierter Test | Hoch | Mittel | Manuelle Tests nach jeder Änderung; Statustext-Ausgang für Diagnose |
| R-02 | ISO-8859-1-Kodierung fragil | Mittel | Mittel | Kodierungsregel in CLAUDE.md § Zeichenkodierung dokumentiert; Editor-Einstellung prüfen |
| R-03 | SN-Zustand flüchtig | Niedrig | Niedrig | Nach Neustart: SN[5]=1 (Automatik aktiv) ist der sichere Standardzustand |
| R-04 | Unvollständige Versionshistorie | Niedrig | Niedrig | ADR-Dateien und .hsl-Header-Kommentare dokumentieren Änderungen ab 03/2026 |

---

### R-01: Kein automatisierter Test

**Beschreibung:** Es gibt keine Testsuite, keinen Simulator und kein CI/CD-System. Die einzige
Möglichkeit, die Korrektheit des Bausteins zu verifizieren, ist das Deployment auf physische
Hardware und manuelle Beobachtung.

**Konsequenz:** Regressionen durch Änderungen werden möglicherweise erst nach dem Produktiv-Deployment
entdeckt. Die drei Guards der Manuell-Erkennung (ADR-002, ADR-004, ADR-005) interagieren
komplex — Fehler in einem Guard können subtil sein.

**Mitigation:** Statustext-Ausgang 4 zeigt alle SN-Werte; manuelle Testszenarien können
die vier Laufzeitszenarien aus §06 abdecken.

(Source: CLAUDE.md § Projektübersicht)

---

### R-02: ISO-8859-1-Kodierung fragil

**Beschreibung:** Moderne Texteditoren (VS Code, Sublime Text, etc.) speichern Dateien
standardmäßig als UTF-8. Ein versehentliches Speichern der `.hsl`-Datei als UTF-8 korrumpiert
alle Umlaut-Zeichen lautlos — der Fehler ist erst nach dem GPA-Upload sichtbar.

**Konsequenz:** Korrumpierte Kommentare oder Baustein-Namen im GPA; potenzielle String-Fehler
in Ausgabe 4 (Statustext).

**Mitigation:** Dokumentiert in CLAUDE.md § Zeichenkodierung; Editor-Konfiguration (`.editorconfig`
oder Editor-Einstellung) empfohlen. Prüfung mit `file -I` nach dem Bearbeiten möglich.

(Source: CLAUDE.md § Zeichenkodierung; anforderungen.md NF-02)

---

### R-03: SN-Zustand flüchtig (Homeserver-Neustart)

**Beschreibung:** SN-Register sind im Homeserver-RAM; bei einem Neustart werden sie auf ihre
Standardwerte zurückgesetzt. `SN[5]` startet mit 1 (Automatik aktiv), auch wenn der Benutzer
vor dem Neustart manuell eingegriffen hatte.

**Konsequenz:** Nach einem Homeserver-Neustart ist der Manuell-Vorrang-Zustand verloren;
die Automatik läuft wieder, auch wenn der Benutzer das nicht erwartet.

**Wahrscheinlichkeit:** Niedrig (Homeserver-Neustarts sind selten).
**Auswirkung:** Niedrig (der sichere Standardzustand, Automatik aktiv, ist für die meisten
Szenarien korrekt; der Benutzer kann jederzeit wieder manuell eingreifen).

---

### R-04: Unvollständige Versionshistorie vor 03/2026

**Beschreibung:** Der Baustein basiert auf einem Original von Matthias Schmidt (2006). Änderungen
zwischen 2006 und 03/2026 sind nicht dokumentiert. Es ist unbekannt, wie viele
Zwischenstände existierten und welche Bugs oder Design-Entscheidungen darin enthalten waren.

**Konsequenz:** Bei zukünftigen Änderungen kann nicht auf eine vollständige Commit-History
zurückgegriffen werden. Designentscheidungen aus der Frühphase sind möglicherweise nicht nachvollziehbar.

**Mitigation:** ADR-Dateien dokumentieren alle bekannten Entscheidungen ab 03/2026 formal.
Das Original-Copyright bleibt im `.hsl`-Header erhalten.

(Source: .hsl Zeilen 3–11)

---

## Technische Schulden

| # | Schuld | Aufwand zur Behebung | Priorität |
|---|--------|---------------------|----------|
| TD-01 | `SN[4]` wird berechnet, aber in keiner Logikregel als Bedingung genutzt (nur Statustext) | Niedrig | Niedrig |
| TD-02 | `.claude/rules/` enthält Go-spezifische Templates (go-conventions.md, streb-architecture.md) ohne Relevanz für dieses HSL-Projekt | Trivial (Löschen/Ersetzen) | Niedrig |
| TD-03 | Anforderungsdokument (anforderungen.md) ist Draft und nicht formal abgenommen; OQ-01–OQ-04 offen | Mittel (Stakeholder-Interview) | Mittel |

### TD-01: SN[4] ohne Nutzung als Bedingung

`SN[4]` wird in §2 (Positions-Flags) korrekt berechnet als "Lamelle weicht vom Sollwert ab",
erscheint aber in keiner 5012-Regel als Bedingung. Es wird ausschließlich im Statustext
(Ausgang 4) ausgegeben.

**Mögliche Lösung:** Entweder in CLAUDE.md § Variablenreferenz dokumentieren, dass SN[4]
diagnostisch-only ist, oder eine Logikregel implementieren, die SN[4] als Guard nutzt.

(Source: docs/arc42/00-source-inventory.md § Contradictions; .hsl Zeilen 58–60)

---

*Siehe auch:* [§02 Randbedingungen](02-constraints.md) für zugrundeliegende Constraints |
[§10 Qualitätsanforderungen](10-quality-requirements.md) für offene Qualitätsfragen
