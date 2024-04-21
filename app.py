from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
app = Flask(__name__)
app.secret_key = "not_so_secret_key"

#home redirects to login page
@app.route("/")
def home():
    return redirect(url_for("login"))

#Use admin and password
@app.route("/login" , methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    conn, cursor = connect_to_db()
    students = read_data(cursor, "students")
    quizzes = read_data(cursor, "quizzes")
    conn.close()
    return render_template("dashboard.html", students=students, quizzes=quizzes)

@app.route("/student/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_id = count_students("students") + 1
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        name_format = re.compile(r"^[a-zA-Z]+$")
        if name_format.match(first_name) and name_format.match(last_name):
            conn, cursor = connect_to_db()
            cursor.execute("INSERT INTO students (student_id, first_name, last_name) VALUES (?, ?, ?)", 
            (student_id, first_name, last_name))
            close_connection(conn)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid first name or last name")
    return render_template("student_form.html")

@app.route("/quiz/add", methods=["GET", "POST"])
def add_quiz():
    if request.method == "POST":
        quiz_id = count_students("quizzes") + 1
        quiz_subject = request.form.get("subject")
        num_question = request.form.get("num_question")
        quiz_date = request.form.get("date")
        sub_format = re.compile(r"^[a-zA-Z0-9 ]+$")
        num_format = re.compile(r"^[0-9]+$")
        date_format = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if sub_format.match(quiz_subject) and num_format.match(num_question) and date_format.match(quiz_date):
            conn, cursor = connect_to_db()
            cursor.execute(
            "INSERT INTO quizzes (quiz_id, quiz_subject, num_questions, quiz_date) VALUES (?, ?, ?, ?)", 
            (quiz_id, quiz_subject, num_question, quiz_date))
            close_connection(conn)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid subject, number of questions, or date")
    return render_template("quiz_form.html")

@app.route("/student/id", methods=["POST"])
def view_student():
    student_id = request.form.get("student_id")
    return redirect(url_for("result_student", id=student_id))

@app.route("/student/<id>", methods=["GET", "POST"])
def result_student(id):
    id = int(id)
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM students WHERE student_id=?", (id,))
    student = cursor.fetchone()
    cursor.execute("SELECT * FROM student_results WHERE student_id=?", (id,))
    student_results = cursor.fetchall()
    conn.close()
    if not student:
        flash("Student not found.")
    elif not student_results:
        flash("No quizzes have been taken by this student")
    return render_template("student.html", student=student, student_results=student_results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        quiz_id = request.form.get("quiz_id")
        grade = request.form.get("grade")
        grade = int(grade)
        if grade in range(0, 101):
            conn, cursor = connect_to_db()
            cursor.execute("SELECT * FROM student_results WHERE student_id=? AND quiz_id=?", (student_id, quiz_id))
            graded = cursor.fetchone()
            if graded is not None:
                flash("This quiz has already been graded for this student.")
                close_connection(conn)
                return redirect(url_for("dashboard"))
            cursor.execute("INSERT INTO student_results (student_id, quiz_id, score) VALUES (?, ?, ?)",
            (student_id, quiz_id, grade))
            close_connection(conn)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid grade")
    return redirect(url_for("dashboard"))

def connect_to_db():
    conn = sqlite3.connect("hw13.db")
    cursor = conn.cursor()
    return conn, cursor

def create_tables(cursor):
    with open("schema.sql", "r") as f:
        sqlite = f.read()
    cursor.executescript(sqlite)

def clear_tables(cursor):
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM quizzes")
    cursor.execute("DELETE FROM student_results")

def insert_basecase(cursor):
    cursor.execute(
    "INSERT INTO students (student_id, first_name, last_name) VALUES (?, ?, ?)", 
    (1, "James", "Smith"))
    cursor.execute(
    "INSERT INTO quizzes (quiz_id, quiz_subject, num_questions, quiz_date) VALUES (?, ?, ?, ?)", 
    (1, "Python Basics", 5, "2015-02-05"))
    cursor.execute(
    "INSERT INTO student_results (student_id, quiz_id, score) VALUES (?, ?, ?)", 
    (1, 1, 85))

def count_students(table):
    conn, cursor = connect_to_db()
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    close_connection(conn)
    return count

def read_data(cursor, table):
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()

def close_connection(conn):
    conn.commit()
    conn.close()

def start_db():
    conn, cursor = connect_to_db()
    create_tables(cursor)
    clear_tables(cursor)
    insert_basecase(cursor)
    close_connection(conn)

if __name__ == "__main__":
    start_db()
    app.run()
