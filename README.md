# FAQ Tool for Websites

Ein einfaches FAQ-Tool für Webseiten, entwickelt am Beispiel einer Elektrotechnik-/Elektronik-Veranstaltung.
Studierende können anonym Fragen stellen. Lehrende können diese Fragen im Adminbereich beantworten, kategorisieren, veröffentlichen, ausblenden oder löschen.

Das Tool ist so aufgebaut, dass es unabhängig von einer bestehenden Website laufen kann und später per Link oder optional per iframe eingebunden werden kann.

---

## Projektidee

Viele Fragen in Vorlesungen, Übungen oder Praktika wiederholen sich. Dieses FAQ-Tool soll Lehrenden helfen, häufige Fragen zentral zu sammeln und strukturiert zu beantworten.

Typische Anwendungsfälle:

* Studierende stellen anonym Fragen zur Veranstaltung.
* Der Professor oder die betreuende Person sieht neue Fragen im Adminbereich.
* Fragen können beantwortet, bearbeitet und veröffentlicht werden.
* Veröffentlichte Fragen erscheinen auf der öffentlichen FAQ-Seite.
* Fragen können nach Kategorie, Status und Suchbegriffen gefiltert werden.

---

## Funktionen

### Öffentlicher Bereich

* Anzeige veröffentlichter Fragen und Antworten
* Suche nach Fragen, Antworten und Kategorien
* Filterung nach Kategorie
* Formular zum Stellen neuer Fragen
* Anonyme Nutzung ohne Studierenden-Login

### Adminbereich

* Login für Lehrende/Admins
* Übersicht über Fragen nach Status
* Filter nach:

  * Status
  * Kategorie
  * Suchbegriff
* Bearbeitung direkt in einer Tabelle:

  * Frage ändern
  * Antwort ändern
  * Kategorie ändern
  * Status ändern
* Kategorieverwaltung:

  * Kategorie hinzufügen
  * Kategorie entfernen
* Status-Erklärung direkt im Adminpanel

### Frage-Status

| Status         | Bedeutung                                                      |
| -------------- | -------------------------------------------------------------- |
| Offen          | Frage wurde eingereicht, aber noch nicht beantwortet           |
| Beantwortet    | Antwort wurde gespeichert, ist aber noch nicht öffentlich      |
| Veröffentlicht | Frage und Antwort sind öffentlich sichtbar                     |
| Ausgeblendet   | Frage bleibt gespeichert, wird aber nicht öffentlich angezeigt |
| Gelöscht       | Frage wird aus der normalen Verwaltung entfernt                |

---

## Technischer Aufbau

Das Projekt besteht aus drei Hauptteilen:

```text
FAQ-Tool
├── frontend
│   ├── index.html
│   ├── ask.html
│   ├── admin-login.html
│   ├── admin.html
│   └── static
│       ├── style.css
│       └── script.js
│
├── backend
│   ├── app.py
│   ├── database.py
│   └── requirements.txt
│
└── database
    └── schema.sql
```

---

## Verwendete Technologien

* HTML
* CSS
* JavaScript
* Python
* FastAPI
* MySQL
* Uvicorn

---

## Voraussetzungen

Für die lokale Nutzung werden benötigt:

* Python 3.10 oder neuer
* MySQL oder MariaDB
* pip
* optional: Git
* optional: VS Code

---

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/MoritzSchallenberg/FAQ-Tool-.git
cd FAQ-Tool-
```

### 2. Virtuelle Python-Umgebung erstellen

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Abhängigkeiten installieren

Falls sich die Datei `requirements.txt` im Backend-Ordner befindet:

```bash
pip install -r backend/requirements.txt
```

Falls sie im Hauptordner liegt:

```bash
pip install -r requirements.txt
```

---

## MySQL-Datenbank einrichten

### 1. MySQL öffnen

```bash
mysql -u root -p
```

### 2. Datenbank importieren

Je nach Speicherort:

```bash
mysql -u root -p < database/schema.sql
```

Die Datei `schema.sql` erstellt die benötigte Datenbankstruktur für Fragen, Antworten, Kategorien und Adminfunktionen.

---

## Konfiguration

Die Zugangsdaten zur Datenbank und Admininformationen sollten nicht direkt im Code stehen.
Dafür kann eine `.env`-Datei genutzt werden.

Beispiel:

```env
MYSQL_HOST=localhost
MYSQL_USER=faq_user
MYSQL_PASSWORD=BITTE_PASSWORT_EINTRAGEN
MYSQL_DATABASE=faq_tool

ADMIN_USERNAME=admin
ADMIN_PASSWORD=BITTE_SICHERES_PASSWORT_SETZEN

COURSE_NAME=Elektrotechnik/Elektronik
SEMESTER=Sommersemester 2026
```

Wichtig:
Die echte `.env`-Datei sollte nicht öffentlich auf GitHub hochgeladen werden.

---

## Server starten

Je nach Projektstruktur:

```bash
uvicorn backend.app:app --reload
```

oder:

```bash
uvicorn app:app --reload
```

Danach ist das Tool lokal erreichbar unter:

```text
http://127.0.0.1:8000
```

---

## Wichtige Seiten

| Seite          | Funktion                               |
| -------------- | -------------------------------------- |
| `/`            | Öffentliche FAQ-Übersicht              |
| `/ask`         | Neue Frage stellen                     |
| `/admin-login` | Login für Admins                       |
| `/admin`       | Adminbereich zur Verwaltung der Fragen |

---

## Einbindung in eine bestehende Website

Das Tool kann unabhängig von einer bestehenden Website laufen.
Die einfachste Einbindung ist ein normaler Link:

```html
<a href="https://dein-server.de/" target="_blank">
    FAQ zur Elektrotechnik/Elektronik öffnen
</a>
```

Optional kann das Tool auch per iframe eingebunden werden:

```html
<iframe
    src="https://dein-server.de/"
    width="100%"
    height="800"
    style="border: none;"
    title="FAQ Elektrotechnik/Elektronik">
</iframe>
```

Hinweis:
Ob eine iframe-Einbindung möglich ist, hängt von der jeweiligen Website und den Server-Sicherheitseinstellungen ab.

---

## Datenschutz-Hinweis

Das Tool ist für eine anonyme Nutzung gedacht. Studierende sollen keine Namen, Matrikelnummern oder sonstige personenbezogene Daten in ihre Fragen schreiben.

Empfohlener Hinweis im Formular:

```text
Bitte geben Sie keine Namen, Matrikelnummern oder sonstige personenbezogene Daten in Ihre Frage ein. Die Frage wird anonym gespeichert und kann nach Freigabe öffentlich im FAQ erscheinen.
```

---

## Sicherheitshinweise

Vor einem echten öffentlichen Einsatz sollten mindestens folgende Punkte geprüft werden:

* starkes Adminpasswort verwenden
* `.env` nicht auf GitHub veröffentlichen
* HTTPS verwenden
* Datenbanknutzer mit eingeschränkten Rechten nutzen
* regelmäßige Backups der Datenbank erstellen
* Eingaben serverseitig prüfen
* Adminbereich nicht ohne Authentifizierung erreichbar machen

---

## Mögliche Erweiterungen

* Export der Fragen und Antworten als CSV oder PDF
* E-Mail-Benachrichtigung bei neuen Fragen
* Markdown- oder LaTeX-Unterstützung für Formeln
* Import von Startfragen
* Rollenverwaltung für mehrere Admins
* automatische Erkennung ähnlicher Fragen
* Statistik über häufige Themen
* optionales iframe-Layout ohne vollständigen Seitenrahmen

---

## Hinweis zum Einsatz

Dieses Projekt ist ein Prototyp bzw. ein kleines Softwaremodul für den Einsatz auf Veranstaltungswebseiten.
Es ist nicht als offizielles System einer Hochschule oder Institution gekennzeichnet, sofern dies nicht ausdrücklich freigegeben wurde.

---

## Lizenz

Dieses Projekt steht unter der GPL-2.0-Lizenz.
Details stehen in der Datei `LICENSE`.

---

## Autor

Moritz Schallenberg
GitHub: `MoritzSchallenberg`
