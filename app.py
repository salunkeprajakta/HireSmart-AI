from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import timedelta
import sqlite3
import os
import json

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from pypdf import PdfReader
from docx import Document

from google import genai


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

# Secure cookie only on HTTPS/Vercel
app.config["SESSION_COOKIE_SECURE"] = bool(
    os.getenv("VERCEL")
)


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

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

gemini_client = None


if (
    GEMINI_API_KEY
    and GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE"
):

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print(
            "Gemini client initialized successfully."
        )

        print(
            "Gemini model:",
            GEMINI_MODEL
        )

    except Exception as error:

        gemini_client = None

        print(
            "Gemini initialization error:",
            error
        )

else:

    print(
        "WARNING: GEMINI_API_KEY is not configured."
    )


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
# ASK GEMINI
# =========================================================

def ask_gemini(prompt):

    if gemini_client is None:

        return ""

    try:

        response = gemini_client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        result = getattr(
            response,
            "output_text",
            ""
        )

        return (
            result or ""
        ).strip()

    except Exception as error:

        print(
            "GEMINI ERROR:",
            type(error).__name__,
            str(error)
        )

        return ""


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# ADD COLUMN IF MISSING
# =========================================================

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

    user_columns = [

        ("phone", "TEXT"),

        ("education", "TEXT"),

        ("skills", "TEXT"),

        ("experience", "TEXT"),

        ("resume_score", "INTEGER"),

        ("resume_skills", "TEXT"),

        ("resume_analysis", "TEXT"),

        ("resume_suggestions", "TEXT")
    ]

    for column, definition in user_columns:

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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
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

            applied_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    interview_columns = [

        ("total", "INTEGER"),

        ("percentage", "INTEGER"),

        ("message", "TEXT"),

        ("questions", "TEXT"),

        ("answers", "TEXT"),

        ("scores", "TEXT")
    ]

    for column, definition in interview_columns:

        add_column_if_missing(
            conn,
            "interview_results",
            column,
            definition
        )


    conn.commit()

    conn.close()


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# EXTRACT RESUME TEXT
# =========================================================

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

                text = page.extract_text()

                if text:

                    parts.append(
                        text
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
            "RESUME EXTRACTION ERROR:",
            error
        )

    return "\n".join(
        parts
    ).strip()


# =========================================================
# GET LATEST RESUME
# =========================================================

def get_latest_resume_for_user(
    user_id
):

    prefix = (
        f"{user_id}_"
    )

    folder = app.config[
        "UPLOAD_FOLDER"
    ]

    if not os.path.isdir(
        folder
    ):

        return None, None

    files = [

        filename

        for filename
        in os.listdir(folder)

        if filename.startswith(prefix)
        and allowed_file(filename)
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


# =========================================================
# SAVE RESUME ANALYSIS
# =========================================================

def save_resume_analysis(
    user_id,
    filename,
    score,
    skills,
    missing_skills,
    suggestions,
    analysis=None
):

    conn = get_db()

    if analysis is None:

        analysis = (
            f"Detected "
            f"{len(skills)} "
            f"relevant skills "
            f"in {filename}."
        )

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
            ", ".join(skills),
            analysis,
            "\n".join(
                suggestions
            ),
            user_id
        )
    )

    conn.commit()

    conn.close()


# =========================================================
# GET RESUME ANALYSIS
# =========================================================

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
# GENERATE INTERVIEW QUESTIONS
# =========================================================

def generate_resume_interview_questions(
    resume_text
):

    prompt = f"""
Create exactly 5 short interview questions
for a candidate based on this resume.

Return only the questions.

One question per line.

Do not add numbering.

Resume:

{resume_text[:12000]}
"""

    result = ask_gemini(
        prompt
    )

    questions = []

    for line in result.splitlines():

        clean = line.strip()

        clean = clean.lstrip(
            "0123456789.-) "
        )

        if clean:

            questions.append(
                clean
            )

    return questions[:5]


# =========================================================
# CHECK INTERVIEW ANSWER
# =========================================================

def check_interview_answer(
    question,
    answer
):

    if not answer.strip():

        return 0

    prompt = f"""
Rate this interview answer
from 0 to 5.

Return only the integer.

Question:
{question}

Answer:
{answer}
"""

    result = ask_gemini(
        prompt
    )

    try:

        score = int(
            float(
                result.strip().split()[0]
            )
        )

        return max(
            0,
            min(
                5,
                score
            )
        )

    except Exception:

        word_count = len(
            answer.split()
        )

        if word_count >= 60:
            return 5

        if word_count >= 35:
            return 4

        if word_count >= 15:
            return 3

        return 2


# =========================================================
# AUTH HELPERS
# =========================================================

def candidate_required():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get(
        "user_role",
        ""
    ).lower() != "candidate":

        return redirect(
            url_for("recruiter_dashboard")
        )

    return None


def recruiter_required():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get(
        "user_role",
        ""
    ).lower() != "recruiter":

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

        if session.get(
            "user_role",
            ""
        ).lower() == "recruiter":

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

        if session.get(
            "user_role",
            ""
        ).lower() == "recruiter":

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

        if session.get(
            "user_role",
            ""
        ).lower() == "recruiter":

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

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            session["user_role"] = user["role"]

            if (
                user["role"].lower()
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

        if (
            new_password
            != confirm_password
        ):

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
        <h2>Password Reset Successful! ✅</h2>
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

    if session.get(
        "user_role",
        ""
    ).lower() == "recruiter":

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

        name=session[
            "user_name"
        ],

        email=session[
            "user_email"
        ],

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

    jobs = conn.execute(
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
        SELECT COUNT(*)

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

        name=session[
            "user_name"
        ],

        email=session[
            "user_email"
        ],

        jobs=jobs,

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

    jobs = conn.execute(
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
        jobs=jobs
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
                SELECT a.status

                FROM applications a

                JOIN jobs j
                ON a.job_id = j.id

                WHERE a.candidate_id = u.id

                AND j.recruiter_id = ?

                ORDER BY a.applied_at DESC

                LIMIT 1

            ) AS status

        FROM users u

        WHERE LOWER(u.role) = 'candidate'

        ORDER BY u.name ASC
        """,
        (
            session["user_id"],
            session["user_id"],
            session["user_id"]
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

        AND LOWER(role) = 'candidate'
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

    jobs = conn.execute(
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

        jobs=jobs,

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

    if request.method == "POST":

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

        filename = (
            str(session["user_id"])
            + "_"
            + secure_filename(
                file.filename
            )
        )

        filepath = os.path.join(
            app.config[
                "UPLOAD_FOLDER"
            ],
            filename
        )

        file.save(
            filepath
        )

        resume_text = extract_resume_text(
            filepath
        )

        if not resume_text:

            return """
            <h2>
                Could not read the resume.
            </h2>

            <a href="/upload_resume">
                Try Again
            </a>
            """

        prompt = f"""
You are an AI resume analyzer.

Analyze this resume.

Return exactly:

SCORE:
[number from 0 to 100]

SKILLS:
comma separated skills

ANALYSIS:
short professional analysis

SUGGESTIONS:
short improvement suggestions

Resume:

{resume_text[:16000]}
"""

        ai_result = ask_gemini(
            prompt
        )

        score = 0

        skills = ""

        analysis = ""

        suggestions = ""

        section = None

        analysis_lines = []

        suggestion_lines = []


        for raw_line in ai_result.splitlines():

            line = raw_line.strip()

            upper = line.upper()

            if upper.startswith(
                "SCORE:"
            ):

                try:

                    score = int(
                        float(
                            line.split(
                                ":",
                                1
                            )[1]
                            .replace(
                                "%",
                                ""
                            )
                            .strip()
                        )
                    )

                    score = max(
                        0,
                        min(
                            100,
                            score
                        )
                    )

                except Exception:

                    score = 0


            elif upper.startswith(
                "SKILLS:"
            ):

                section = "skills"

                skills = line.split(
                    ":",
                    1
                )[1].strip()


            elif upper.startswith(
                "ANALYSIS:"
            ):

                section = "analysis"

                value = line.split(
                    ":",
                    1
                )[1].strip()

                if value:

                    analysis_lines.append(
                        value
                    )


            elif upper.startswith(
                "SUGGESTIONS:"
            ):

                section = "suggestions"

                value = line.split(
                    ":",
                    1
                )[1].strip()

                if value:

                    suggestion_lines.append(
                        value
                    )


            elif line:

                if section == "analysis":

                    analysis_lines.append(
                        line
                    )

                elif section == "suggestions":

                    suggestion_lines.append(
                        line
                    )


        analysis = (
            "\n".join(
                analysis_lines
            )
            or
            "Resume uploaded successfully."
        )

        suggestions = (
            "\n".join(
                suggestion_lines
            )
            or
            "Keep your resume updated and tailored to the target role."
        )


        if not skills:

            text_lower = resume_text.lower()

            detected = [

                skill

                for skill
                in SKILLS_LIST

                if skill.lower()
                in text_lower
            ]

            skills = ", ".join(
                detected
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
                skills,
                analysis,
                suggestions,
                session["user_id"]
            )
        )

        conn.commit()

        conn.close()

        return render_template(
            "resume_uploaded.html",
            filename=filename
        )

    return render_template(
        "upload_resume.html"
    )
# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route("/resume_analysis")
def resume_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # GET LATEST RESUME
    # -----------------------------------------------------

    filename, filepath = get_latest_resume()

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

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if not os.path.isfile(filepath):

        return render_template(
            "resume_analysis.html",

            filename=filename,

            skills=[],

            missing_skills=[],

            score=0,

            suggestions=[
                "Resume file was not found.",
                "Please upload your resume again."
            ],

            resume_text="",

            resume_information={}
        )

    # -----------------------------------------------------
    # EXTRACT RESUME TEXT
    # -----------------------------------------------------

    try:

        resume_text = extract_resume_text(
            filepath
        )

    except Exception as error:

        print(
            "Resume extraction error:",
            repr(error)
        )

        return render_template(
            "resume_analysis.html",

            filename=filename,

            skills=[],

            missing_skills=[],

            score=0,

            suggestions=[
                "Could not read your resume.",
                "Please upload a text-based PDF or DOCX file."
            ],

            resume_text="",

            resume_information={}
        )

    # -----------------------------------------------------
    # EMPTY RESUME CHECK
    # -----------------------------------------------------

    if not resume_text or not resume_text.strip():

        return render_template(
            "resume_analysis.html",

            filename=filename,

            skills=[],

            missing_skills=[],

            score=0,

            suggestions=[
                "Could not extract text from this resume.",
                "Please upload a text-based PDF or DOCX file.",
                "Scanned/image-only PDFs may not be readable."
            ],

            resume_text="",

            resume_information={}
        )

    # -----------------------------------------------------
    # NORMALIZE TEXT
    # -----------------------------------------------------

    text_lower = resume_text.lower()

    # -----------------------------------------------------
    # DETECT SKILLS
    # -----------------------------------------------------

    found_skills = []

    for skill in SKILLS_LIST:

        if skill.lower() in text_lower:

            found_skills.append(
                skill
            )

    # Remove duplicates
    found_skills = list(
        dict.fromkeys(found_skills)
    )

    # -----------------------------------------------------
    # MISSING SKILLS
    # -----------------------------------------------------

    missing_skills = []

    for skill in SKILLS_LIST:

        if skill not in found_skills:

            missing_skills.append(
                skill
            )

    # -----------------------------------------------------
    # RESUME SCORE
    # -----------------------------------------------------

    score = 30 + (
        len(found_skills) * 7
    )

    if score > 100:

        score = 100

    # -----------------------------------------------------
    # RESUME INFORMATION
    # -----------------------------------------------------

    import re

    # Email
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        resume_text
    )

    email = (
        email_match.group(0)
        if email_match
        else "Not detected"
    )

    # Phone
    phone_match = re.search(
        r'(\+91[\s-]?)?[6-9]\d{9}',
        resume_text
    )

    phone = (
        phone_match.group(0)
        if phone_match
        else "Not detected"
    )

    # -----------------------------------------------------
    # NAME DETECTION
    # -----------------------------------------------------

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    detected_name = "Not detected"

    if lines:

        first_line = lines[0]

        if (
            len(first_line) <= 60
            and "@" not in first_line
            and not any(
                character.isdigit()
                for character in first_line
            )
        ):

            detected_name = first_line

    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    education = "Not detected"

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

    education_lines = []

    for line in lines:

        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in education_keywords
        ):

            education_lines.append(
                line
            )

    if education_lines:

        education = " | ".join(
            education_lines[:5]
        )

    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    experience = "Not detected"

    experience_keywords = [
        "experience",
        "intern",
        "internship",
        "developer",
        "software engineer",
        "worked at",
        "employment"
    ]

    experience_lines = []

    for line in lines:

        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in experience_keywords
        ):

            experience_lines.append(
                line
            )

    if experience_lines:

        experience = " | ".join(
            experience_lines[:5]
        )

    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    projects = "Not detected"

    project_lines = []

    for line in lines:

        lower_line = line.lower()

        if (
            "project" in lower_line
            or
            "developed" in lower_line
            or
            "built" in lower_line
        ):

            project_lines.append(
                line
            )

    if project_lines:

        projects = " | ".join(
            project_lines[:5]
        )

    # -----------------------------------------------------
    # RESUME INFORMATION DICTIONARY
    # -----------------------------------------------------

    resume_information = {

        "name": detected_name,

        "email": email,

        "phone": phone,

        "education": education,

        "experience": experience,

        "projects": projects,

        "skills_count": len(
            found_skills
        ),

        "resume_filename": filename
    }

    # -----------------------------------------------------
    # SUGGESTIONS
    # -----------------------------------------------------

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
            "Your resume contains good basic information. Keep it updated."
        )

    # -----------------------------------------------------
    # SAVE ANALYSIS
    # -----------------------------------------------------

    save_resume_analysis(
        session["user_id"],
        filename,
        score,
        found_skills,
        missing_skills,
        suggestions
    )

    # -----------------------------------------------------
    # RENDER PAGE
    # -----------------------------------------------------

    return render_template(

        "resume_analysis.html",

        filename=filename,

        skills=found_skills,

        missing_skills=missing_skills,

        score=score,

        suggestions=suggestions,

        resume_text=resume_text,

        resume_information=
        resume_information
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
            error=(
                "Please upload your "
                "resume first."
            )
        )

    resume_text = extract_resume_text(
        filepath
    )

    text_lower = resume_text.lower()

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

    if not existing:

        cursor = conn.execute(
            """
            INSERT INTO applications
            (
                job_id,
                candidate_id,
                status
            )

            VALUES (?, ?, ?)
            """,
            (
                job_id,
                session["user_id"],
                "Applied"
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
    "/recruiter/application/<int:application_id>/<status>",
    methods=["POST"]
)
def update_application_status(
    application_id,
    status
):

    check = recruiter_required()

    if check:

        return check

    status = status.capitalize()

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
        application["recruiter_id"]
        != session["user_id"]
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

            (
                "Your application for "
                f"{application['title']} "
                "has been updated to "
                f"{status}."
            )
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
# RECRUITER - SEND REQUEST
# =========================================================

@app.route(
    "/recruiter/candidate/<int:candidate_id>/request",
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

    job_id = request.form.get(
        "job_id",
        ""
    ).strip() or None

    message = request.form.get(
        "message",
        ""
    ).strip()


    if request_type not in {
        "job",
        "interview"
    }:

        request_type = "job"


    conn = get_db()

    candidate = conn.execute(
        """
        SELECT id

        FROM users

        WHERE id = ?

        AND LOWER(role) = 'candidate'
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
                session["user_id"]
            )
        ).fetchone()


    if (
        request_type == "job"
        and not job
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
            session["user_id"],
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
                session["user_id"],
                candidate_id,
                job_id,
                request_type,
                message
            )
        )


        if job:

            job_title = job[
                "title"
            ]

        else:

            job_title = (
                "the selected position"
            )


        request_label = (
            "job"
            if request_type == "job"
            else "interview"
        )


        conn.execute(
            """
            INSERT INTO notifications
            (
                candidate_id,
                message,
                is_read
            )

            VALUES (?, ?, 0)
            """,
            (
                candidate_id,

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
            candidate_id=candidate_id
        )
    )


# =========================================================
# OLD JOB REQUEST ROUTE
# Compatibility
# =========================================================

@app.route(
    "/recruiter/request/job",
    methods=["POST"]
)
def recruiter_job_request():

    check = recruiter_required()

    if check:

        return check

    candidate_id = request.form.get(
        "candidate_id"
    )

    job_id = request.form.get(
        "job_id"
    )

    if not candidate_id or not job_id:

        return redirect(
            url_for(
                "recruiter_candidates"
            )
        )

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
            session["user_id"]
        )
    ).fetchone()

    candidate = conn.execute(
        """
        SELECT id

        FROM users

        WHERE id = ?

        AND LOWER(role) = 'candidate'
        """,
        (
            candidate_id,
        )
    ).fetchone()

    if not job or not candidate:

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
            session["user_id"],
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
                session["user_id"],
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
                message,
                is_read
            )

            VALUES (?, ?, 0)
            """,
            (
                candidate_id,

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
            candidate_id=candidate_id
        )
    )


# =========================================================
# OLD INTERVIEW REQUEST ROUTE
# Compatibility
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
        "candidate_id"
    )

    job_id = request.form.get(
        "job_id"
    ) or None

    if not candidate_id:

        return redirect(
            url_for(
                "recruiter_candidates"
            )
        )

    conn = get_db()

    if job_id:

        valid_job = conn.execute(
            """
            SELECT id

            FROM jobs

            WHERE id = ?

            AND recruiter_id = ?
            """,
            (
                job_id,
                session["user_id"]
            )
        ).fetchone()

        if not valid_job:

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
            session["user_id"],
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

            VALUES (?, ?, ?, 'interview', ?, 'Pending')
            """,
            (
                session["user_id"],
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
                message,
                is_read
            )

            VALUES (?, ?, 0)
            """,
            (
                candidate_id,
                (
                    "Recruiter sent you an "
                    "interview request."
                )
            )
        )

        conn.commit()


    conn.close()

    return redirect(
        url_for(
            "recruiter_candidate_profile",
            candidate_id=candidate_id
        )
    )


# =========================================================
# CANDIDATE REQUESTS
# =========================================================

@app.route(
    "/requests"
)
@app.route(
    "/candidate/requests"
)
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
            session["user_id"],
        )
    ).fetchall()

    conn.close()

    return render_template(
        "candidate_requests.html",
        requests=requests_list
    )


# =========================================================
# RESPOND TO REQUEST
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
            session["user_id"]
        )
    ).fetchone()

    if not req:

        conn.close()

        return redirect(
            url_for(
                "candidate_requests"
            )
        )


    if action == "accept":

        new_status = "Accepted"

    else:

        new_status = "Declined"


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
        and req["request_type"]
        == "job"
        and req["job_id"]
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
                session["user_id"]
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

                VALUES (?, ?, 'Applied')
                """,
                (
                    req["job_id"],
                    session["user_id"]
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
                    session["user_id"],
                    application_id,
                    (
                        "You accepted the "
                        "recruiter job request."
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
        and req["request_type"]
        == "interview"
    ):

        return redirect(
            url_for("interview")
        )


    return redirect(
        url_for(
            "candidate_requests"
        )
    )


# =========================================================
# OLD ACCEPT ROUTE
# =========================================================

@app.route(
    "/candidate/request/<int:request_id>/accept",
    methods=["POST"]
)
def accept_candidate_request(
    request_id
):

    return respond_to_request(
        request_id,
        "accept"
    )


# =========================================================
# OLD DECLINE ROUTE
# =========================================================

@app.route(
    "/candidate/request/<int:request_id>/decline",
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
# START INTERVIEW
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


    if request.method == "GET":

        return render_template(
            "interview.html",

            filename=filename,

            resume_uploaded=
            bool(filepath),

            error=None
        )


    if not filepath:

        return render_template(
            "interview.html",

            filename=None,

            resume_uploaded=False,

            error=(
                "Please upload your resume "
                "before starting the AI interview."
            )
        )


    resume_text = extract_resume_text(
        filepath
    )


    questions = (
        generate_resume_interview_questions(
            resume_text
        )
    )


    if not questions:

        questions = [

            "Tell me about yourself.",

            "What technical skills do you have?",

            "Explain one project mentioned in your resume.",

            "What was your contribution to your project?",

            "Why should we hire you?"
        ]


    session[
        "interview_questions"
    ] = questions

    session[
        "interview_answers"
    ] = []

    session[
        "interview_scores"
    ] = []

    session[
        "interview_index"
    ] = 0


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

    questions = session.get(
        "interview_questions",
        []
    )

    answers = session.get(
        "interview_answers",
        []
    )

    scores = session.get(
        "interview_scores",
        []
    )

    index = session.get(
        "interview_index",
        0
    )


    if not questions:

        return redirect(
            url_for("interview")
        )


    if request.method == "POST":

        if index >= len(
            questions
        ):

            return redirect(
                url_for(
                    "interview_result"
                )
            )


        answer = request.form.get(
            "answer",
            ""
        ).strip()


        current_question = (
            questions[index]
        )


        score = check_interview_answer(
            current_question,
            answer
        )


        answers.append(
            answer
        )

        scores.append(
            score
        )


        index += 1


        session[
            "interview_answers"
        ] = answers

        session[
            "interview_scores"
        ] = scores

        session[
            "interview_index"
        ] = index


        if index >= len(
            questions
        ):

            total_score = sum(
                scores
            )

            total_questions = len(
                questions
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
                    "There is still some room "
                    "for improvement."
                )

            elif percentage >= 40:

                message = (
                    "Average performance. "
                    "Try to improve your "
                    "technical explanations."
                )

            else:

                message = (
                    "Keep practicing and improve "
                    "your interview answers."
                )


            conn = get_db()

            conn.execute(
                """
                INSERT INTO interview_results
                (
                    candidate_id,
                    score,
                    feedback,
                    total,
                    percentage,
                    message,
                    questions,
                    answers,
                    scores
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],

                    total_score,

                    message,

                    total_questions,

                    percentage,

                    message,

                    json.dumps(
                        questions
                    ),

                    json.dumps(
                        answers
                    ),

                    json.dumps(
                        scores
                    )
                )
            )

            conn.commit()

            conn.close()


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


    return render_template(
        "interview_question.html",

        question=
        questions[index],

        question_number=
        index + 1,

        total_questions=
        len(questions)
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
                session["user_id"],
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
        """


    return f"""
    <h2>
        Gemini Integration Working ✅
    </h2>

    <p>
        {result}
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