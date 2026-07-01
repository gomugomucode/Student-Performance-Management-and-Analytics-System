-- PostgreSQL schema for Student Performance Management System
-- Production-ready migration script

BEGIN;

CREATE TABLE IF NOT EXISTS students (
    student_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(30),
    semester SMALLINT CHECK (semester BETWEEN 1 AND 12),
    department VARCHAR(100),
    age SMALLINT CHECK (age BETWEEN 1 AND 130),
    grade VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    marks INTEGER NOT NULL CHECK (marks BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_marks_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_marks_student_subject UNIQUE (student_id, subject)
);

CREATE INDEX IF NOT EXISTS idx_students_name ON students (name);
CREATE INDEX IF NOT EXISTS idx_students_department ON students (department);
CREATE INDEX IF NOT EXISTS idx_marks_student_id ON marks (student_id);
CREATE INDEX IF NOT EXISTS idx_marks_subject ON marks (subject);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_marks_updated_at
BEFORE UPDATE ON marks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMIT;
