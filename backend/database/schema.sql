
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    experience INTEGER NOT NULL DEFAULT 0 CHECK (experience >= 0),
    verification_status TEXT NOT NULL
        CHECK (verification_status IN ('pending', 'verified', 'rejected', 'suspended')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE (subject_id, name)
);

CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    UNIQUE (topic_id, name)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    assessment_type TEXT NOT NULL
        CHECK (assessment_type IN ('diagnostic', 'practice', 'targeted', 'reassessment')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    assessment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    time_taken INTEGER NOT NULL CHECK (time_taken >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS student_progress (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    accuracy REAL NOT NULL CHECK (accuracy >= 0 AND accuracy <= 100),
    attempt_count INTEGER NOT NULL CHECK (attempt_count >= 0),
    status TEXT NOT NULL
        CHECK (status IN ('normal', 'needs_intervention', 'in_progress', 'successful', 'unsuccessful')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    UNIQUE (student_id, concept_id)
);

CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    type TEXT NOT NULL
        CHECK (type IN ('targeted_practice', 'learning_resource', 'teacher_session', 'reassessment')),
    teacher_id INTEGER,
    status TEXT NOT NULL
        CHECK (status IN ('in_progress', 'successful', 'unsuccessful')),
    result TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS learning_resources (
    id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    resource_type TEXT NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES learning_resources(id) ON DELETE CASCADE
);

-- Performance indexes used by the backend.
CREATE INDEX IF NOT EXISTS idx_topics_subject_id ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_concepts_topic_id ON concepts(topic_id);
CREATE INDEX IF NOT EXISTS idx_questions_concept_id ON questions(concept_id);
CREATE INDEX IF NOT EXISTS idx_assessments_student_id ON assessments(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_assessment_id ON attempts(assessment_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student_id ON attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question_id ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_progress_student_id ON student_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_concept_id ON student_progress(concept_id);
CREATE INDEX IF NOT EXISTS idx_interventions_student_id ON interventions(student_id);
CREATE INDEX IF NOT EXISTS idx_interventions_concept_id ON interventions(concept_id);
CREATE INDEX IF NOT EXISTS idx_resources_concept_id ON learning_resources(concept_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_student_id ON recommendations(student_id);

-- Prevent an attempt from associating an assessment with a different student.
CREATE TRIGGER IF NOT EXISTS validate_attempt_student
BEFORE INSERT ON attempts
FOR EACH ROW
WHEN (SELECT student_id FROM assessments WHERE id = NEW.assessment_id) != NEW.student_id
BEGIN
    SELECT RAISE(ABORT, 'attempt student_id does not match assessment student_id');
END;
