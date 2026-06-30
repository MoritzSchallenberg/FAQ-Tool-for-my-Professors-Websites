# FAQ Tool PIKS - Prof.-Schmidt-Version

Diese Version ist nur fuer die Integration in die bestehende PHP/PostgreSQL-Webseite gedacht.
Alle Python-, FastAPI- und JSON-Demo-Dateien wurden entfernt. Enthalten ist aber ein
kleines PHP-Frontend und PHP-Backend, damit Studierende wieder Fragen stellen koennen.

## Enthaltene Dateien

```text
database/
  01_schema_extension_prof_schmidt.sql
  02_example_start_categories.sql
  03_render_queries.sql

backend/
  faq_helpers.php

frontend/
  faq_public_page.php
  faq_ask_page.php

php_integration/
  faq_public_snippet.php
  faq_ask_snippet.php

anleitung/
  Anleitung_Prof_Schmidt.docx
```

## Grundstruktur

Die Datenbank arbeitet mit zwei neuen Tabellen:

- `qaitem`: speichert Kategorien, Fragen und Antworten.
- `itemrelation`: verbindet Kurs, Kategorie, Frage und Antwort.

Die vorhandene Tabelle `courseinstance` wird vorausgesetzt und nicht veraendert.

## Frontend und Backend

- `frontend/faq_public_page.php` ist eine einfache Beispielseite fuer die FAQ-Anzeige.
- `frontend/faq_ask_page.php` ist eine einfache Beispielseite fuer das Frageformular.
- `backend/faq_helpers.php` enthaelt die PHP-Funktionen zum Suchen des Kurses, Laden der Kategorien und Speichern neuer Fragen.
- `php_integration/faq_public_snippet.php` und `php_integration/faq_ask_snippet.php` koennen direkt in die bestehende Website eingebunden werden.

Die Frontend-Dateien sind bewusst PHP-Dateien, nicht statisches HTML. Grund: Nur PHP kann direkt mit der vorhandenen PostgreSQL-Verbindung arbeiten und Fragen in `qaitem`/`itemrelation` speichern.

## Wichtig vor der Integration

Die E-Mail nennt `ci.bi_id AS id`. Deshalb nutzt `backend/faq_helpers.php` standardmaessig:

```sql
SELECT ci.bi_id AS id
FROM courseinstance ci
```

Falls die echte Kurs-ID in der bestehenden Datenbank anders heisst, muss diese eine Abfrage
in `faq_lookup_course_id()` angepasst werden.

## Reihenfolge

1. Datenbank sichern.
2. `database/01_schema_extension_prof_schmidt.sql` in PostgreSQL ausfuehren.
3. Kurs-ID der passenden `courseinstance` bestimmen.
4. Kategorien anlegen und ueber `itemrelation.parent_course` mit dem Kurs verknuepfen.
5. `backend/faq_helpers.php` mit hochladen.
6. `php_integration/faq_public_snippet.php` an der FAQ-Anzeigestelle einbinden.
7. `php_integration/faq_ask_snippet.php` an der Frageformular-Stelle einbinden.
8. Alternativ die Beispielseiten aus `frontend/` als Startpunkt verwenden.
9. Antworten spaeter als `qaitem` mit `type='answer'` anlegen.
10. Antworten ueber `itemrelation` unter die passende Frage haengen.
11. Frage und Antwort auf `status='published'` setzen, damit sie oeffentlich erscheinen.

Details stehen in `anleitung/Anleitung_Prof_Schmidt.docx`.

