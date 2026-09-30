# Source Document Inventory

**Generated:** 2026-04-29
**Updated:** 2026-04-29 (ADRs und Anforderungsdokument hinzugefügt)
**Purpose:** Comprehensive inventory of all source documents with arc42 section mapping
and cross-reference analysis for the Gira Homeserver Jalousie Lamellennachführung block.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Architecture Decision Records (SourceDocuments/adr/) | 6 |
| Requirements / Specifications (SourceDocuments/SpecsAndRequirments/) | 1 |
| Project documentation (CLAUDE.md) | 1 |
| Implementation source (HSL) | 1 |
| Operational rules (.claude/rules/) | 4 |
| **Total usable sources** | **13** |

> **Note:** `SourceDocuments/research/` und `SourceDocuments/lead-machine.pdf` existieren
> nicht im Repository. Alle anderen Scan-Verzeichnisse sind vorhanden. Siehe [Gaps](#gaps).

---

## Document Catalog

### Architecture Decision Records (`SourceDocuments/adr/`)

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 1 | `ADR-001-jalousie-raffstore-geraetetyp.md` | Accepted | pre-03/2026 | EN[12] als Gerätetyp-Diskriminator; Jalousie vs. Raffstore | §01, §05, §09 | Supersedes: keine |
| 2 | `ADR-002-sn6-abfahrt-flag.md` | Accepted | 03/2026 | SN[6] schützt Manuell-Erkennung während Abfahrt; 180-s-Timeout | §08, §09 | Supersedes: pre-03/2026-Verhalten |
| 3 | `ADR-003-sn6-reset-zeitpunkt.md` | Accepted | 03/2026 | SN[6] Reset erst nach Lamellenbewegung (EC[12]), nicht bei EC[10] | §06, §09 | Supersedes: pre-03/2026-Verhalten; ergänzt ADR-002 |
| 4 | `ADR-004-endlagen-ausschluss.md` | Accepted | 03/2026 | EN[12]<98 schließt 100%-Endlage von Manuell-Erkennung aus | §05, §09 | Ergänzt ADR-002 |
| 5 | `ADR-005-ec2-uebergangsmaskierung.md` | Accepted | pre-03/2026 | `not EC[2]` maskiert Manuell-Erkennung beim Beschattungs-Umschalten | §06, §09 | — |
| 6 | `ADR-006-jalousie-initiale-abfahrt.md` | Accepted | 04/2026 | Jalousie: Abfahrt nur wenn EN[10]<EN[9] | §05, §09 | Supersedes: pre-04/2026-Verhalten; ergänzt ADR-001 |

### Requirements / Specifications (`SourceDocuments/SpecsAndRequirments/`)

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 7 | `anforderungen.md` | Draft | 2026-04-29 | Stakeholder, funktionale Anforderungen F-01–F-08, NF-01–NF-03, offene Fragen | §01, §02, §03, §08, §10 | Abgeleitet aus CLAUDE.md und .hsl; noch nicht formal abgenommen |

### Project Documentation (repo root)

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 8 | `CLAUDE.md` | Active | — | Project overview, HSL format, variable reference, logic architecture, design decisions, encoding | §01–§09, §12 | Primärquelle für alle ADRs |
| 9 | `README.md` | Active | — | Claude Code harness setup, CLAUDE.md template usage | (operational, not architecture) | — |

### Implementation Source

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 10 | `19822_Jalousie Lamellennachführung_optimiert.hsl` | Active v3.2.5 | 04/2026 | Vollständige HSL-Implementierung: Header, Eingänge, Speicher, Ausgänge, 45 Logikregeln | §04, §05, §06, §09 | CLAUDE.md dokumentiert diese Datei; ADR-003/006 datieren Änderungen |

### Operational Rules (`.claude/rules/`)

| # | File | Status | Date | Key Topics | Arc42 Sections | Notes |
|---|------|--------|------|------------|----------------|-------|
| 11 | `.claude/rules/git-safety.md` | Active | — | Commit-Protokoll, Branch-Workflow | §02 (Prozesskontrolle) | Boilerplate; nicht HSL-architekturspezifisch |
| 12 | `.claude/rules/go-conventions.md` | Active | — | Go Error Handling, Naming, Testing | (N/A — kein Go-Code im Projekt) | Template-Artefakt; nicht anwendbar |
| 13 | `.claude/rules/security.md` | Active | — | Credential Safety, Path Safety | (N/A — lokale HSL-Datei, kein Netzwerkcode) | Template-Artefakt; nicht anwendbar |
| 14 | `.claude/rules/streb-architecture.md` | Active | — | Provider/Installer Go Interface-Muster | (N/A — kein Go-Code) | Template-Artefakt; nicht anwendbar |

---

## Extracted Claims

### From CLAUDE.md

#### §01 Introduction and Goals

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| The block implements "Jalousie Lamellennachführung" — automatic sun-position tracking for adjustable blinds with lamella angle positioning and manual-override detection | CLAUDE.md § Projektübersicht | explicit |
| Two device types are supported: Jalousie (EN[12]=0, no lamella feedback) and Raffstore (EN[12]>0, lamella feedback available) | CLAUDE.md § Variablenreferenz / Designentscheidungen; ADR-001 | explicit |
| Runs without a build process, package manager, or test suite | CLAUDE.md § Projektübersicht | explicit |
| Stakeholder: Bewohner, Installateur, Gira Homeserver (Plattform) | SpecsAndRequirments/anforderungen.md § Stakeholder | explicit (Draft) |

#### §02 Constraints

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| The .hsl file uses ISO-8859-1 (Latin-1) encoding; must not be saved as UTF-8 | CLAUDE.md § Zeichenkodierung; anforderungen.md NF-02 | explicit |
| HSL is a proprietary Gira format; no public specification exists in the repository | CLAUDE.md § Projektübersicht | explicit |
| Deployment exclusively via GPA (Gira Project Assistant) — direct file upload, no CI/CD | CLAUDE.md § Projektübersicht; anforderungen.md NF-01 | explicit |
| File version is V 3.2.5; original author Matthias Schmidt, 2006 | .hsl lines 3–4 | explicit |
| Modifications in 03/2026 (SN[6] timing, EC[10], endlage exclusion) and 04/2026 (Jalousie travel condition) | .hsl lines 6–11; ADR-003, ADR-006 | explicit |

#### §03 Context and Scope

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Sun inclination received via EN[1], triggered ~every 2 minutes by external "Sonnepur" service | CLAUDE.md § Variablenreferenz | explicit |
| Block consumes 12 inputs (EN[1]–EN[12]) from the Gira Homeserver automation bus | CLAUDE.md § Variablenreferenz | explicit |
| Block produces 4 outputs: lamella target % (Ausgang 1), blind target % (Ausgang 2), up/down command (Ausgang 3), status debug text (Ausgang 4) | CLAUDE.md § Variablenreferenz | explicit |
| Executes within Gira Homeserver runtime; no external APIs or databases | CLAUDE.md § Projektübersicht | explicit |
| Shading enable/disable (EN[2]) and cycle trigger (EN[3]) come from upstream automation logic | CLAUDE.md § Variablenreferenz | inferred |

#### §04 Solution Strategy

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Pipe-separated opcode format; opcodes 5000–5012 cover header, parameters, inputs, storage, outputs, and logic rules | CLAUDE.md § HSL-Dateiformat | explicit |
| 5012 logic rule fires when condition is true, sets a storage cell (sn_idx) or output (out_idx) | CLAUDE.md § HSL-Dateiformat | explicit |
| Rules execute sequentially, top-to-bottom, every cycle | CLAUDE.md § Logik-Architektur | explicit |
| EC[N] true only in the cycle when EN[N] changes; EA[N] holds previous value | CLAUDE.md § Variablenreferenz | explicit |

#### §05 Building Block View

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Logic organized into 11 named functional sections executing per cycle | CLAUDE.md § Logik-Architektur | explicit |
| Section 1 (Sollwertberechnung): SN[2] from inclination formula or rest value; clamped to [EN[5], EN[6]] | CLAUDE.md § Logik-Architektur | explicit |
| Section 2 (Positions-Flags): SN[3] (blind at target ±3%) and SN[4] (lamella deviation >EN[4]) | CLAUDE.md § Logik-Architektur | explicit |
| Section 3 (Manuell-Vorrang-Erkennung): Clears SN[5]; skips endlage (≥98%), EC[2] transitions, active travel (SN[6]==1) | CLAUDE.md § Logik-Architektur; ADR-002, ADR-004, ADR-005 | explicit |
| Section 4 (Behang-Automatik): EC[3] sends blind to EN[9]; Jalousie only when EN[10]<EN[9]; Raffstore when SN[3]==0 | CLAUDE.md § Logik-Architektur; ADR-001, ADR-006 | explicit |
| Section 5 (Lamellennachführung EC[10]): On blind arrival sends lamella to SN[2] or EN[7] | CLAUDE.md § Logik-Architektur; ADR-003 | explicit |
| Section 6 (Abfahrt-Flag Reset): Clears SN[6] when lamella leaves 100% or blind arrives (Jalousie) | CLAUDE.md § Logik-Architektur; ADR-003 | explicit |
| Section 7 (Lamellennachführung EC[1]): Re-tracks lamella on inclination change; minimum threshold EN[4] | CLAUDE.md § Logik-Architektur | explicit |
| Section 8 (Lamellennachführung EC[2]): Immediate lamella movement when shading switches | CLAUDE.md § Logik-Architektur; ADR-005 | explicit |
| Section 9 (Manuell-Vorrang-Rücknahme): Restores SN[5]=1 when position returns within tolerance | CLAUDE.md § Logik-Architektur | explicit |
| Section 10 (Timeout): Clears SN[6] after 180 seconds; safety fallback | CLAUDE.md § Logik-Architektur; ADR-002 | explicit |
| Section 11 (Statustext): Always-firing rule writes all SN values to output 4 | CLAUDE.md § Logik-Architektur | explicit |
| Lamella setpoint formula: `round(((90 - EN[1]) * (EN[6] - EN[5]) / 90) + EN[5] + EN[8])` | CLAUDE.md § Designentscheidungen; anforderungen.md F-01 | explicit |

#### §06 Runtime View

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Homeserver evaluates all rules each cycle, top-to-bottom | CLAUDE.md § Logik-Architektur | explicit |
| EC[3] (cycle trigger) initiates blind travel; EA[3]==0 confirms rising edge | .hsl lines 80–92; ADR-006 | explicit |
| EC[10] triggers lamella adjustment when blind arrives at target (±3%) | .hsl lines 101–112; ADR-003 | explicit |
| EC[1] triggers lamella re-tracking for Raffstore if change ≥EN[4] | .hsl lines 129–131 | explicit |
| EC[2] triggers immediate lamella movement; suppresses manual detection in that cycle | .hsl lines 138–141; ADR-005 | explicit |
| SN[6] reset path: EC[12] fires and EN[12]<98 (Raffstore); or EC[10] arrives and EN[12]==0 (Jalousie) | .hsl lines 119–120; ADR-003 | explicit |

#### §07 Deployment View

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Deployed via GPA by uploading the .hsl file to the Gira Homeserver | CLAUDE.md § Projektübersicht | explicit |
| No build process, no package manager, no automated tests | CLAUDE.md § Projektübersicht | explicit |
| No CI/CD pipeline | CLAUDE.md § Projektübersicht | inferred |
| No staging/production environment distinction documented | — | gap |
| Open question: minimum supported Gira Homeserver firmware version | anforderungen.md OQ-01 | gap |

#### §08 Crosscutting Concepts

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| Safety timeout: SN[6] cleared after 180 s to prevent permanent travel-lock | CLAUDE.md § Logik-Architektur §10; .hsl line 163; ADR-002 | explicit |
| Debug observability: always-firing status rule writes all SN state to output 4 | CLAUDE.md § Logik-Architektur §11; .hsl line 170 | explicit |
| Tolerance bands: ±3% for blind position (SN[3]), EN[4]% for lamella deviation | CLAUDE.md § Variablenreferenz | explicit |
| No persistent state: SN values are in-memory registers, reset on Homeserver restart | — | inferred |

#### §09 Architecture Decisions

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| **ADR-001:** EN[12]==0 as Jalousie discriminator — single input doubles as device-type selector | ADR-001; CLAUDE.md § Designentscheidungen | explicit |
| **ADR-002:** SN[6] movement flag guards manual override detection; 180-s timeout fallback | ADR-002; CLAUDE.md § Designentscheidungen | explicit |
| **ADR-003:** SN[6] reset after lamella movement completes (EC[12]), not at blind arrival (EC[10]) | ADR-003; CLAUDE.md § Designentscheidungen | explicit |
| **ADR-004:** EN[12]<98 endlage exclusion — 100%-retracted position not interpreted as manual override | ADR-004; CLAUDE.md § Designentscheidungen | explicit |
| **ADR-005:** `not EC[2]` transition gate — manual detection suppressed in shading-toggle cycle | ADR-005; CLAUDE.md § Designentscheidungen | explicit |
| **ADR-006:** Jalousie initial travel only when EN[10]<EN[9] (added 04/2026) | ADR-006; .hsl lines 10–11 | explicit |

#### §10 Quality Requirements

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| NF-01: Travel-lock must be released within 180 s (timeout fallback) | anforderungen.md NF-01 | explicit (Draft) |
| NF-02: .hsl file must use ISO-8859-1 encoding | anforderungen.md NF-02 | explicit (Draft) |
| NF-03: Block must work correctly for both Jalousie and Raffstore device types | anforderungen.md NF-03 | explicit (Draft) |
| No SLOs, false-detection-rate targets, or response-time budgets formally documented | anforderungen.md § Offene Fragen OQ-04 | gap |

#### §11 Risks and Technical Debt

| Claim | Source Location | Confidence |
|-------|----------------|------------|
| No formal risk register; all risks below are inferred | — | gap |
| Risk: No automated test suite — correctness only verifiable by deploying to physical hardware | CLAUDE.md § Projektübersicht | inferred |
| Risk: ISO-8859-1 encoding is fragile — incorrect save as UTF-8 silently corrupts Umlauts | CLAUDE.md § Zeichenkodierung | inferred |
| Risk: SN state volatile — Homeserver restart resets SN[5]=1, may briefly re-enable automation after manual override | — | inferred |
| Risk: v3.2.5 is derived from a 2006 third-party block; full modification history only partially captured in header | .hsl lines 3–11 | inferred |
| Open question: is the 180-s timeout sufficient for all installed blind configurations? | anforderungen.md OQ-02 | inferred |

#### §12 Glossary

Extracted from CLAUDE.md, .hsl file, and ADRs:

| Term | Definition |
|------|-----------|
| Jalousie | Venetian blind with horizontal slats; no lamella-position feedback (EN[12]=0) |
| Raffstore | External venetian blind with lamella-position feedback (EN[12]>0) |
| Lamelle | Individual slat of a venetian blind; the element whose angle is controlled |
| Behang | The full blind drop/covering assembly (not individual slats) |
| Inklination | Sun elevation angle (0–90°), supplied as % from Sonnepur |
| Abfahrt | Motor-driven travel of the blind to a target position |
| Endlage | End position; 100% = fully closed/retracted |
| Sonnepur | External Gira Homeserver service broadcasting sun inclination every ~2 min |
| GPA | Gira Project Assistant — proprietary IDE/loader for Gira Homeserver blocks |
| HSL | Homeserver Script Language — proprietary pipe-separated rule format |
| Sollwert | Target/setpoint value |
| IST / Istwert | Actual/current measured value |
| EN[N] | Input register N — reads from the Gira automation bus |
| SN[N] | Storage register N — internal in-memory cell |
| EC[N] | Edge-change trigger — true exactly in the cycle when EN[N] changes |
| EA[N] | Previous value of EN[N] from the preceding cycle |
| sbC / sBC / send | Gira output signal type identifiers |
| Manuell-Vorrang | Manual override — automation suppressed because user adjusted the blind |
| Automatik-Flag | SN[5]=1 means automation active; SN[5]=0 means manual override active |
| Abfahrt-Flag | SN[6]=1 means blind or lamella is currently traveling |

---

## Arc42 Coverage Map

| Arc42 Section | Source Documents | Coverage |
|--------------|-----------------|----------|
| §01 Introduction and Goals | CLAUDE.md § Projektübersicht; anforderungen.md § Stakeholder | adequate — purpose and stakeholders stated; no formal quality goals yet |
| §02 Constraints | CLAUDE.md § Projektübersicht, § Zeichenkodierung; .hsl header; anforderungen.md NF-01–03 | adequate |
| §03 Context and Scope | CLAUDE.md § Variablenreferenz, § Projektübersicht; anforderungen.md F-01–08 | adequate |
| §04 Solution Strategy | CLAUDE.md § HSL-Dateiformat, § Logik-Architektur | adequate |
| §05 Building Block View | CLAUDE.md § Logik-Architektur, § Variablenreferenz; .hsl (full source); ADR-001, ADR-006 | rich |
| §06 Runtime View | CLAUDE.md § Logik-Architektur; .hsl (rule triggers); ADR-003, ADR-005 | adequate |
| §07 Deployment View | CLAUDE.md § Projektübersicht | sparse — GPA mentioned; no firmware version, no environment details |
| §08 Crosscutting Concepts | CLAUDE.md § Logik-Architektur §10–11; .hsl lines 163, 170; ADR-002 | sparse |
| §09 Architecture Decisions | ADR-001 bis ADR-006; CLAUDE.md § Designentscheidungen; .hsl header | rich |
| §10 Quality Requirements | anforderungen.md NF-01–03 (Draft) | sparse — NF-Anforderungen vorhanden, keine SLOs/Qualitätsziele |
| §11 Risks and Technical Debt | (alle inferred, kein formales Risikoregister) | none formal |
| §12 Glossary | CLAUDE.md § Variablenreferenz; .hsl comments; ADR-001 | rich |

---

## Contradictions

No contradictions detected between sources. CLAUDE.md, the .hsl implementation, and all ADRs are consistent. The ADR dates match the .hsl header change notes.

### SN[4] defined but unused as a condition trigger (minor tension)

- **CLAUDE.md / anforderungen.md:** SN[4] is described as "Flag: Lamelle weicht vom Sollwert ab".
- **.hsl implementation:** SN[4] is computed (lines 58–60) but never appears as a condition in any 5012 rule; it appears only in the debug status text (line 170).
- **Severity:** minor — flag is correctly described; role is diagnostic-only.
- **Recommended resolution:** Add a note in CLAUDE.md § Variablenreferenz that SN[4] is currently diagnostic-only, or implement a rule that uses it.

---

## Gaps

### §10 Quality Requirements — Keine formalen Qualitätsziele

`anforderungen.md` enthält NF-Anforderungen (Draft), aber keine SLOs, keine Falsch-Erkennungsrate und keine Response-Time-Budgets.

**Fehlend:** Response-Time-Budget für Lamellenanpassung nach Behang-Ankunft; maximale Fahrtzeit (relevant für 180-s-Timeout); Verfügbarkeitsziel.

**Empfehlung:** Anforderungen in `anforderungen.md` mit dem Systembesitzer abzunehmen und OQ-01–04 zu schließen.

### §11 Risks and Technical Debt — Kein formales Risikoregister

Alle Risiken sind aus dem Code inferiert. Kein Impact/Likelihood-Assessment vorhanden.

**Empfehlung:** Inferred-Risiken aus §11 in ein formales Risikoregister in `SourceDocuments/` überführen.

### §07 Deployment View — Fehlende Umgebungsdetails

GPA-Upload ist bekannt, aber Firmware-Version, Multi-Instanz-Handling und Backup-Prozedur sind nicht dokumentiert.

**Empfehlung:** Deployment-Notizen oder Runbook in `SourceDocuments/` ergänzen.

### SourceDocuments/research/ — Nicht vorhanden

Kein Forschungsmaterial zur Sonnenstand-Algorithmus-Wahl, zur Inklinationsformel oder zu Motorsteuerungs-Referenzen.

### SourceDocuments/lead-machine.pdf — Nicht vorhanden

Zweck des Dokuments unbekannt; Auswirkung auf arc42 kann nicht beurteilt werden.

---

## Supersession Chain

| Superseded Document / Behavior | Superseded By | Date | Reason |
|-------------------------------|---------------|------|--------|
| .hsl pre-03/2026: SN[6] reset bei EC[10] (Behang-Ankunft) | ADR-003 / .hsl v3.2.5 (03/2026) | 03/2026 | SN[6] Reset erst nach Lamellenbewegung (EC[12]) |
| .hsl pre-03/2026: keine Endlage-Ausnahme in Manuell-Erkennung | ADR-004 / .hsl v3.2.5 (03/2026) | 03/2026 | EN[12]<98 schließt 100%-Endlage aus |
| .hsl pre-04/2026: Jalousie-Abfahrt ohne Richtungsprüfung | ADR-006 / .hsl v3.2.5 (04/2026) | 04/2026 | Abfahrt nur wenn EN[10]<EN[9] |
| Designentscheidungen nur in CLAUDE.md-Prosa | ADR-001 bis ADR-006 | 2026-04-29 | Formale ADR-Dateien in SourceDocuments/adr/ |
