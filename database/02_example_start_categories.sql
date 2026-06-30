-- Optionale Startkategorien fuer ein Modul.
-- Vor Ausfuehrung muss :course_id durch die passende courseinstance-ID ersetzt werden.
--
-- Beispiel psql:
-- \set course_id 8210518
-- \i database/02_example_start_categories.sql

WITH wanted_categories (title, text, sort_order) AS (
    VALUES
        ('Allgemein', 'Allgemeine Fragen zur Veranstaltung', 10),
        ('Vorlesung', 'Fragen zur Vorlesung', 20),
        ('Uebung', 'Fragen zur Uebung', 30),
        ('Praktikum', 'Fragen zum Praktikum', 40),
        ('Pruefung', 'Fragen zur Pruefung', 50)
),
inserted_categories AS (
    INSERT INTO qaitem (title, text, type, source_person, source_person_hidden, status)
    SELECT wanted.title, wanted.text, 'category', 'FAQ-Tool', TRUE, 'published'
    FROM wanted_categories wanted
    WHERE NOT EXISTS (
        SELECT 1
        FROM qaitem qa
        WHERE qa.type = 'category'
          AND lower(qa.title) = lower(wanted.title)
    )
    RETURNING id, title
),
all_categories AS (
    SELECT qa.id, qa.title, wanted.sort_order
    FROM wanted_categories wanted
    JOIN qaitem qa
      ON qa.type = 'category'
     AND lower(qa.title) = lower(wanted.title)
)
INSERT INTO itemrelation (parent_course, parent_qa, child_qa, sort_order)
SELECT
    :course_id,
    NULL,
    id,
    sort_order
FROM all_categories
ON CONFLICT DO NOTHING;
