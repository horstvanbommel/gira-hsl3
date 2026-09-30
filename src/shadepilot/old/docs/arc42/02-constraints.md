# §02 Randbedingungen

(Source: CLAUDE.md § Projektübersicht, § Zeichenkodierung, § HSL-Dateiformat;
`19822_Jalousie Lamellennachführung_optimiert.hsl` Header-Kommentare;
SourceDocuments/SpecsAndRequirments/anforderungen.md NF-01–NF-03)

---

## Technische Randbedingungen

| Randbedingung | Beschreibung | Quelle |
|--------------|-------------|--------|
| **ISO-8859-1-Kodierung** | Die `.hsl`-Datei muss in Latin-1 kodiert sein. Speichern als UTF-8 korrumpiert Umlaute (ä, ö, ü, ß) lautlos. (NF-02) | CLAUDE.md § Zeichenkodierung |
| **Proprietäres HSL-Format** | Das Dateiformat ist Gira-proprietär; es existiert keine öffentliche Spezifikation. Änderungen müssen aus Reverse Engineering der vorhandenen Datei und Erfahrungswissen abgeleitet werden. | CLAUDE.md § Projektübersicht |
| **Keine automatisierten Tests** | Es gibt keine Testsuite und kein CI/CD-System. Korrektheit kann ausschließlich durch Deployment auf physische Hardware und manuelle Beobachtung verifiziert werden. | CLAUDE.md § Projektübersicht |
| **GPA als einziges Deployment-Werkzeug** | Der Gira Project Assistant ist das einzige Werkzeug zum Laden der `.hsl`-Datei auf den Homeserver. Kein alternatives Deployment-Pfad existiert. | CLAUDE.md § Projektübersicht |
| **Kein Build-Prozess** | Es gibt keinen Compiler, keinen Paketmanager und keinen Transformationsschritt. Die `.hsl`-Datei wird direkt deployiert. | CLAUDE.md § Projektübersicht |

---

## Organisatorische Randbedingungen

| Randbedingung | Beschreibung | Quelle |
|--------------|-------------|--------|
| **Kein git-Remote** | Das Repository hat keinen konfigurierten Remote. Alle Commits verbleiben lokal; kein kollaborativer PR-Workflow. | git config (lokal) |
| **Einzelentwickler-Workflow** | Das Projekt hat keine formalen Code-Review- oder Abnahme-Prozesse für HSL-Änderungen. | CLAUDE.md (implizit) |
| **Anforderungen Draft-Status** | Das Anforderungsdokument (`anforderungen.md`) ist noch nicht formal abgenommen. Offene Fragen OQ-01 bis OQ-04 sind ungeklärt. | SpecsAndRequirments/anforderungen.md |

---

## Versionsgeschichte und Herkunft

| Fakt | Wert | Quelle |
|------|------|--------|
| Aktuelle Version | V 3.2.5 | `.hsl` Zeile 13 |
| Ursprungsautor | Matthias Schmidt, 2006 | `.hsl` Zeile 4 |
| Anpassungen 03/2026 | SN[6]-Reset-Zeitpunkt korrigiert (ADR-003); EC[10]-Logik überarbeitet; Endlage 100% ausgeschlossen (ADR-004) | `.hsl` Zeilen 6–9 |
| Anpassungen 04/2026 | Initiale Abfahrt für Jalousien auf `EN[10]<EN[9]` beschränkt (ADR-006) | `.hsl` Zeilen 10–11 |

> ⚠️ Inferred: Die vollständige Änderungshistorie vor 03/2026 ist nicht dokumentiert.
> Zwischenstände zwischen dem Original (2006) und den aktuellen Anpassungen sind nicht rekonstruierbar.

---

*Siehe auch:* [§11 Risiken](11-risks-and-technical-debt.md) für Auswirkungen dieser Randbedingungen.
