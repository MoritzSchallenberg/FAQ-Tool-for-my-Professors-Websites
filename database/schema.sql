-- FAQ-Tool Datenbankstruktur fuer MySQL/MariaDB
-- Ausfuehren z. B. mit:
-- mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS faq_tool
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE faq_tool;

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    sort_order INT DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    category_id INT NULL,
    question_text TEXT NOT NULL,
    contact_email VARCHAR(255) NULL,
    source_ip_hash CHAR(64) NULL,
    status ENUM('open', 'answered', 'published', 'hidden', 'deleted') DEFAULT 'open',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_questions_status (status),
    INDEX idx_questions_public (is_public),
    INDEX idx_questions_created_at (created_at),
    FULLTEXT INDEX ft_questions_text (question_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL UNIQUE,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_answers_text (answer_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO courses (name, slug)
VALUES ('Elektrotechnik/Elektronik', 'et');

INSERT IGNORE INTO categories (name, sort_order)
VALUES
('Allgemein', 10),
('Vorlesung', 20),
('Übung', 30),
('Praktikum', 40),
('Prüfung', 50),
('Knotenpotentialverfahren', 60),
('Maschenstromverfahren', 70),
('Operationsverstärker', 80),
('Nichtlineare Bauteile', 90),
('Formelsammlung', 100);
