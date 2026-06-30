# FAQ Tool for Professor Websites

Ein lokales FAQ-Tool für Professoren-Websites.  
Das Projekt ermöglicht es, häufig gestellte Fragen übersichtlich darzustellen und über eine lokale Anwendung zu verwalten.

## Ziel des Projekts

Das Tool wurde entwickelt, um wiederkehrende Fragen von Studierenden strukturiert zu sammeln und einfach bereitzustellen.  
Dadurch können Informationen zentral gepflegt und schneller gefunden werden.

## Funktionen

- Anzeige von FAQ-Fragen und Antworten
- Strukturierte Speicherung der Inhalte
- Lokale Ausführung über Python
- HTML-Seiten für die Benutzeroberfläche
- JSON-Datei zur Speicherung der FAQ-Daten

## Projektstruktur

```text
FAQ-Tool-for-my-Professors-Websites
│
├── app.py
├── data.json
├── index.html
├── ...
└── README.md
```

## Voraussetzungen

Für die Ausführung wird Python benötigt.

```bash
python --version
```

Falls Python noch nicht installiert ist:  
https://www.python.org/

## Installation

Repository herunterladen:

```bash
git clone https://github.com/MoritzSchallenberg/FAQ-Tool-for-my-Professors-Websites.git
```

In den Projektordner wechseln:

```bash
cd FAQ-Tool-for-my-Professors-Websites
```

## Startanleitung

Das Python-Skript starten:

```bash
python app.py
```

Danach kann die lokale Website im Browser geöffnet werden.

Beispiel:

```text
http://localhost:5000
```

## Bedienung

1. Anwendung starten.
2. Lokale Website im Browser öffnen.
3. FAQ-Fragen ansehen.
4. Inhalte über die vorhandene Struktur verwalten.

## Beispiel

### Frage

```text
Wann findet die Prüfung statt?
```

### Antwort

```text
Die Prüfungstermine werden über die offiziellen Hochschulkanäle veröffentlicht.
```

## Verwendete Technologien

- Python
- HTML
- CSS
- JSON

## Mögliche Verbesserungen

- Suchfunktion für Fragen
- Kategorien für verschiedene Themenbereiche
- Bearbeiten und Löschen von Fragen direkt über die Website
- Admin-Bereich für Professoren oder Mitarbeitende
- Import und Export der FAQ-Daten
- Besseres responsives Design für Smartphone und Tablet

## Hinweis

Das Projekt ist als lokales Tool gedacht und kann als Grundlage für eine spätere Integration in eine bestehende Professoren-Website dienen.
