DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS quizzes;
DROP TABLE IF EXISTS student_results;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE quizzes (
    quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_subject TEXT,
    num_questions INTEGER,
    quiz_date TEXT
);

CREATE TABLE student_results (
    student_id INTEGER,
    quiz_id INTEGER,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    PRIMARY KEY (student_id, quiz_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
);
