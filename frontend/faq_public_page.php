<?php
/*
 * Beispiel-Frontend fuer die oeffentliche FAQ-Anzeige.
 */

// Beispiel:
// require_once '/pfad/zur/bestehenden/db_verbindung.php';
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <title>FAQ</title>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="https://www.fh-aachen.de/typo3conf/ext/fhac_design_2012/Resources/Public/Css/FhOLD.css?1612433004" media="all">
</head>
<body>
<div id="seite">
    <div id="header">
        <div id="topnavi">FAQ zur Veranstaltung</div>
    </div>
    <div id="headnavi">
        <span class="passiv">
            <a href="faq_public_page.php?ref_id=<?php echo htmlspecialchars($_GET['ref_id'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">FAQ</a>
        </span>
        <span class="passiv">
            <a href="faq_ask_page.php?ref_id=<?php echo htmlspecialchars($_GET['ref_id'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">Frage stellen</a>
        </span>
    </div>
    <div id="logo">
        <a href="/" title="zur Startseite">
            <img src="https://services.fh-aachen.de/img/fh-logo-left.svg" width="57" height="194" alt="LOGO der FH Aachen" title="zur Startseite">
        </a>
    </div>
    <div id="inhalt" class="csc-default">
        <p style="font-size: 11px; color: #555; border-left: 3px solid #00a99d; padding-left: 6px;">
            Presented by Team Carologistics &amp; Team Alert with greetings to MASCOR Institute.
        </p>
        <?php include __DIR__ . '/../php_integration/faq_public_snippet.php'; ?>
        <p><a href="faq_ask_page.php?ref_id=<?php echo htmlspecialchars($_GET['ref_id'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">Neue Frage stellen</a></p>
    </div>
    <div style="clear: both;"></div>
</div>
</body>
</html>
