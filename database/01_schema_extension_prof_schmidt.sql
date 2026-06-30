-- FAQ-Tool: PostgreSQL-Erweiterung fuer die bestehende PHP/PostgreSQL-Webseite.
-- Diese Datei legt nur die beiden FAQ-Tabellen und die benoetigten ENUM-Typen an.
-- Die vorhandene Tabelle courseinstance wird nicht angelegt oder veraendert.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'qa_item_type') THEN
        CREATE TYPE qa_item_type AS ENUM ('category', 'question', 'answer');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'qa_status') THEN
        CREATE TYPE qa_status AS ENUM ('open', 'answered', 'published', 'hidden', 'deleted');
    END IF;
END $$;

-- qaitem enthaelt alle FAQ-Inhalte.
-- type legt fest, ob der Eintrag Kategorie, Frage oder Antwort ist.
CREATE TABLE IF NOT EXISTS qaitem (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    hidden_text TEXT NULL,
    type qa_item_type NOT NULL,
    source_person TEXT NULL,
    source_person_hidden BOOLEAN DEFAULT TRUE,
    status qa_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- itemrelation bildet die Struktur ab:
-- courseinstance -> Kategorie -> Frage -> Antwort.
--
-- parent_course ist bewusst ohne FOREIGN KEY angelegt.
CREATE TABLE IF NOT EXISTS itemrelation (
    id BIGSERIAL PRIMARY KEY,
    parent_course BIGINT NULL,
    parent_qa BIGINT NULL REFERENCES qaitem(id) ON DELETE CASCADE,
    child_qa BIGINT NOT NULL REFERENCES qaitem(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT itemrelation_exactly_one_parent CHECK (
        (parent_course IS NOT NULL AND parent_qa IS NULL)
        OR
        (parent_course IS NULL AND parent_qa IS NOT NULL)
    ),
    CONSTRAINT itemrelation_no_self_link CHECK (parent_qa IS NULL OR parent_qa <> child_qa)
);

CREATE INDEX IF NOT EXISTS idx_qaitem_type_status
    ON qaitem(type, status);

CREATE INDEX IF NOT EXISTS idx_qaitem_text_search
    ON qaitem USING gin (to_tsvector('german', coalesce(title, '') || ' ' || coalesce(text, '')));

CREATE INDEX IF NOT EXISTS idx_itemrelation_parent_course
    ON itemrelation(parent_course, sort_order);

CREATE INDEX IF NOT EXISTS idx_itemrelation_parent_qa
    ON itemrelation(parent_qa, sort_order);

CREATE INDEX IF NOT EXISTS idx_itemrelation_child_qa
    ON itemrelation(child_qa);

CREATE UNIQUE INDEX IF NOT EXISTS uq_itemrelation_course_child
    ON itemrelation(parent_course, child_qa)
    WHERE parent_course IS NOT NULL AND parent_qa IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_itemrelation_qa_child
    ON itemrelation(parent_qa, child_qa)
    WHERE parent_course IS NULL AND parent_qa IS NOT NULL;
