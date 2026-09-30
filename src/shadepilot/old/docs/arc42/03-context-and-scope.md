# §03 Kontextabgrenzung

(Source: CLAUDE.md § Projektübersicht, § Variablenreferenz;
SourceDocuments/SpecsAndRequirments/anforderungen.md F-01–F-08)

---

## Systemgrenze

Der Baustein **Jalousie Lamellennachführung** ist ein HSL-Baustein, der innerhalb des
Gira-Homeserver-Laufzeitsystems ausgeführt wird. Er hat keinen direkten Zugriff auf externe
Netzwerkdienste, Datenbanken oder Betriebssystemressourcen. Alle Kommunikation erfolgt über
den Gira-Automatisierungsbus über die definierten Eingänge (`EN[1]`–`EN[12]`) und
Ausgänge (1–4).

---

## Fachlicher Kontext

```mermaid
graph LR
    subgraph Extern
        SUN["Sonnepur\n(Sonnenstand-Dienst)"]
        MOTOR["Motorsteuerung\n(Jalousie / Raffstore)"]
        UPSTR["Upstream-Logik\n(Zeitprogramm, Sensoren)"]
        GPA["GPA\n(Gira Project Assistant)"]
    end

    subgraph HS["Gira Homeserver"]
        BUS["Automatisierungsbus"]
        BLOCK["Lamellen-Nachführung\n(HSL-Baustein 19822)"]
    end

    SUN -->|"EN[1]: Inklination %\n~alle 2 Min"| BUS
    UPSTR -->|"EN[2]: Beschattung Ein/Aus\nEN[3]: Zyklus Ein/Aus\nEN[9..11]: Konfiguration"| BUS
    MOTOR -->|"EN[10]: Behang IST %\nEN[12]: Lamelle IST %"| BUS
    BUS -->|"EN[1..12]"| BLOCK

    BLOCK -->|"Ausgang 1: Lamelle Soll %"| BUS
    BLOCK -->|"Ausgang 2: Behang Soll %"| BUS
    BLOCK -->|"Ausgang 3: Auf/Ab-Befehl"| BUS
    BLOCK -->|"Ausgang 4: Statustext"| BUS
    BUS -->|"Lamelle Soll, Behang Soll,\nAuf/Ab"| MOTOR

    GPA -.->|"Deployment\n(.hsl Upload)"| BLOCK
```

---

## Technischer Kontext

### Eingänge (EN)

| Eingang | Beschreibung | Herkunft |
|---------|-------------|---------|
| `EN[1]` | Sonnen-Inklination (%) — Trigger ca. alle 2 Minuten | Sonnepur-Dienst |
| `EN[2]` | Beschattung Ein (1) / Aus (0) | Upstream-Logik (Zeitplan, Sensor) |
| `EN[3]` | Zyklus Ein (1) / Aus (0) — Aktiviert Behang-Automatik | Upstream-Logik |
| `EN[4]` | Mindeständerung / Toleranz (%) | Konfigurationsparameter (GPA) |
| `EN[5]` | Lamellenstellung waagrecht (%) | Konfigurationsparameter (GPA) |
| `EN[6]` | Lamellenstellung senkrecht (%) | Konfigurationsparameter (GPA) |
| `EN[7]` | Lamellenstellung bei Beschattung Aus (%) | Konfigurationsparameter (GPA) |
| `EN[8]` | Offset Lamellenwinkel +/- (%) | Konfigurationsparameter (GPA) |
| `EN[9]` | Behang-Zielposition bei Sonnenschutz (%) | Konfigurationsparameter / Upstream |
| `EN[10]` | Behang IST-Position (%) | Motorsteuerung (Rückmeldung) |
| `EN[11]` | Steuerung: 1 = Behang AUF bei Beschattung AUS | Konfigurationsparameter (GPA) |
| `EN[12]` | Lamelle IST-Position (%) — **0 bei Jalousie, >0 bei Raffstore** | Motorsteuerung / Jalousie-Typ |

### Ausgänge

| Ausgang | Beschreibung | Ziel |
|---------|-------------|------|
| Ausgang 1 (`sbC`) | Lamellen-Sollwert (%) | Motorsteuerung (Lamelle) |
| Ausgang 2 (`send`) | Behang-Sollwert (%) | Motorsteuerung (Behang) |
| Ausgang 3 | Auf/Ab-Befehl | Motorsteuerung (Fahrtrichtung) |
| Ausgang 4 | Statustext (Debug-String) | Gira-Bus (Diagnose / Visualisierung) |

---

## Externe Schnittstellen

| Schnittstelle | Richtung | Protokoll / Format | Beschreibung |
|--------------|----------|-------------------|-------------|
| Sonnepur | → Eingang | Gira-Bus-Analogwert | Inklinationswert 0–100 %, Trigger ca. alle 2 Min. |
| Motorsteuerung | ↔ bidirektional | Gira-Bus-Analog + Digital | Sollwerte aus, IST-Position zurück |
| Upstream-Logik | → Eingang | Gira-Bus-Binär/Analog | Beschattung, Zyklus, Konfigurationswerte |
| GPA | → Deployment | Proprietäres Gira-Protokoll | Einmalig: `.hsl`-Datei hochladen |

---

*Siehe auch:* [§05 Bausteinsicht](05-building-block-view.md) für die interne Struktur |
[§12 Glossar](12-glossary.md) für Begriffsdefinitionen
