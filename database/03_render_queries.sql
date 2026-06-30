-- Beispielabfragen fuer die vorhandene PHP-Renderfunktion.
-- Diese Datei muss nicht importiert werden. Sie dient als Vorlage.

-- Alle FAQ-Items anzeigen.
SELECT
    qa.id,
    qa.type,
    qa.status,
    qa.title,
    qa.text,
    qa.hidden_text,
    qa.source_person,
    qa.source_person_hidden,
    qa.created_at
FROM qaitem qa
ORDER BY qa.created_at DESC, qa.id DESC;

-- Offene Fragen anzeigen.
SELECT
    qa.id,
    qa.status,
    qa.title,
    qa.text,
    qa.created_at
FROM qaitem qa
WHERE qa.type = 'question'
  AND qa.status = 'open'
ORDER BY qa.created_at DESC, qa.id DESC;

-- Relationen kontrollieren.
SELECT
    ir.id,
    ir.parent_course,
    ir.parent_qa,
    parent_qa.title AS parent_qa_title,
    parent_qa.type AS parent_qa_type,
    ir.child_qa,
    child_qa.title AS child_qa_title,
    child_qa.type AS child_qa_type,
    ir.sort_order
FROM itemrelation ir
LEFT JOIN qaitem parent_qa ON parent_qa.id = ir.parent_qa
JOIN qaitem child_qa ON child_qa.id = ir.child_qa
ORDER BY ir.parent_course NULLS LAST, parent_qa.title NULLS LAST, ir.sort_order, ir.id;

-- Oeffentliche FAQ-Struktur fuer einen Kurs anzeigen.
-- Parameter in PHP: $1 = courseinstance-ID, also der Wert aus itemrelation.parent_course.
WITH category_questions AS (
    SELECT
        q.id AS question_id,
        category_item.id AS category_id,
        category_item.title AS category_name,
        question_relation.sort_order AS question_order
    FROM itemrelation category_relation
    JOIN qaitem category_item
        ON category_item.id = category_relation.child_qa
       AND category_item.type = 'category'
       AND category_item.status <> 'deleted'
    JOIN itemrelation question_relation
        ON question_relation.parent_course IS NULL
       AND question_relation.parent_qa = category_item.id
    JOIN qaitem q
        ON q.id = question_relation.child_qa
       AND q.type = 'question'
    WHERE category_relation.parent_course = $1
      AND category_relation.parent_qa IS NULL
    UNION
    SELECT
        q.id AS question_id,
        NULL::bigint AS category_id,
        NULL::text AS category_name,
        direct_relation.sort_order AS question_order
    FROM itemrelation direct_relation
    JOIN qaitem q
        ON q.id = direct_relation.child_qa
       AND q.type = 'question'
    WHERE direct_relation.parent_course = $1
      AND direct_relation.parent_qa IS NULL
)
SELECT
    COALESCE(category_questions.category_name, 'Allgemein') AS category,
    q.text AS question,
    answer_item.text AS answer,
    q.id AS question_id
FROM category_questions
JOIN qaitem q ON q.id = category_questions.question_id
LEFT JOIN LATERAL (
    SELECT string_agg(answer.text, E'\n\n' ORDER BY answer_relation.sort_order, answer.id) AS text
    FROM itemrelation answer_relation
    JOIN qaitem answer
        ON answer.id = answer_relation.child_qa
       AND answer.type = 'answer'
       AND answer.status = 'published'
    WHERE answer_relation.parent_course IS NULL
      AND answer_relation.parent_qa = q.id
) answer_item ON TRUE
WHERE q.status = 'published'
  AND answer_item.text IS NOT NULL
ORDER BY COALESCE(category_questions.category_name, 'Allgemein'), category_questions.question_order, q.created_at DESC;
