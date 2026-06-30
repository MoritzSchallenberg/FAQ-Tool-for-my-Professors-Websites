<?php
/*
 * Gemeinsame PHP-Hilfsfunktionen fuer das FAQ-Tool.
 *
 * Diese Datei ist das kleine Backend:
 * - Kurs anhand ref_id finden
 * - Kategorien laden
 * - neue Fragen speichern
 *
 * Voraussetzung: $db ist eine bestehende PostgreSQL-Verbindung.
 */

if (!function_exists('faq_lookup_course_id')) {
    function faq_lookup_course_id($db, $ref_id) {
        $sql = "
            SELECT ci.bi_id AS id
            FROM courseinstance ci
            WHERE ci.numref::text = $1
               OR ci.bi_id::text = $1
            ORDER BY ci.active DESC NULLS LAST, ci.bi_id DESC
            LIMIT 1
        ";

        $result = pg_query_params($db, $sql, array($ref_id));
        $row = $result ? pg_fetch_assoc($result) : false;

        if (!$row || $row['id'] === null || $row['id'] === '') {
            return null;
        }

        return $row['id'];
    }
}

if (!function_exists('faq_get_categories')) {
    function faq_get_categories($db, $course_id) {
        $sql = "
            SELECT qa.id, qa.title
            FROM itemrelation ir
            JOIN qaitem qa ON qa.id = ir.child_qa
            WHERE ir.parent_course = $1
              AND ir.parent_qa IS NULL
              AND qa.type = 'category'
              AND qa.status <> 'deleted'
            ORDER BY ir.sort_order ASC, qa.title ASC
        ";

        return pg_query_params($db, $sql, array($course_id));
    }
}

if (!function_exists('faq_category_belongs_to_course')) {
    function faq_category_belongs_to_course($db, $course_id, $category_id) {
        $sql = "
            SELECT qa.id
            FROM itemrelation ir
            JOIN qaitem qa ON qa.id = ir.child_qa
            WHERE ir.parent_course = $1
              AND ir.parent_qa IS NULL
              AND qa.id = $2
              AND qa.type = 'category'
              AND qa.status <> 'deleted'
            LIMIT 1
        ";

        $result = pg_query_params($db, $sql, array($course_id, $category_id));
        return $result && pg_fetch_assoc($result);
    }
}

if (!function_exists('faq_insert_question')) {
    function faq_insert_question($db, $course_id, $question_text, $category_id_raw) {
        $question_text = trim($question_text);
        $category_id = ctype_digit((string) $category_id_raw) ? (string) $category_id_raw : '';

        if (strlen($question_text) < 5) {
            return array(false, 'Die Frage ist zu kurz.', null);
        }

        pg_query($db, 'BEGIN');

        $title = substr($question_text, 0, 120);
        $hidden_text = 'created_from=faq_frontend';

        $insert_question_sql = "
            INSERT INTO qaitem (title, text, hidden_text, type, source_person, source_person_hidden, status)
            VALUES ($1, $2, $3, 'question', 'FAQ-Formular', TRUE, 'open')
            RETURNING id
        ";
        $insert_result = pg_query_params($db, $insert_question_sql, array($title, $question_text, $hidden_text));
        $question_row = $insert_result ? pg_fetch_assoc($insert_result) : false;

        if (!$question_row) {
            pg_query($db, 'ROLLBACK');
            return array(false, 'Die Frage konnte nicht gespeichert werden.', null);
        }

        $question_id = $question_row['id'];

        if ($category_id !== '') {
            if (!faq_category_belongs_to_course($db, $course_id, $category_id)) {
                pg_query($db, 'ROLLBACK');
                return array(false, 'Die ausgewaehlte Kategorie wurde nicht gefunden.', null);
            }

            $relation_sql = "
                INSERT INTO itemrelation (parent_course, parent_qa, child_qa, sort_order)
                VALUES (NULL, $1, $2, 100)
            ";
            $relation_result = pg_query_params($db, $relation_sql, array($category_id, $question_id));
        } else {
            $relation_sql = "
                INSERT INTO itemrelation (parent_course, parent_qa, child_qa, sort_order)
                VALUES ($1, NULL, $2, 100)
            ";
            $relation_result = pg_query_params($db, $relation_sql, array($course_id, $question_id));
        }

        if (!$relation_result) {
            pg_query($db, 'ROLLBACK');
            return array(false, 'Die Frage konnte nicht verknuepft werden.', null);
        }

        pg_query($db, 'COMMIT');
        return array(true, 'Frage wurde gespeichert.', $question_id);
    }
}
?>
