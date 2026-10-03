from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import timedelta
import sqlite3
import os
import time
import json
import re

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from pypdf import PdfReader
from docx import Document

from google import genai
from google.genai import types


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "hiresmart_secret_key"
)

# Persistent login
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.getenv("VERCEL"))


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

if os.getenv("VERCEL"):
    DATABASE = "/tmp/hiresmart.db"
else:
    DATABASE = "hiresmart.db"


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

if os.getenv("VERCEL"):
    UPLOAD_FOLDER = "/tmp/uploads"
else:
    UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

gemini_client = None

if (
    GEMINI_API_KEY
    and GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE"
):

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=15000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                )
            )
        )

        print("================================")
        print("Gemini client initialized successfully.")
        print("Model:", GEMINI_MODEL)
        print("================================")

    except Exception as error:

        gemini_client = None

        print("================================")
        print("GEMINI INITIALIZATION ERROR")
        print("TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("================================")

else:

    print("================================")
    print("WARNING: GEMINI API KEY NOT CONFIGURED")
    print("================================")


# =========================================================
# SKILLS LIST
# =========================================================

SKILLS_LIST = [

    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "HTML",
    "CSS",
    "SQL",

    "Flask",
    "Django",
    "React",
    "Node.js",

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "AI",

    "Data Science",
    "Data Analysis",

    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",

    "Git",
    "GitHub",

    "MySQL",
    "SQLite",
    "MongoDB",

    "REST API",
    "API",

    "AWS",
    "Azure",

    "Power BI",
    "Excel",

    "Communication",
    "Leadership"
]


# =========================================================
# GEMINI HELPERS
# =========================================================

def fallback_answer_score(answer):

    """Fast local fallback score from 0 to 5."""

    word_count = len(
        answer.split()
    )

    if not answer.strip():

        return 0

    if word_count >= 60:

        return 5

    if word_count >= 35:

        return 4

    if word_count >= 15:

        return 3

    if word_count >= 5:

        return 2

    return 1


def gemini_text(prompt):

    """
    Generate text using Gemini Generate Content API.
    """

    if gemini_client is None:

        raise RuntimeError(
            "Gemini client is not initialized. "
            "Check GEMINI_API_KEY."
        )

    response = gemini_client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.2,

            max_output_tokens=120,

            thinking_config=types.ThinkingConfig(

                thinking_level="minimal"

            )
        )
    )

    text = (
        getattr(
            response,
            "text",
            ""
        )
        or ""
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text


def ask_gemini(prompt):

    try:

        return gemini_text(
            prompt
        )

    except Exception as error:

        print(
            "GEMINI ERROR:",
            type(error).__name__,
            str(error)
        )

        return ""


# =========================================================
# FIRST AI INTERVIEW QUESTION
# =========================================================

def generate_first_interview_question(

    resume_text,

    interview_type,

    total_questions

):

    prompt = f"""
You are conducting a professional
{interview_type} job interview.

The candidate has selected
{total_questions} questions.

Candidate resume:

{resume_text[:12000]}

Generate ONLY the first interview question.

Rules:

- The question MUST use a specific detail
  from the resume.

- HR interviews must ask about a specific
  project, experience, achievement,
  responsibility, education, or career item.

- Technical interviews must ask about a
  specific technology, project,
  implementation, database, algorithm,
  architecture, or technical decision
  from the resume.

- Ask exactly ONE question.

- Do not number it.

- Do not give an answer.

- Do not add any explanation.
"""

    question = gemini_text(
        prompt
    )

    question = (
        question
        .splitlines()[0]
        .strip()
    )

    return question, None


# =========================================================
# FOLLOW-UP QUESTION + ANSWER SCORE
# =========================================================

def evaluate_answer_and_generate_followup(

    resume_text,

    previous_questions,

    current_question,

    answer,

    interview_type,

    next_question_number,

    total_questions

):

    prompt = f"""
You are conducting a live
{interview_type} job interview.

Candidate resume:

{resume_text[:12000]}

Previous interview questions:

{chr(10).join(previous_questions[-5:])}

Current question:

{current_question}

Candidate's answer:

{answer}

The next question is question
{next_question_number} of
{total_questions}.

Do BOTH tasks:

SCORE:
<integer from 0 to 5>

NEXT_QUESTION:
<one question>

Rules:

- Score the answer for relevance,
  clarity, accuracy, and depth.

- The next question MUST be based
  on the candidate's answer.

- It must also remain relevant
  to the resume and selected
  interview type.

- Do not repeat previous questions.

- Ask exactly one next question.

- Do not provide an answer.

- Do not add explanations.

- Return ONLY the two lines above.
"""

    text = gemini_text(
        prompt
    )

    score = fallback_answer_score(
        answer
    )

    question = (
        "Can you explain that experience "
        "in more detail?"
    )

    for line in text.splitlines():

        clean = line.strip()

        upper = clean.upper()

        if upper.startswith(
            "SCORE:"
        ):

            try:

                score = int(
                    float(
                        clean.split(
                            ":",
                            1
                        )[1]
                        .strip()
                        .split()[0]
                    )
                )

                score = max(
                    0,
                    min(
                        5,
                        score
                    )
                )

            except Exception:

                pass

        elif upper.startswith(
            "NEXT_QUESTION:"
        ):

            value = (
                clean
                .split(
                    ":",
                    1
                )[1]
                .strip()
            )

            if value:

                question = value

    return (
        score,
        question,
        None
    )


def check_interview_answer(
    question,
    answer
):

    """
    Fast local fallback kept for compatibility.
    """

    return fallback_answer_score(
        answer
    )


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


def add_column_if_missing(
    conn,
    table,
    column,
    definition
):

    columns = {

        row["name"]

        for row in conn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

    }

    if column not in columns:

        conn.execute(

            f"""
            ALTER TABLE {table}
            ADD COLUMN {column} {definition}
            """

        )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_table():

    conn = get_db()


    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL,

            phone TEXT,

            education TEXT,

            skills TEXT,

            experience TEXT,

            resume_score INTEGER,

            resume_skills TEXT,

            resume_analysis TEXT,

            resume_suggestions TEXT

        )
        """

    )


    for column, definition in [

        ("phone", "TEXT"),

        ("education", "TEXT"),

        ("skills", "TEXT"),

        ("experience", "TEXT"),

        ("resume_score", "INTEGER"),

        ("resume_skills", "TEXT"),

        ("resume_analysis", "TEXT"),

        ("resume_suggestions", "TEXT"),

    ]:

        add_column_if_missing(

            conn,

            "users",

            column,

            definition

        )


    # -----------------------------------------------------
    # JOBS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            recruiter_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            company TEXT NOT NULL,

            location TEXT NOT NULL,

            skills TEXT NOT NULL,

            description TEXT,

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    # -----------------------------------------------------
    # APPLICATIONS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            candidate_id INTEGER NOT NULL,

            status TEXT DEFAULT 'Applied',

            applied_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            application_id INTEGER,

            message TEXT NOT NULL,

            is_read INTEGER DEFAULT 0,

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    # -----------------------------------------------------
    # RECRUITER REQUESTS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS recruiter_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            recruiter_id INTEGER NOT NULL,

            candidate_id INTEGER NOT NULL,

            job_id INTEGER,

            request_type TEXT NOT NULL,

            message TEXT,

            status TEXT DEFAULT 'Pending',

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    # -----------------------------------------------------
    # INTERVIEW RESULTS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS interview_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            score INTEGER,

            feedback TEXT,

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    for column, definition in [

        ("total", "INTEGER"),

        ("percentage", "INTEGER"),

        ("message", "TEXT"),

        ("questions", "TEXT"),

        ("answers", "TEXT"),

        ("scores", "TEXT"),

    ]:

        add_column_if_missing(

            conn,

            "interview_results",

            column,

            definition

        )


    # -----------------------------------------------------
    # ACTIVE INTERVIEWS
    # -----------------------------------------------------

    conn.execute(

        """
        CREATE TABLE IF NOT EXISTS active_interviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            duration INTEGER NOT NULL,

            total_questions INTEGER NOT NULL,

            interview_type TEXT NOT NULL,

            start_time REAL NOT NULL,

            current_index INTEGER DEFAULT 0,

            current_question TEXT,

            questions TEXT,

            answers TEXT,

            scores TEXT,

            interaction_id TEXT,

            status TEXT DEFAULT 'active',

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """

    )


    add_column_if_missing(

        conn,

        "active_interviews",

        "resume_text",

        "TEXT"

    )


    conn.execute(

        """
        CREATE INDEX IF NOT EXISTS
        idx_active_interviews_candidate

        ON active_interviews(
            candidate_id,
            status
        )
        """

    )


    conn.commit()

    conn.close()


# =========================================================
# FILE / RESUME HELPERS
# =========================================================

def allowed_file(filename):

    return (

        "."

        in filename

        and

        filename.rsplit(
            ".",
            1
        )[1].lower()

        in ALLOWED_EXTENSIONS

    )


def extract_resume_text(filepath):

    extension = filepath.rsplit(
        ".",
        1
    )[1].lower()

    parts = []


    try:

        if extension == "pdf":

            reader = PdfReader(
                filepath
            )

            for page in reader.pages:

                page_text = (
                    page.extract_text()
                )

                if page_text:

                    parts.append(
                        page_text
                    )


        elif extension == "docx":

            document = Document(
                filepath
            )

            for paragraph in document.paragraphs:

                if paragraph.text:

                    parts.append(
                        paragraph.text
                    )


    except Exception as error:

        print(
            "RESUME TEXT EXTRACTION ERROR:",
            repr(error)
        )


    return "\n".join(
        parts
    ).strip()


def get_latest_resume_for_user(
    user_id
):

    prefix = f"{user_id}_"

    folder = app.config[
        "UPLOAD_FOLDER"
    ]


    if not os.path.isdir(folder):

        return None, None


    files = [

        filename

        for filename
        in os.listdir(folder)

        if (
            filename.startswith(prefix)
            and
            allowed_file(filename)
        )

    ]


    if not files:

        return None, None


    files.sort(

        key=lambda filename:

        os.path.getmtime(

            os.path.join(

                folder,

                filename

            )

        ),

        reverse=True

    )


    filename = files[0]

    filepath = os.path.join(

        folder,

        filename

    )


    return (

        filename,

        filepath

    )


def get_latest_resume():

    return get_latest_resume_for_user(

        session["user_id"]

    )


def save_resume_analysis(

    user_id,

    filename,

    score,

    skills,

    missing_skills,

    suggestions,

    analysis=None

):

    if analysis is None:

        analysis = (

            f"Detected "
            f"{len(skills)} "
            f"relevant skills "
            f"in {filename}."

        )


    conn = get_db()


    conn.execute(

        """
        UPDATE users

        SET

            resume_score = ?,

            resume_skills = ?,

            resume_analysis = ?,

            resume_suggestions = ?

        WHERE id = ?
        """,

        (

            score,

            ", ".join(
                skills
            ),

            analysis,

            "\n".join(
                suggestions
            ),

            user_id

        )

    )


    conn.commit()

    conn.close()


def get_resume_analysis(
    user_id
):

    conn = get_db()


    row = conn.execute(

        """
        SELECT

            resume_score,

            resume_skills,

            resume_analysis,

            resume_suggestions

        FROM users

        WHERE id = ?
        """,

        (
            user_id,
        )

    ).fetchone()


    conn.close()


    return row


# =========================================================
# AUTH HELPERS
# =========================================================

def candidate_required():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if (
        session
        .get(
            "user_role",
            ""
        )
        .lower()
        != "candidate"
    ):

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )


    return None


def recruiter_required():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if (
        session
        .get(
            "user_role",
            ""
        )
        .lower()
        != "recruiter"
    ):

        return redirect(
            url_for("dashboard")
        )


    return None


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:

        if (
            session
            .get(
                "user_role",
                ""
            )
            .lower()
            == "recruiter"
        ):

            return redirect(
                url_for(
                    "recruiter_dashboard"
                )
            )


        return redirect(
            url_for("dashboard")
        )


    return redirect(
        url_for("register")
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if "user_id" in session:

        if (
            session
            .get(
                "user_role",
                ""
            )
            .lower()
            == "recruiter"
        ):

            return redirect(
                url_for(
                    "recruiter_dashboard"
                )
            )


        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        ).strip()


        role = request.form.get(
            "role",
            "Candidate"
        ).strip()


        if (
            not name
            or not email
            or not password
        ):

            return """
            <h2>Please fill all fields.</h2>
            <a href="/register">
                Go Back
            </a>
            """


        if role.lower() not in {
            "candidate",
            "recruiter"
        }:

            role = "Candidate"


        conn = get_db()


        try:

            conn.execute(

                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )

                VALUES (?, ?, ?, ?)
                """,

                (

                    name,

                    email,

                    generate_password_hash(
                        password
                    ),

                    role

                )

            )


            conn.commit()


        except sqlite3.IntegrityError:

            conn.close()


            return """
            <h2>Email already registered.</h2>
            <a href="/register">
                Try Again
            </a>
            """


        conn.close()


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if "user_id" in session:

        if (
            session
            .get(
                "user_role",
                ""
            )
            .lower()
            == "recruiter"
        ):

            return redirect(
                url_for(
                    "recruiter_dashboard"
                )
            )


        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        ).strip()


        if (
            not email
            or not password
        ):

            return """
            <h2>
                Please enter email and password.
            </h2>

            <a href="/login">
                Go Back
            </a>
            """


        conn = get_db()


        user = conn.execute(

            """
            SELECT *
            FROM users
            WHERE email = ?
            """,

            (
                email,
            )

        ).fetchone()


        conn.close()


        if (
            user
            and
            check_password_hash(
                user["password"],
                password
            )
        ):

            session.permanent = True

            session[
                "user_id"
            ] = user["id"]

            session[
                "user_name"
            ] = user["name"]

            session[
                "user_email"
            ] = user["email"]

            session[
                "user_role"
            ] = user["role"]


            if (
                user["role"]
                .lower()
                == "recruiter"
            ):

                return redirect(
                    url_for(
                        "recruiter_dashboard"
                    )
                )


            return redirect(
                url_for(
                    "dashboard"
                )
            )


        return """
        <h2>Invalid email or password.</h2>

        <a href="/login">
            Try Again
        </a>
        """


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()


    return redirect(
        url_for("login")
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()


        new_password = request.form.get(
            "new_password",
            ""
        ).strip()


        confirm_password = request.form.get(
            "confirm_password",
            ""
        ).strip()


        if (
            not email
            or not new_password
            or not confirm_password
        ):

            return """
            <h2>Please fill all fields.</h2>

            <a href="/forgot-password">
                Go Back
            </a>
            """


        if new_password != confirm_password:

            return """
            <h2>Passwords do not match.</h2>

            <a href="/forgot-password">
                Try Again
            </a>
            """


        conn = get_db()


        user = conn.execute(

            """
            SELECT id
            FROM users
            WHERE email = ?
            """,

            (
                email,
            )

        ).fetchone()


        if not user:

            conn.close()


            return """
            <h2>Email not registered.</h2>

            <a href="/forgot-password">
                Try Again
            </a>
            """


        conn.execute(

            """
            UPDATE users

            SET password = ?

            WHERE email = ?
            """,

            (
                generate_password_hash(
                    new_password
                ),

                email

            )

        )


        conn.commit()

        conn.close()


        return """
        <h2>
            Password Reset Successful! ✅
        </h2>

        <a href="/login">
            Go to Login
        </a>
        """


    return render_template(
        "forgot_password.html"
    )


# =========================================================
# CANDIDATE DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if (
        session
        .get(
            "user_role",
            ""
        )
        .lower()
        == "recruiter"
    ):

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )


    conn = get_db()


    notification_count = conn.execute(

        """
        SELECT COUNT(*)

        FROM notifications

        WHERE candidate_id = ?

        AND is_read = 0
        """,

        (
            session["user_id"],
        )

    ).fetchone()[0]


    request_count = conn.execute(

        """
        SELECT COUNT(*)

        FROM recruiter_requests

        WHERE candidate_id = ?

        AND status = 'Pending'
        """,

        (
            session["user_id"],
        )

    ).fetchone()[0]


    conn.close()


    return render_template(

        "candidate_dashboard.html",

        name=session.get(
            "user_name",
            "Candidate"
        ),

        email=session.get(
            "user_email",
            ""
        ),

        role=session.get(
            "user_role",
            "Candidate"
        ),

        notification_count=
        notification_count,

        request_count=
        request_count

    )


# =========================================================
# RECRUITER DASHBOARD
# =========================================================

@app.route(
    "/recruiter/dashboard"
)
def recruiter_dashboard():

    check = recruiter_required()

    if check:

        return check


    conn = get_db()


    recruiter_jobs = conn.execute(

        """
        SELECT *

        FROM jobs

        WHERE recruiter_id = ?

        ORDER BY created_at DESC
        """,

        (
            session["user_id"],
        )

    ).fetchall()


    total_applications = conn.execute(

        """
        SELECT COUNT(a.id)

        FROM applications a

        JOIN jobs j
        ON a.job_id = j.id

        WHERE j.recruiter_id = ?
        """,

        (
            session["user_id"],
        )

    ).fetchone()[0]


    conn.close()


    return render_template(

        "recruiter_dashboard.html",

        name=session.get(
            "user_name",
            "Recruiter"
        ),

        email=session.get(
            "user_email",
            ""
        ),

        jobs=recruiter_jobs,

        total_applications=
        total_applications

    )


# =========================================================
# RECRUITER - POST JOB
# =========================================================

@app.route(
    "/recruiter/post_job",
    methods=["GET", "POST"]
)
def post_job():

    check = recruiter_required()

    if check:

        return check


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()


        company = request.form.get(
            "company",
            ""
        ).strip()


        location = request.form.get(
            "location",
            ""
        ).strip()


        skills = request.form.get(
            "skills",
            ""
        ).strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        if (
            not title
            or not company
            or not location
            or not skills
        ):

            return """
            <h2>
                Please fill all required fields.
            </h2>

            <a href="/recruiter/post_job">
                Go Back
            </a>
            """


        conn = get_db()


        conn.execute(

            """
            INSERT INTO jobs
            (
                recruiter_id,
                title,
                company,
                location,
                skills,
                description
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (

                session["user_id"],

                title,

                company,

                location,

                skills,

                description

            )

        )


        conn.commit()

        conn.close()


        return redirect(
            url_for(
                "recruiter_jobs"
            )
        )


    return render_template(
        "post_job.html"
    )


# =========================================================
# RECRUITER - MY JOBS
# =========================================================

@app.route(
    "/recruiter/jobs"
)
def recruiter_jobs():

    check = recruiter_required()

    if check:

        return check


    conn = get_db()


    jobs_list = conn.execute(

        """
        SELECT

            j.*,

            COUNT(a.id)
            AS application_count

        FROM jobs j

        LEFT JOIN applications a
        ON j.id = a.job_id

        WHERE j.recruiter_id = ?

        GROUP BY j.id

        ORDER BY j.created_at DESC

        """,

        (
            session["user_id"],
        )

    ).fetchall()


    conn.close()


    return render_template(

        "recruiter_jobs.html",

        jobs=jobs_list

    )


# =========================================================
# RECRUITER - CANDIDATES
# =========================================================

@app.route(
    "/recruiter/candidates"
)
def recruiter_candidates():

    check = recruiter_required()

    if check:

        return check


    recruiter_id = session[
        "user_id"
    ]


    conn = get_db()


    candidates = conn.execute(

        """
        SELECT

            u.id AS candidate_id,

            u.name,

            u.email,

            u.phone,

            u.education,

            u.skills,

            u.experience,

            u.resume_score,

            u.resume_skills,

            u.resume_analysis,

            u.resume_suggestions,

            (
                SELECT a.id

                FROM applications a

                JOIN jobs j
                ON a.job_id = j.id

                WHERE a.candidate_id = u.id

                AND j.recruiter_id = ?

                ORDER BY a.applied_at DESC

                LIMIT 1

            ) AS application_id,

            (
                SELECT a.status

                FROM applications a

                JOIN jobs j
                ON a.job_id = j.id

                WHERE a.candidate_id = u.id

                AND j.recruiter_id = ?

                ORDER BY a.applied_at DESC

                LIMIT 1

            ) AS application_status,

            (
                SELECT rr.status

                FROM recruiter_requests rr

                WHERE rr.candidate_id = u.id

                AND rr.recruiter_id = ?

                ORDER BY rr.created_at DESC

                LIMIT 1

            ) AS latest_request_status

        FROM users u

        WHERE LOWER(u.role)
            = 'candidate'

        ORDER BY u.name ASC

        """,

        (
            recruiter_id,
            recruiter_id,
            recruiter_id
        )

    ).fetchall()


    conn.close()


    return render_template(

        "recruiter_candidates.html",

        candidates=candidates

    )


# =========================================================
# RECRUITER - CANDIDATE PROFILE
# =========================================================

@app.route(
    "/recruiter/candidate/<int:candidate_id>"
)
def recruiter_candidate_profile(
    candidate_id
):

    check = recruiter_required()

    if check:

        return check


    conn = get_db()


    candidate = conn.execute(

        """
        SELECT *

        FROM users

        WHERE id = ?

        AND LOWER(role)
            = 'candidate'

        """,

        (
            candidate_id,
        )

    ).fetchone()


    if not candidate:

        conn.close()


        return """
        <h2>Candidate not found.</h2>

        <a href="/recruiter/candidates">
            Back to Candidates
        </a>
        """


    applications = conn.execute(

        """
        SELECT

            a.id,

            a.status,

            a.applied_at,

            j.id AS job_id,

            j.title,

            j.company,

            j.location,

            j.skills,

            j.description

        FROM applications a

        JOIN jobs j
        ON a.job_id = j.id

        WHERE a.candidate_id = ?

        AND j.recruiter_id = ?

        ORDER BY a.applied_at DESC

        """,

        (
            candidate_id,
            session["user_id"]
        )

    ).fetchall()


    interview_results = conn.execute(

        """
        SELECT *

        FROM interview_results

        WHERE candidate_id = ?

        ORDER BY created_at DESC

        """,

        (
            candidate_id,
        )

    ).fetchall()


    jobs_list = conn.execute(

        """
        SELECT *

        FROM jobs

        WHERE recruiter_id = ?

        ORDER BY created_at DESC

        """,

        (
            session["user_id"],
        )

    ).fetchall()


    requests_list = conn.execute(

        """
        SELECT

            rr.*,

            j.title AS job_title

        FROM recruiter_requests rr

        LEFT JOIN jobs j
        ON rr.job_id = j.id

        WHERE rr.recruiter_id = ?

        AND rr.candidate_id = ?

        ORDER BY rr.created_at DESC

        """,

        (
            session["user_id"],
            candidate_id
        )

    ).fetchall()


    conn.close()


    analysis = get_resume_analysis(
        candidate_id
    )


    interview = (

        interview_results[0]

        if interview_results

        else None

    )


    return render_template(

        "recruiter_candidate_profile.html",

        candidate=candidate,

        applications=applications,

        interview_results=
        interview_results,

        jobs=jobs_list,

        requests=requests_list,

        analysis=analysis,

        resume_analysis=analysis,

        interview=interview

    )


# =========================================================
# RECRUITER - VIEW CANDIDATE RESUME
# =========================================================

@app.route(
    "/recruiter/candidate/<int:candidate_id>/resume"
)
def recruiter_candidate_resume(
    candidate_id
):

    check = recruiter_required()

    if check:

        return check


    filename, filepath = (
        get_latest_resume_for_user(
            candidate_id
        )
    )


    if (
        not filepath
        or
        not os.path.exists(filepath)
    ):

        return """
        <h2>Resume not found.</h2>

        <a href="/recruiter/candidates">
            Back to Candidates
        </a>
        """


    return send_file(

        filepath,

        as_attachment=False,

        download_name=filename

    )


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()


    if request.method == "POST":

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        education = request.form.get(
            "education",
            ""
        ).strip()


        skills = request.form.get(
            "skills",
            ""
        ).strip()


        experience = request.form.get(
            "experience",
            ""
        ).strip()


        conn.execute(

            """
            UPDATE users

            SET

                phone = ?,

                education = ?,

                skills = ?,

                experience = ?

            WHERE id = ?

            """,

            (

                phone,

                education,

                skills,

                experience,

                session["user_id"]

            )

        )


        conn.commit()


    user = conn.execute(

        """
        SELECT *

        FROM users

        WHERE id = ?

        """,

        (
            session["user_id"],
        )

    ).fetchone()


    conn.close()


    return render_template(

        "profile.html",

        user=user

    )


# =========================================================
# UPLOAD RESUME
# =========================================================

@app.route(
    "/upload_resume",
    methods=["GET", "POST"]
)
def upload_resume():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "GET":

        filename, filepath = (
            get_latest_resume()
        )


        return render_template(

            "upload_resume.html",

            filename=filename,

            resume_uploaded=
            bool(filepath),

            error=None

        )


    if "resume" not in request.files:

        return """
        <h2>No resume selected.</h2>

        <a href="/upload_resume">
            Try Again
        </a>
        """


    file = request.files[
        "resume"
    ]


    if not file.filename:

        return """
        <h2>Please select a resume.</h2>

        <a href="/upload_resume">
            Try Again
        </a>
        """


    if not allowed_file(
        file.filename
    ):

        return """
        <h2>
            Only PDF and DOCX files are allowed.
        </h2>

        <a href="/upload_resume">
            Try Again
        </a>
        """


    filename = secure_filename(
        file.filename
    )


    filename = (
        f"{session['user_id']}_"
        f"{filename}"
    )


    filepath = os.path.join(

        app.config[
            "UPLOAD_FOLDER"
        ],

        filename

    )


    try:

        file.save(
            filepath
        )

    except Exception as error:

        print(
            "RESUME SAVE ERROR:",
            repr(error)
        )


        return """
        <h2>
            Could not save the resume.
        </h2>

        <a href="/upload_resume">
            Try Again
        </a>
        """


    # IMPORTANT:
    #
    # Do not call Gemini while uploading.
    #
    # Gemini can take time.
    #
    # Resume analysis is done locally first.
    #
    try:

        resume_text = extract_resume_text(
            filepath
        )

    except Exception as error:

        print(
            "RESUME EXTRACTION ERROR:",
            repr(error)
        )

        resume_text = ""


    if not resume_text.strip():

        return """
        <h2>
            Resume uploaded, but its text could not be read.
        </h2>

        <p>
            Please upload a text-based PDF or DOCX file.
        </p>

        <a href="/upload_resume">
            Try Again
        </a>
        """


    # Fast local analysis

    text_lower = resume_text.lower()


    found_skills = list(
        dict.fromkeys(

            [

                skill

                for skill in SKILLS_LIST

                if skill.lower()
                in text_lower

            ]

        )
    )


    resume_score = min(

        100,

        30
        +
        len(found_skills)
        * 7

    )


    suggestions = []


    if len(found_skills) < 5:

        suggestions.append(

            "Add more relevant technical skills."

        )


    if "education" not in text_lower:

        suggestions.append(

            "Add your education details."

        )


    if "experience" not in text_lower:

        suggestions.append(

            "Add your work experience or internship details."

        )


    if "project" not in text_lower:

        suggestions.append(

            "Add academic or personal projects."

        )


    if not suggestions:

        suggestions.append(

            "Your resume contains good basic information. "
            "Keep it updated."

        )


    analysis = (

        "Resume uploaded successfully. "

        f"Detected {len(found_skills)} relevant skills."

    )


    conn = get_db()


    conn.execute(

        """
        UPDATE users

        SET

            resume_score = ?,

            resume_skills = ?,

            resume_analysis = ?,

            resume_suggestions = ?

        WHERE id = ?

        """,

        (

            resume_score,

            ", ".join(
                found_skills
            ),

            analysis,

            "\n".join(
                suggestions
            ),

            session["user_id"]

        )

    )


    conn.commit()

    conn.close()


    return render_template(

        "resume_uploaded.html",

        filename=filename

    )


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route(
    "/resume_analysis"
)
def resume_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    filename, filepath = (
        get_latest_resume()
    )


    if not filename or not filepath:

        return render_template(

            "resume_analysis.html",

            filename="No Resume",

            skills=[],

            missing_skills=[],

            score=0,

            suggestions=[
                "Please upload your resume first."
            ],

            resume_text="",

            resume_information={}

        )


    try:

        resume_text = extract_resume_text(
            filepath
        )


        if not resume_text.strip():

            return render_template(

                "resume_analysis.html",

                filename=filename,

                skills=[],

                missing_skills=[],

                score=0,

                suggestions=[

                    "Could not extract text from this resume.",

                    "Please upload a text-based PDF or DOCX file."

                ],

                resume_text="",

                resume_information={}

            )


        text_lower = (
            resume_text.lower()
        )


        found_skills = [

            skill

            for skill in SKILLS_LIST

            if skill.lower()
            in text_lower

        ]


        found_skills = list(
            dict.fromkeys(
                found_skills
            )
        )


        missing_skills = [

            skill

            for skill in SKILLS_LIST

            if skill not in found_skills

        ]


        score = min(

            100,

            30
            +
            len(found_skills)
            * 7

        )


        lines = [

            line.strip()

            for line
            in resume_text.splitlines()

            if line.strip()

        ]


        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        email_match = re.search(

            r"[\w.\-+]+@[\w.\-]+\.\w+",

            resume_text

        )


        email = (

            email_match.group(0)

            if email_match

            else "Not detected"

        )


        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        phone_match = re.search(

            r"(\+91[\s-]?)?[6-9]\d{9}",

            resume_text

        )


        phone = (

            phone_match.group(0)

            if phone_match

            else "Not detected"

        )


        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        detected_name = (
            "Not detected"
        )


        if lines:

            first_line = lines[0]


            if (

                len(first_line)
                <= 60

                and "@"
                not in first_line

                and not any(

                    ch.isdigit()

                    for ch
                    in first_line

                )

            ):

                detected_name = first_line


        # -------------------------------------------------
        # EDUCATION
        # -------------------------------------------------

        education_keywords = [

            "bachelor",

            "b.tech",

            "b.e",

            "bca",

            "b.sc",

            "mca",

            "m.tech",

            "m.sc",

            "master",

            "degree",

            "engineering",

            "computer science",

            "information technology",

            "university",

            "college",

            "education"

        ]


        education_lines = [

            line

            for line
            in lines

            if any(

                keyword
                in line.lower()

                for keyword
                in education_keywords

            )

        ]


        education = (

            " | ".join(

                education_lines[:5]

            )

            if education_lines

            else "Not detected"

        )


        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        experience_keywords = [

            "experience",

            "intern",

            "internship",

            "developer",

            "software engineer",

            "worked at",

            "employment"

        ]


        experience_lines = [

            line

            for line
            in lines

            if any(

                keyword
                in line.lower()

                for keyword
                in experience_keywords

            )

        ]


        experience = (

            " | ".join(

                experience_lines[:5]

            )

            if experience_lines

            else "Not detected"

        )


        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        project_lines = [

            line

            for line
            in lines

            if (

                "project"
                in line.lower()

                or

                "developed"
                in line.lower()

                or

                "built"
                in line.lower()

            )

        ]


        projects = (

            " | ".join(

                project_lines[:5]

            )

            if project_lines

            else "Not detected"

        )


        # -------------------------------------------------
        # RESUME INFORMATION
        # -------------------------------------------------

        resume_information = {

            "name":
            detected_name,

            "email":
            email,

            "phone":
            phone,

            "education":
            education,

            "experience":
            experience,

            "projects":
            projects,

            "skills_count":
            len(found_skills),

            "resume_filename":
            filename

        }


        # -------------------------------------------------
        # SUGGESTIONS
        # -------------------------------------------------

        suggestions = []


        if len(found_skills) < 5:

            suggestions.append(

                "Add more relevant technical skills."

            )


        if email == "Not detected":

            suggestions.append(

                "Add a professional email address."

            )


        if phone == "Not detected":

            suggestions.append(

                "Add your contact number."

            )


        if education == "Not detected":

            suggestions.append(

                "Add your education details."

            )


        if experience == "Not detected":

            suggestions.append(

                "Add your internship or work experience."

            )


        if projects == "Not detected":

            suggestions.append(

                "Add your academic or personal projects."

            )


        if not suggestions:

            suggestions.append(

                "Your resume contains good basic information. "
                "Keep it updated."

            )


        analysis_text = (

            f"Detected "
            f"{len(found_skills)} "
            f"relevant skills "
            f"in {filename}."

        )


        save_resume_analysis(

            session["user_id"],

            filename,

            score,

            found_skills,

            missing_skills,

            suggestions,

            analysis=
            analysis_text

        )


        analysis = get_resume_analysis(

            session["user_id"]

        )


        return render_template(

            "resume_analysis.html",

            filename=filename,

            skills=found_skills,

            missing_skills=
            missing_skills,

            score=score,

            suggestions=suggestions,

            resume_text=
            resume_text,

            resume_information=
            resume_information,

            analysis=analysis

        )


    except Exception as error:

        print(
            "Resume analysis error:",
            repr(error)
        )


        return render_template(

            "resume_analysis.html",

            filename=filename,

            skills=[],

            missing_skills=[],

            score=0,

            suggestions=[
                "Unable to analyze resume."
            ],

            resume_text="",

            resume_information={}

        )


# =========================================================
# SKILL ANALYSIS
# =========================================================

@app.route(
    "/skill_analysis"
)
def skill_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    filename, filepath = (
        get_latest_resume()
    )


    if not filepath:

        return render_template(

            "skill_analysis.html",

            error=
            "Please upload your resume first."

        )


    try:

        resume_text = (
            extract_resume_text(
                filepath
            )
        )


        text_lower = (
            resume_text.lower()
        )


        found_skills = [

            skill

            for skill
            in SKILLS_LIST

            if skill.lower()
            in text_lower

        ]


        missing_skills = [

            skill

            for skill
            in SKILLS_LIST

            if skill not in found_skills

        ]


        return render_template(

            "skill_analysis.html",

            skills=found_skills,

            missing_skills=
            missing_skills,

            filename=filename

        )


    except Exception as error:

        print(
            "Skill analysis error:",
            repr(error)
        )


        return render_template(

            "skill_analysis.html",

            error=
            "Unable to analyze skills."

        )


# =========================================================
# JOBS
# =========================================================

@app.route("/jobs")
def jobs():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()


    jobs_list = conn.execute(

        """
        SELECT

            j.*,

            u.name AS recruiter_name

        FROM jobs j

        JOIN users u

        ON j.recruiter_id = u.id

        ORDER BY j.created_at DESC

        """

    ).fetchall()


    conn.close()


    return render_template(

        "jobs.html",

        jobs=jobs_list

    )


# =========================================================
# APPLY FOR JOB
# =========================================================

@app.route(
    "/apply/<int:job_id>",
    methods=["POST"]
)
def apply_job(job_id):

    check = candidate_required()

    if check:

        return check


    conn = get_db()


    job = conn.execute(

        """
        SELECT *

        FROM jobs

        WHERE id = ?

        """,

        (
            job_id,
        )

    ).fetchone()


    if not job:

        conn.close()


        return redirect(
            url_for("jobs")
        )


    existing = conn.execute(

        """
        SELECT id

        FROM applications

        WHERE job_id = ?

        AND candidate_id = ?

        """,

        (
            job_id,

            session["user_id"]
        )

    ).fetchone()


    if existing:

        conn.close()


        return redirect(
            url_for(
                "my_applications"
            )
        )


    cursor = conn.execute(

        """
        INSERT INTO applications

        (
            job_id,

            candidate_id,

            status

        )

        VALUES (?, ?, 'Applied')

        """,

        (

            job_id,

            session["user_id"]

        )

    )


    application_id = cursor.lastrowid


    conn.execute(

        """
        INSERT INTO notifications

        (
            candidate_id,

            application_id,

            message,

            is_read

        )

        VALUES (?, ?, ?, 0)

        """,

        (

            session["user_id"],

            application_id,

            (
                "Your application for "
                f"{job['title']} "
                "has been submitted."
            )

        )

    )


    conn.commit()

    conn.close()


    return redirect(

        url_for(
            "my_applications"
        )

    )


# =========================================================
# MY APPLICATIONS
# =========================================================

@app.route(
    "/my_applications"
)
def my_applications():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()


    applications = conn.execute(

        """
        SELECT

            a.id,

            a.status,

            a.applied_at,

            j.title,

            j.company,

            j.location,

            j.skills,

            j.description

        FROM applications a

        JOIN jobs j

        ON a.job_id = j.id

        WHERE a.candidate_id = ?

        ORDER BY a.applied_at DESC

        """,

        (
            session["user_id"],
        )

    ).fetchall()


    conn.close()


    return render_template(

        "my_applications.html",

        applications=applications

    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route(
    "/notifications"
)
def notifications():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    conn = get_db()


    notification_list = conn.execute(

        """
        SELECT *

        FROM notifications

        WHERE candidate_id = ?

        ORDER BY created_at DESC

        """,

        (
            session["user_id"],
        )

    ).fetchall()


    conn.execute(

        """
        UPDATE notifications

        SET is_read = 1

        WHERE candidate_id = ?

        """,

        (
            session["user_id"],
        )

    )


    conn.commit()

    conn.close()


    return render_template(

        "notifications.html",

        notifications=
        notification_list

    )


# =========================================================
# RECRUITER - UPDATE APPLICATION
# =========================================================

@app.route(

    "/recruiter/application/"
    "<int:application_id>/"
    "<status>",

    methods=["POST"]

)
def update_application_status(

    application_id,

    status

):

    check = recruiter_required()

    if check:

        return check


    status = (
        status.capitalize()
    )


    allowed_statuses = {

        "Shortlisted",

        "Rejected",

        "Pending"

    }


    if status not in allowed_statuses:

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    conn = get_db()


    application = conn.execute(

        """
        SELECT

            a.*,

            j.title,

            j.recruiter_id

        FROM applications a

        JOIN jobs j

        ON a.job_id = j.id

        WHERE a.id = ?

        """,

        (
            application_id,
        )

    ).fetchone()


    if not application:

        conn.close()

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    if (

        application[
            "recruiter_id"
        ]

        !=

        session[
            "user_id"
        ]

    ):

        conn.close()

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    conn.execute(

        """
        UPDATE applications

        SET status = ?

        WHERE id = ?

        """,

        (
            status,

            application_id
        )

    )


    message = (

        f"Your application for "
        f"{application['title']} "
        f"has been updated to "
        f"{status}."

    )


    conn.execute(

        """
        INSERT INTO notifications

        (
            candidate_id,

            application_id,

            message,

            is_read

        )

        VALUES (?, ?, ?, 0)

        """,

        (

            application[
                "candidate_id"
            ],

            application_id,

            message

        )

    )


    conn.commit()

    conn.close()


    return redirect(

        url_for(
            "recruiter_candidates"
        )

    )


# =========================================================
# RECRUITER - SEND GENERIC REQUEST
# =========================================================

@app.route(

    "/recruiter/candidate/"
    "<int:candidate_id>/request",

    methods=["POST"]

)
def send_candidate_request(
    candidate_id
):

    check = recruiter_required()

    if check:

        return check


    request_type = request.form.get(

        "request_type",

        "job"

    ).strip().lower()


    if request_type not in {
        "job",
        "interview"
    }:

        request_type = "job"


    raw_job_id = request.form.get(
        "job_id",
        ""
    ).strip()


    job_id = (
        raw_job_id
        or None
    )


    message = request.form.get(
        "message",
        ""
    ).strip()


    conn = get_db()


    candidate = conn.execute(

        """
        SELECT id

        FROM users

        WHERE id = ?

        AND LOWER(role)
            = 'candidate'

        """,

        (
            candidate_id,
        )

    ).fetchone()


    if not candidate:

        conn.close()

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    job = None


    if job_id:

        job = conn.execute(

            """
            SELECT *

            FROM jobs

            WHERE id = ?

            AND recruiter_id = ?

            """,

            (

                job_id,

                session[
                    "user_id"
                ]

            )

        ).fetchone()


    if (

        request_type == "job"

        and

        not job

    ):

        conn.close()

        return redirect(

            url_for(

                "recruiter_candidate_profile",

                candidate_id=
                candidate_id

            )

        )


    existing = conn.execute(

        """
        SELECT id

        FROM recruiter_requests

        WHERE recruiter_id = ?

        AND candidate_id = ?

        AND request_type = ?

        AND COALESCE(job_id, 0)
            = COALESCE(?, 0)

        AND status = 'Pending'

        """,

        (

            session[
                "user_id"
            ],

            candidate_id,

            request_type,

            job_id

        )

    ).fetchone()


    if not existing:

        conn.execute(

            """
            INSERT INTO recruiter_requests

            (
                recruiter_id,

                candidate_id,

                job_id,

                request_type,

                message,

                status

            )

            VALUES (?, ?, ?, ?, ?, 'Pending')

            """,

            (

                session[
                    "user_id"
                ],

                candidate_id,

                job_id,

                request_type,

                message

            )

        )


        job_title = (

            job["title"]

            if job

            else
            "the selected position"

        )


        request_label = (

            "job"

            if request_type == "job"

            else
            "interview"

        )


        conn.execute(

            """
            INSERT INTO notifications

            (
                candidate_id,

                application_id,

                message,

                is_read

            )

            VALUES (?, ?, ?, 0)

            """,

            (

                candidate_id,

                None,

                (

                    "Recruiter sent you a "
                    f"{request_label} request "
                    f"for {job_title}."

                )

            )

        )


        conn.commit()


    conn.close()


    return redirect(

        url_for(

            "recruiter_candidate_profile",

            candidate_id=
            candidate_id

        )

    )


# =========================================================
# OLD COMPATIBILITY - JOB REQUEST
# =========================================================

@app.route(
    "/recruiter/request/job",
    methods=["POST"]
)
def recruiter_job_request():

    candidate_id = request.form.get(
        "candidate_id",
        ""
    ).strip()


    job_id = request.form.get(
        "job_id",
        ""
    ).strip()


    if (
        not candidate_id
        or not job_id
    ):

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    check = recruiter_required()

    if check:

        return check


    conn = get_db()


    job = conn.execute(

        """
        SELECT *

        FROM jobs

        WHERE id = ?

        AND recruiter_id = ?

        """,

        (

            job_id,

            session[
                "user_id"
            ]

        )

    ).fetchone()


    candidate = conn.execute(

        """
        SELECT id

        FROM users

        WHERE id = ?

        AND LOWER(role)
            = 'candidate'

        """,

        (
            candidate_id,
        )

    ).fetchone()


    if (
        not job
        or not candidate
    ):

        conn.close()

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    existing = conn.execute(

        """
        SELECT id

        FROM recruiter_requests

        WHERE recruiter_id = ?

        AND candidate_id = ?

        AND job_id = ?

        AND request_type = 'job'

        AND status = 'Pending'

        """,

        (

            session[
                "user_id"
            ],

            candidate_id,

            job_id

        )

    ).fetchone()


    if not existing:

        conn.execute(

            """
            INSERT INTO recruiter_requests

            (
                recruiter_id,

                candidate_id,

                job_id,

                request_type,

                message,

                status

            )

            VALUES (?, ?, ?, 'job', ?, 'Pending')

            """,

            (

                session[
                    "user_id"
                ],

                candidate_id,

                job_id,

                request.form.get(
                    "message",
                    ""
                ).strip()

            )

        )


        conn.execute(

            """
            INSERT INTO notifications

            (
                candidate_id,

                application_id,

                message,

                is_read

            )

            VALUES (?, ?, ?, 0)

            """,

            (

                candidate_id,

                None,

                (
                    "Recruiter sent you a "
                    f"job request for "
                    f"{job['title']}."

                )

            )

        )


        conn.commit()


    conn.close()


    return redirect(

        url_for(

            "recruiter_candidate_profile",

            candidate_id=
            candidate_id

        )

    )


# =========================================================
# OLD COMPATIBILITY - INTERVIEW REQUEST
# =========================================================

@app.route(
    "/recruiter/request/interview",
    methods=["POST"]
)
def recruiter_interview_request():

    check = recruiter_required()

    if check:

        return check


    candidate_id = request.form.get(
        "candidate_id",
        ""
    ).strip()


    job_id = request.form.get(
        "job_id",
        ""
    ).strip() or None


    message = request.form.get(
        "message",
        ""
    ).strip()


    if not candidate_id:

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    conn = get_db()


    candidate = conn.execute(

        """
        SELECT id

        FROM users

        WHERE id = ?

        AND LOWER(role)
            = 'candidate'

        """,

        (
            candidate_id,
        )

    ).fetchone()


    if not candidate:

        conn.close()

        return redirect(

            url_for(
                "recruiter_candidates"
            )

        )


    job = None


    if job_id:

        job = conn.execute(

            """
            SELECT *

            FROM jobs

            WHERE id = ?

            AND recruiter_id = ?

            """,

            (

                job_id,

                session[
                    "user_id"
                ]

            )

        ).fetchone()


        if not job:

            job_id = None


    existing = conn.execute(

        """
        SELECT id

        FROM recruiter_requests

        WHERE recruiter_id = ?

        AND candidate_id = ?

        AND request_type = 'interview'

        AND COALESCE(job_id, 0)
            = COALESCE(?, 0)

        AND status = 'Pending'

        """,

        (

            session[
                "user_id"
            ],

            candidate_id,

            job_id

        )

    ).fetchone()


    if not existing:

        conn.execute(

            """
            INSERT INTO recruiter_requests

            (
                recruiter_id,

                candidate_id,

                job_id,

                request_type,

                message,

                status

            )

            VALUES (
                ?, ?, ?, 'interview', ?, 'Pending'
            )

            """,

            (

                session[
                    "user_id"
                ],

                candidate_id,

                job_id,

                message

            )

        )


        job_text = (

            f" for {job['title']}"

            if job

            else
            ""

        )


        conn.execute(

            """
            INSERT INTO notifications

            (
                candidate_id,

                application_id,

                message,

                is_read

            )

            VALUES (?, ?, ?, 0)

            """,

            (

                candidate_id,

                None,

                (
                    "Recruiter sent you an "
                    "interview request"
                    f"{job_text}."

                )

            )

        )


        conn.commit()


    conn.close()


    return redirect(

        url_for(

            "recruiter_candidate_profile",

            candidate_id=
            candidate_id

        )

    )


# =========================================================
# CANDIDATE REQUESTS
# =========================================================

@app.route("/requests")
@app.route("/candidate/requests")
def candidate_requests():

    check = candidate_required()

    if check:

        return check


    conn = get_db()


    requests_list = conn.execute(

        """
        SELECT

            rr.*,

            j.title AS job_title,

            j.company,

            j.location,

            u.name AS recruiter_name,

            u.email AS recruiter_email

        FROM recruiter_requests rr

        JOIN users u

        ON rr.recruiter_id = u.id

        LEFT JOIN jobs j

        ON rr.job_id = j.id

        WHERE rr.candidate_id = ?

        ORDER BY rr.created_at DESC

        """,

        (
            session[
                "user_id"
            ],
        )

    ).fetchall()


    conn.close()


    return render_template(

        "candidate_requests.html",

        requests=requests_list

    )


# =========================================================
# CANDIDATE RESPOND TO REQUEST
# =========================================================

@app.route(
    "/requests/<int:request_id>/<action>",
    methods=["POST"]
)
def respond_to_request(
    request_id,
    action
):

    check = candidate_required()

    if check:

        return check


    if action not in {
        "accept",
        "decline"
    }:

        return redirect(

            url_for(
                "candidate_requests"
            )

        )


    conn = get_db()


    req = conn.execute(

        """
        SELECT *

        FROM recruiter_requests

        WHERE id = ?

        AND candidate_id = ?

        """,

        (

            request_id,

            session[
                "user_id"
            ]

        )

    ).fetchone()


    if not req:

        conn.close()

        return redirect(

            url_for(
                "candidate_requests"
            )

        )


    # Prevent changing processed requests

    if req["status"] != "Pending":

        conn.close()

        return redirect(

            url_for(
                "candidate_requests"
            )

        )


    new_status = (

        "Accepted"

        if action == "accept"

        else
        "Declined"

    )


    conn.execute(

        """
        UPDATE recruiter_requests

        SET status = ?

        WHERE id = ?

        """,

        (

            new_status,

            request_id

        )

    )


    # -----------------------------------------------------
    # ACCEPT JOB REQUEST
    # -----------------------------------------------------

    if (

        action == "accept"

        and

        req["request_type"]
        == "job"

        and

        req["job_id"]

    ):

        existing = conn.execute(

            """
            SELECT id

            FROM applications

            WHERE job_id = ?

            AND candidate_id = ?

            """,

            (

                req["job_id"],

                session[
                    "user_id"
                ]

            )

        ).fetchone()


        if not existing:

            cursor = conn.execute(

                """
                INSERT INTO applications

                (
                    job_id,

                    candidate_id,

                    status

                )

                VALUES (
                    ?, ?, 'Applied'
                )

                """,

                (

                    req["job_id"],

                    session[
                        "user_id"
                    ]

                )

            )


            application_id = (
                cursor.lastrowid
            )


            conn.execute(

                """
                INSERT INTO notifications

                (
                    candidate_id,

                    application_id,

                    message,

                    is_read

                )

                VALUES (?, ?, ?, 0)

                """,

                (

                    session[
                        "user_id"
                    ],

                    application_id,

                    (
                        "You accepted the "
                        "recruiter job request."
                    )

                )

            )


    # -----------------------------------------------------
    # NOTIFY CANDIDATE
    # -----------------------------------------------------

    conn.execute(

        """
        INSERT INTO notifications

        (
            candidate_id,

            application_id,

            message,

            is_read

        )

        VALUES (?, ?, ?, 0)

        """,

        (

            session[
                "user_id"
            ],

            None,

            (
                f"You {action}ed the recruiter "
                f"{req['request_type']} request."
            )

        )

    )


    conn.commit()

    conn.close()


    # -----------------------------------------------------
    # ACCEPT INTERVIEW REQUEST
    # -----------------------------------------------------

    if (

        action == "accept"

        and

        req["request_type"]
        == "interview"

    ):

        return redirect(

            url_for(
                "interview"
            )

        )


    return redirect(

        url_for(
            "candidate_requests"
        )

    )


# =========================================================
# OLD ACCEPT / DECLINE COMPATIBILITY ROUTES
# =========================================================

@app.route(
    "/candidate/request/"
    "<int:request_id>/accept",
    methods=["POST"]
)
def accept_candidate_request(
    request_id
):

    return respond_to_request(

        request_id,

        "accept"

    )


@app.route(
    "/candidate/request/"
    "<int:request_id>/decline",
    methods=["POST"]
)
def decline_candidate_request(
    request_id
):

    return respond_to_request(

        request_id,

        "decline"

    )


# =========================================================
# START AI INTERVIEW
# =========================================================

@app.route(
    "/interview",
    methods=["GET", "POST"]
)
def interview():

    check = candidate_required()

    if check:

        return check


    filename, filepath = (
        get_latest_resume()
    )


    # -----------------------------------------------------
    # SETTINGS PAGE
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template(

            "interview.html",

            filename=filename,

            resume_uploaded=
            bool(filepath),

            error=None

        )


    # -----------------------------------------------------
    # CHECK RESUME
    # -----------------------------------------------------

    if not filepath:

        return render_template(

            "interview.html",

            filename=None,

            resume_uploaded=False,

            error=(

                "Please upload your resume "
                "before starting "
                "the AI interview."

            )

        )


    # -----------------------------------------------------
    # DURATION -> QUESTION COUNT
    # -----------------------------------------------------

    try:

        duration = int(

            request.form.get(

                "duration",

                15

            )

        )

    except (
        TypeError,
        ValueError
    ):

        duration = 15


    if duration == 15:

        question_count = 10

    elif duration == 20:

        question_count = 20

    elif duration == 30:

        question_count = 30

    else:

        duration = 15

        question_count = 10


    # -----------------------------------------------------
    # INTERVIEW TYPE
    # -----------------------------------------------------

    interview_type = (

        request.form.get(

            "interview_type",

            "hr"

        )

        .strip()

        .lower()

    )


    if interview_type not in {

        "hr",

        "technical"

    }:

        interview_type = "hr"


    # -----------------------------------------------------
    # READ RESUME
    # -----------------------------------------------------

    try:

        resume_text = (
            extract_resume_text(
                filepath
            )
        )


    except Exception as error:

        return render_template(

            "interview.html",

            filename=filename,

            resume_uploaded=True,

            error=(
                f"Could not read resume: "
                f"{error}"
            )

        )


    if not resume_text:

        return render_template(

            "interview.html",

            filename=filename,

            resume_uploaded=True,

            error=(

                "Could not extract text "
                "from your resume. "
                "Please upload a valid "
                "PDF or DOCX resume."

            )

        )


    # -----------------------------------------------------
    # CANCEL OLD ACTIVE INTERVIEW
    # -----------------------------------------------------

    conn = get_db()


    conn.execute(

        """
        UPDATE active_interviews

        SET status = 'cancelled'

        WHERE candidate_id = ?

        AND status = 'active'

        """,

        (

            session[
                "user_id"
            ],

        )

    )


    conn.commit()

    conn.close()


    # -----------------------------------------------------
    # GENERATE FIRST QUESTION
    # -----------------------------------------------------

    try:

        first_question, interaction_id = (

            generate_first_interview_question(

                resume_text,

                interview_type,

                question_count

            )

        )


    except Exception as error:

        print(

            "FIRST INTERVIEW QUESTION ERROR:",

            type(error).__name__,

            str(error)

        )


        return render_template(

            "interview.html",

            filename=filename,

            resume_uploaded=True,

            error=(

                "Gemini could not generate "
                "the interview question. "
                "Please check "
                "GEMINI_API_KEY/model "
                "and try again."

            )

        )


    # -----------------------------------------------------
    # CREATE SERVER-SIDE INTERVIEW
    # -----------------------------------------------------

    start_time = time.time()


    questions = [
        first_question
    ]


    answers = []


    scores = []


    conn = get_db()


    cursor = conn.execute(

        """
        INSERT INTO active_interviews

        (
            candidate_id,

            duration,

            total_questions,

            interview_type,

            start_time,

            current_index,

            current_question,

            questions,

            answers,

            scores,

            interaction_id,

            resume_text,

            status

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, 'active'
        )

        """,

        (

            session[
                "user_id"
            ],

            duration,

            question_count,

            interview_type,

            start_time,

            0,

            first_question,

            json.dumps(
                questions
            ),

            json.dumps(
                answers
            ),

            json.dumps(
                scores
            ),

            interaction_id,

            resume_text[
                :12000
            ]

        )

    )


    interview_id = (
        cursor.lastrowid
    )


    conn.commit()

    conn.close()


    # Small ID only

    session[
        "interview_id"
    ] = interview_id


    return redirect(

        url_for(
            "interview_question"
        )

    )


# =========================================================
# INTERVIEW QUESTION
# =========================================================

@app.route(
    "/interview/question",
    methods=["GET", "POST"]
)
def interview_question():

    check = candidate_required()

    if check:

        return check


    interview_id = session.get(
        "interview_id"
    )


    if not interview_id:

        return redirect(

            url_for(
                "interview"
            )

        )


    conn = get_db()


    interview_row = conn.execute(

        """
        SELECT *

        FROM active_interviews

        WHERE id = ?

        AND candidate_id = ?

        AND status = 'active'

        """,

        (

            interview_id,

            session[
                "user_id"
            ]

        )

    ).fetchone()


    conn.close()


    if not interview_row:

        session.pop(

            "interview_id",

            None

        )


        return redirect(

            url_for(
                "interview"
            )

        )


    try:

        questions = json.loads(

            interview_row[
                "questions"
            ]

            or "[]"

        )

    except Exception:

        questions = []


    try:

        answers = json.loads(

            interview_row[
                "answers"
            ]

            or "[]"

        )

    except Exception:

        answers = []


    try:

        scores = json.loads(

            interview_row[
                "scores"
            ]

            or "[]"

        )

    except Exception:

        scores = []


    total_questions = int(

        interview_row[
            "total_questions"
        ]

        or 1

    )


    current_index = int(

        interview_row[
            "current_index"
        ]

        or 0

    )


    # -----------------------------------------------------
    # TIMER
    # -----------------------------------------------------

    elapsed_seconds = (

        time.time()

        -

        float(

            interview_row[
                "start_time"
            ]

        )

    )


    duration_seconds = (

        int(

            interview_row[
                "duration"
            ]

        )

        * 60

    )


    remaining_seconds = max(

        0,

        int(

            duration_seconds
            -
            elapsed_seconds

        )

    )


    # -----------------------------------------------------
    # TIME EXPIRED
    # -----------------------------------------------------

    if remaining_seconds <= 0:

        return finish_interview(

            session[
                "user_id"
            ],

            interview_id

        )


    # -----------------------------------------------------
    # CORRUPT/FINISHED STATE
    # -----------------------------------------------------

    if current_index >= len(
        questions
    ):

        return finish_interview(

            session[
                "user_id"
            ],

            interview_id

        )


    current_question = (

        questions[
            current_index
        ]

    )


    # -----------------------------------------------------
    # SUBMIT ANSWER
    # -----------------------------------------------------

    if request.method == "POST":

        answer = request.form.get(

            "answer",

            ""

        ).strip()


        # Check timer again

        elapsed_seconds = (

            time.time()

            -

            float(

                interview_row[
                    "start_time"
                ]

            )

        )


        if elapsed_seconds >= duration_seconds:

            return finish_interview(

                session[
                    "user_id"
                ],

                interview_id

            )


        next_index = (

            current_index

            +

            1

        )


        # -------------------------------------------------
        # FINAL QUESTION
        # -------------------------------------------------

        if next_index >= total_questions:

            score = fallback_answer_score(
                answer
            )


            final_interaction_id = (

                interview_row[
                    "interaction_id"
                ]

            )


            answers.append(
                answer
            )


            scores.append(
                score
            )


            conn = get_db()


            conn.execute(

                """
                UPDATE active_interviews

                SET

                    current_index = ?,

                    answers = ?,

                    scores = ?,

                    interaction_id = ?

                WHERE id = ?

                """,

                (

                    next_index,

                    json.dumps(
                        answers
                    ),

                    json.dumps(
                        scores
                    ),

                    final_interaction_id,

                    interview_id

                )

            )


            conn.commit()

            conn.close()


            return finish_interview(

                session[
                    "user_id"
                ],

                interview_id

            )


        # -------------------------------------------------
        # ONE GEMINI CALL
        # -------------------------------------------------

        score, next_question, next_interaction_id = (

            evaluate_answer_and_generate_followup(

                interview_row[
                    "resume_text"
                ]

                or "",

                questions,

                current_question,

                answer,

                interview_row[
                    "interview_type"
                ],

                next_index + 1,

                total_questions

            )

        )


        answers.append(
            answer
        )


        scores.append(
            score
        )


        questions.append(
            next_question
        )


        # -------------------------------------------------
        # SAVE STATE
        # -------------------------------------------------

        conn = get_db()


        conn.execute(

            """
            UPDATE active_interviews

            SET

                current_index = ?,

                current_question = ?,

                questions = ?,

                answers = ?,

                scores = ?,

                interaction_id = ?

            WHERE id = ?

            """,

            (

                next_index,

                next_question,

                json.dumps(
                    questions
                ),

                json.dumps(
                    answers
                ),

                json.dumps(
                    scores
                ),

                next_interaction_id,

                interview_id

            )

        )


        conn.commit()

        conn.close()


        return redirect(

            url_for(
                "interview_question"
            )

        )


    # -----------------------------------------------------
    # SHOW QUESTION
    # -----------------------------------------------------

    return render_template(

        "interview_question.html",

        question=
        current_question,

        question_number=
        current_index + 1,

        total_questions=
        total_questions,

        remaining_seconds=
        remaining_seconds,

        duration=
        int(
            interview_row[
                "duration"
            ]
        ),

        interview_type=
        interview_row[
            "interview_type"
        ]

    )


# =========================================================
# FINISH INTERVIEW
# =========================================================

def finish_interview(

    candidate_id,

    interview_id

):

    conn = get_db()


    interview_row = conn.execute(

        """
        SELECT *

        FROM active_interviews

        WHERE id = ?

        AND candidate_id = ?

        """,

        (

            interview_id,

            candidate_id

        )

    ).fetchone()


    if not interview_row:

        conn.close()


        session.pop(

            "interview_id",

            None

        )


        return redirect(

            url_for(
                "interview"
            )

        )


    try:

        questions = json.loads(

            interview_row[
                "questions"
            ]

            or "[]"

        )

    except Exception:

        questions = []


    try:

        answers = json.loads(

            interview_row[
                "answers"
            ]

            or "[]"

        )

    except Exception:

        answers = []


    try:

        scores = json.loads(

            interview_row[
                "scores"
            ]

            or "[]"

        )

    except Exception:

        scores = []


    total_questions = int(

        interview_row[
            "total_questions"
        ]

        or

        len(
            questions
        )

        or 1

    )


    # Fill missing scores

    while len(
        scores
    ) < total_questions:

        scores.append(
            0
        )


    while len(
        answers
    ) < total_questions:

        answers.append(
            ""
        )


    total_score = sum(

        max(

            0,

            min(

                5,

                int(score)

            )

        )

        for score
        in scores[
            :total_questions
        ]

    )


    percentage = int(

        (

            total_score

            /

            (
                total_questions
                * 5
            )

        )

        * 100

    )


    if percentage >= 80:

        message = (
            "Excellent interview performance!"
        )


    elif percentage >= 60:

        message = (

            "Good performance. "
            "There is still room "
            "for improvement."

        )


    elif percentage >= 40:

        message = (

            "Average performance. "
            "Keep improving "
            "your interview answers."

        )


    else:

        message = (

            "Keep practicing and "
            "improve your interview answers."

        )


    # -----------------------------------------------------
    # SAVE RESULT
    # -----------------------------------------------------

    conn.execute(

        """
        INSERT INTO interview_results

        (
            candidate_id,

            score,

            total,

            percentage,

            message,

            questions,

            answers,

            scores

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?
        )

        """,

        (

            candidate_id,

            total_score,

            total_questions,

            percentage,

            message,

            json.dumps(
                questions[
                    :total_questions
                ]
            ),

            json.dumps(
                answers[
                    :total_questions
                ]
            ),

            json.dumps(
                scores[
                    :total_questions
                ]
            )

        )

    )


    # -----------------------------------------------------
    # MARK COMPLETE
    # -----------------------------------------------------

    conn.execute(

        """
        UPDATE active_interviews

        SET status = 'completed'

        WHERE id = ?

        """,

        (
            interview_id,
        )

    )


    conn.commit()

    conn.close()


    # -----------------------------------------------------
    # SAVE RESULT VALUES IN SESSION
    # -----------------------------------------------------

    session.pop(
        "interview_id",
        None
    )


    session[
        "last_interview_score"
    ] = total_score


    session[
        "last_interview_total"
    ] = total_questions


    session[
        "last_interview_percentage"
    ] = percentage


    session[
        "last_interview_message"
    ] = message


    return redirect(

        url_for(
            "interview_result"
        )

    )


# =========================================================
# INTERVIEW RESULT
# =========================================================

@app.route(
    "/interview/result"
)
def interview_result():

    check = candidate_required()

    if check:

        return check


    score = session.get(

        "last_interview_score",

        0

    )


    total = session.get(

        "last_interview_total",

        0

    )


    percentage = session.get(

        "last_interview_percentage",

        0

    )


    message = session.get(

        "last_interview_message",

        ""

    )


    if not total:

        conn = get_db()


        result = conn.execute(

            """
            SELECT *

            FROM interview_results

            WHERE candidate_id = ?

            ORDER BY created_at DESC

            LIMIT 1

            """,

            (

                session[
                    "user_id"
                ]

            )

        ).fetchone()


        conn.close()


        if result:

            score = (
                result["score"]
                or 0
            )


            total = (
                result["total"]
                or 0
            )


            percentage = (
                result["percentage"]
                or 0
            )


            message = (

                result["message"]

                or

                result["feedback"]

                or

                ""

            )


    return render_template(

        "interview_result.html",

        score=score,

        total=total,

        percentage=percentage,

        message=message

    )


# =========================================================
# TEST GEMINI
# =========================================================

@app.route(
    "/test_gemini"
)
def test_gemini():

    if gemini_client is None:

        return """
        <h2>
            Gemini is not configured.
        </h2>

        <p>
            Configure GEMINI_API_KEY
            in Vercel Environment Variables.
        </p>
        """


    result = ask_gemini(

        """
        Say hello and confirm that
        HireSmart AI Gemini integration
        is working.
        """

    )


    if not result:

        return """
        <h2>
            Gemini request failed.
        </h2>

        <p>
            Check the server logs
            and GEMINI_API_KEY.
        </p>
        """


    safe_result = (

        result

        .replace(
            "&",
            "&amp;"
        )

        .replace(
            "<",
            "&lt;"
        )

        .replace(
            ">",
            "&gt;"
        )

    )


    return f"""
    <h2>
        Gemini Integration Working ✅
    </h2>

    <p>
        {safe_result}
    </p>

    <a href="/">
        Back to HireSmart AI
    </a>
    """


# =========================================================
# CREATE DATABASE
# =========================================================

create_table()


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )