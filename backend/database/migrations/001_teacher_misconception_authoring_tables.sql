-- Teacher-authored misconception tagging feature.
-- Additive migration: creates the new tables only.

CREATE TABLE IF NOT EXISTS question_steps (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    step_number INTEGER NOT NULL,
    step_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS misconceptions (
    id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL REFERENCES concepts(id),
    description TEXT NOT NULL,
    created_by_teacher_id INTEGER REFERENCES teachers(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS question_options (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    option_text TEXT NOT NULL,
    is_correct INTEGER NOT NULL DEFAULT 0 CHECK (is_correct IN (0, 1)),
    misconception_id INTEGER REFERENCES misconceptions(id),
    deviates_at_step INTEGER
);

CREATE INDEX IF NOT EXISTS idx_question_steps_question_id ON question_steps(question_id);
CREATE INDEX IF NOT EXISTS idx_question_options_question_id ON question_options(question_id);
CREATE INDEX IF NOT EXISTS idx_question_options_misconception_id ON question_options(misconception_id);
CREATE INDEX IF NOT EXISTS idx_misconceptions_concept_id ON misconceptions(concept_id);
