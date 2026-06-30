<?php
/*
 * Frageformular fuer die bestehende PHP/PostgreSQL-Seite.
 *
 * Erwartung:
 * - $db ist bereits eine gueltige PostgreSQL-Verbindung.
 * - courseinstance existiert bereits.
 * - qaitem und itemrelation wurden mit 01_schema_extension_prof_schmidt.sql angelegt.
 *
 * Das Snippet legt nur neue Fragen an.
 * Antworten und weitere Verknuepfungen werden spaeter direkt in der Datenbank gepflegt.
 *
 * Die eigentliche Speicherlogik liegt in backend/faq_helpers.php.
 */

require_once __DIR__ . '/../backend/faq_helpers.php';

if (!isset($db)) {
    echo '<p>FAQ-Fehler: Es wurde keine PostgreSQL-Verbindung in $db gefunden.</p>';
    return;
}

$ref_id = $_GET['ref_id'] ?? ($_POST['ref_id'] ?? '');
$message = '';
$form_action = $_SERVER['PHP_SELF'] ?? 'main.php';

if ($ref_id === '') {
    echo '<p>Keine Kursreferenz fuer das FAQ-Formular uebergeben.</p>';
    return;
}

$course_id = faq_lookup_course_id($db, $ref_id);

if ($course_id === null) {
    echo '<p>Fuer dieses Modul wurde noch keine FAQ-Struktur gefunden.</p>';
    return;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $honeypot = trim($_POST['website'] ?? '');
    if ($honeypot !== '') {
        $message = 'Frage wurde gespeichert.';
    } else {
        list($success, $message, $question_id) = faq_insert_question(
            $db,
            $course_id,
            $_POST['question_text'] ?? '',
            $_POST['category_id'] ?? ''
        );
    }
}

$category_result = faq_get_categories($db, $course_id);

echo '<h3>Neue FAQ-Frage stellen</h3>';

if ($message !== '') {
    echo '<p><strong>' . htmlspecialchars($message, ENT_QUOTES, 'UTF-8') . '</strong></p>';
}

echo '<form action="' . htmlspecialchars($form_action, ENT_QUOTES, 'UTF-8') . '" method="post">';
echo '<input type="hidden" name="ref_id" value="' . htmlspecialchars($ref_id, ENT_QUOTES, 'UTF-8') . '">';

echo '<p><label for="category_id">Kategorie:</label><br>';
echo '<select id="category_id" name="category_id">';
echo '<option value="">Ohne Kategorie / Allgemein</option>';
if ($category_result) {
    while ($category = pg_fetch_assoc($category_result)) {
        echo '<option value="' . htmlspecialchars($category['id'], ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars($category['title'], ENT_QUOTES, 'UTF-8')
            . '</option>';
    }
}
echo '</select></p>';

echo '<p><label for="question_text">Frage:</label><br>';
echo '<textarea id="question_text" name="question_text" rows="6" cols="80" required></textarea></p>';

echo '<p style="display:none;"><label for="website">Dieses Feld bitte leer lassen:</label>';
echo '<input id="website" type="text" name="website" value=""></p>';

echo '<input type="submit" value="Frage absenden">';
echo '</form>';
?>
