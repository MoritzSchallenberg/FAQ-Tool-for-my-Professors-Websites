<?php
/*
 * Oeffentliche FAQ-Anzeige fuer die bestehende PHP/PostgreSQL-Seite.
 *
 * Erwartung:
 * - $db ist bereits eine gueltige PostgreSQL-Verbindung.
 * - courseinstance existiert bereits.
 * - qaitem und itemrelation wurden mit 01_schema_extension_prof_schmidt.sql angelegt.
 *
 * Wichtige Anpassungsstelle:
 * Die Kursabfrage liegt in backend/faq_helpers.php in faq_lookup_course_id().
 * Nach der E-Mail wird dort ci.bi_id AS id verwendet. Falls die echte ID-Spalte
 * anders heisst, muss diese Funktion angepasst werden.
 */

require_once __DIR__ . '/../backend/faq_helpers.php';

if (!isset($db)) {
    echo '<p>FAQ-Fehler: Es wurde keine PostgreSQL-Verbindung in $db gefunden.</p>';
    return;
}

$ref_id = $_GET['ref_id'] ?? '';
$search = trim($_GET['faq_search'] ?? '');
$form_action = $_SERVER['PHP_SELF'] ?? 'main.php';

if ($ref_id === '') {
    echo '<p>Keine Kursreferenz fuer die FAQ uebergeben.</p>';
    return;
}

$course_id = faq_lookup_course_id($db, $ref_id);

if ($course_id === null) {
    echo '<p>Fuer dieses Modul wurde noch keine FAQ-Struktur gefunden.</p>';
    return;
}

$faq_public_sql = "
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
        COALESCE(category_questions.category_name, 'Allgemein') AS kategorie,
        q.text AS frage,
        answer_item.text AS antwort
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
      AND (
          $2 = ''
          OR q.text ILIKE '%' || $2 || '%'
          OR answer_item.text ILIKE '%' || $2 || '%'
          OR category_questions.category_name ILIKE '%' || $2 || '%'
      )
    ORDER BY COALESCE(category_questions.category_name, 'Allgemein'), category_questions.question_order, q.created_at DESC
";

$faq_result = pg_query_params($db, $faq_public_sql, array($course_id, $search));

echo '<h3>FAQ</h3>';
echo '<form action="' . htmlspecialchars($form_action, ENT_QUOTES, 'UTF-8') . '" method="get">';
echo '<input type="hidden" name="ref_id" value="' . htmlspecialchars($ref_id, ENT_QUOTES, 'UTF-8') . '">';
echo '<label for="faq_search">FAQ durchsuchen:</label> ';
echo '<input id="faq_search" type="search" name="faq_search" value="' . htmlspecialchars($search, ENT_QUOTES, 'UTF-8') . '">';
echo '<input type="submit" value="Suchen">';
echo '</form>';

echo '<table rules="all" frame="border">';
echo '<tr><td><strong>Kategorie</strong></td><td><strong>Frage</strong></td><td><strong>Antwort</strong></td></tr>';

$count = 0;
if ($faq_result) {
    while ($row = pg_fetch_assoc($faq_result)) {
        $count++;
        echo '<tr>';
        echo '<td>' . htmlspecialchars($row['kategorie'], ENT_QUOTES, 'UTF-8') . '</td>';
        echo '<td>' . nl2br(htmlspecialchars($row['frage'], ENT_QUOTES, 'UTF-8')) . '</td>';
        echo '<td>' . nl2br(htmlspecialchars($row['antwort'], ENT_QUOTES, 'UTF-8')) . '</td>';
        echo '</tr>';
    }
}

if ($count === 0) {
    echo '<tr><td colspan="3">Es wurden keine veroeffentlichten FAQ-Eintraege gefunden.</td></tr>';
}

echo '</table>';
?>
