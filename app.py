from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import time

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from pypdf import PdfReader
from docx import Document

from google import genai


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "hiresmart_secret_key"


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE = "hiresmart.db"


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# GEMINI AI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.6-flash"

gemini_client = None


if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
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
    print("Fallback interview system will be used.")
    print("================================")


# =========================================================
# ASK GEMINI
# =========================================================

def ask_gemini(prompt):

    if gemini_client is None:

        print("================================")
        print("Gemini client is not initialized.")
        print("Using fallback interview system.")
        print("================================")

        return ""

    try:

        print("================================")
        print("SENDING REQUEST TO GEMINI")
        print("MODEL:", GEMINI_MODEL)
        print("================================")

        response = gemini_client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        result = getattr(
            response,
            "output_text",
            None
        )

        if not result:

            print("Gemini returned no text.")
            print("Full Gemini response:", response)

            return ""

        print("================================")
        print("GEMINI SUCCESS")
        print("================================")

        return result.strip()

    except Exception as error:

        error_text = str(error).lower()

        print("================================")
        print("GEMINI ERROR")
        print("TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("DETAIL:", repr(error))
        print("================================")

        if (
            "429" in error_text
            or "ratelimit" in error_text
            or "rate limit" in error_text
            or "quota" in error_text
            or "too_many_requests" in error_text
        ):

            print("GEMINI QUOTA EXCEEDED.")
            print("Fallback interview questions will be used.")

        return ""


# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_table():

    conn = get_db()

    # =====================================================
    # USERS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL
        )
    """)

    columns = conn.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    existing_columns = [
        column["name"]
        for column in columns
    ]

    if "phone" not in existing_columns:

        conn.execute(
            "ALTER TABLE users ADD COLUMN phone TEXT"
        )

    if "education" not in existing_columns:

        conn.execute(
            "ALTER TABLE users ADD COLUMN education TEXT"
        )

    if "skills" not in existing_columns:

        conn.execute(
            "ALTER TABLE users ADD COLUMN skills TEXT"
        )

    if "experience" not in existing_columns:

        conn.execute(
            "ALTER TABLE users ADD COLUMN experience TEXT"
        )

    # =====================================================
    # JOBS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            recruiter_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            company TEXT NOT NULL,

            location TEXT NOT NULL,

            skills TEXT NOT NULL,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # APPLICATIONS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            candidate_id INTEGER NOT NULL,

            status TEXT DEFAULT 'Applied',

            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # NOTIFICATIONS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            application_id INTEGER,

            message TEXT NOT NULL,

            is_read INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

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

        if not name or not email or not password:

            return """
            <h2>Please fill all fields.</h2>
            <a href="/register">Go Back</a>
            """

        hashed_password = generate_password_hash(
            password
        )

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                hashed_password,
                role
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <h2>Email already registered</h2>
            <p>Please use another email address.</p>
            <a href="/register">Try Again</a>
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

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        if not email or not password:

            return """
            <h2>Please enter email and password.</h2>
            <a href="/login">Go Back</a>
            """

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            email,
        )).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            if user["role"].lower() == "recruiter":

                return redirect(
                    url_for("recruiter_dashboard")
                )

            return redirect(
                url_for("dashboard")
            )

        return """
        <h2>Invalid email or password</h2>
        <a href="/login">Try Again</a>
        """

    return render_template(
        "login.html"
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
            <a href="/forgot-password">Go Back</a>
            """

        if len(new_password) < 6:

            return """
            <h2>Password must be at least 6 characters.</h2>
            <a href="/forgot-password">Try Again</a>
            """

        if new_password != confirm_password:

            return """
            <h2>Passwords do not match.</h2>
            <a href="/forgot-password">Try Again</a>
            """

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if not user:

            conn.close()

            return """
            <h2>Email not registered.</h2>
            <p>Please enter a registered email address.</p>
            <a href="/forgot-password">Try Again</a>
            """

        hashed_password = generate_password_hash(
            new_password
        )

        conn.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (
                hashed_password,
                email
            )
        )

        conn.commit()

        conn.close()

        return """
        <h2>Password Reset Successful! ✅</h2>
        <p>Your password has been updated.</p>
        <a href="/login">Go to Login</a>
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

    role = session.get(
        "user_role",
        "Candidate"
    )

    if role.lower() == "candidate":

        conn = get_db()

        notification_count = conn.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE candidate_id = ?
            AND is_read = 0
        """, (
            session["user_id"],
        )).fetchone()[0]

        conn.close()

        return render_template(
            "candidate_dashboard.html",
            name=session["user_name"],
            email=session["user_email"],
            role=role,
            notification_count=notification_count
        )

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        email=session["user_email"],
        role=role
    )


# =========================================================
# RECRUITER DASHBOARD
# =========================================================

@app.route("/recruiter/dashboard")
def recruiter_dashboard():

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

    conn = get_db()

    recruiter_jobs = conn.execute("""
        SELECT *
        FROM jobs
        WHERE recruiter_id = ?
        ORDER BY created_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    total_applications = conn.execute("""
        SELECT COUNT(applications.id)
        FROM applications
        JOIN jobs
        ON applications.job_id = jobs.id
        WHERE jobs.recruiter_id = ?
    """, (
        session["user_id"],
    )).fetchone()[0]

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
        total_applications=total_applications
    )


# =========================================================
# RECRUITER - POST JOB
# =========================================================

@app.route(
    "/recruiter/post_job",
    methods=["GET", "POST"]
)
def post_job():

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
            <h2>Please fill all required fields.</h2>
            <a href="/recruiter/post_job">
                Go Back
            </a>
            """

        conn = get_db()

        conn.execute("""
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
        """, (
            session["user_id"],
            title,
            company,
            location,
            skills,
            description
        ))

        conn.commit()

        conn.close()

        return redirect(
            url_for("recruiter_jobs")
        )

    return render_template(
        "post_job.html"
    )


# =========================================================
# RECRUITER - MY JOBS
# =========================================================

@app.route("/recruiter/jobs")
def recruiter_jobs():

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

    conn = get_db()

    jobs = conn.execute("""
        SELECT
            jobs.*,
            COUNT(applications.id) AS application_count
        FROM jobs
        LEFT JOIN applications
        ON jobs.id = applications.job_id
        WHERE jobs.recruiter_id = ?
        GROUP BY jobs.id
        ORDER BY jobs.created_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "recruiter_jobs.html",
        jobs=jobs
    )


# =========================================================
# RECRUITER - CANDIDATES
# =========================================================

@app.route("/recruiter/candidates")
def recruiter_candidates():

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

    conn = get_db()

    candidates = conn.execute("""
        SELECT
            applications.id AS application_id,
            applications.status,
            applications.applied_at,

            users.id AS candidate_id,
            users.name,
            users.email,
            users.phone,
            users.education,
            users.skills,
            users.experience,

            jobs.id AS job_id,
            jobs.title AS job_title,
            jobs.company

        FROM applications

        JOIN users
        ON applications.candidate_id = users.id

        JOIN jobs
        ON applications.job_id = jobs.id

        WHERE jobs.recruiter_id = ?

        ORDER BY applications.applied_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "recruiter_candidates.html",
        candidates=candidates
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

        conn.execute("""
            UPDATE users
            SET
                phone = ?,
                education = ?,
                skills = ?,
                experience = ?
            WHERE id = ?
        """, (
            phone,
            education,
            skills,
            experience,
            session["user_id"]
        ))

        conn.commit()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    if "." not in filename:

        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# GET LATEST RESUME
# =========================================================

def get_latest_resume():

    if "user_id" not in session:

        return None, None

    user_id = session["user_id"]

    upload_folder = os.path.abspath(
        app.config["UPLOAD_FOLDER"]
    )

    if not os.path.exists(upload_folder):

        return None, None

    user_files = []

    for filename in os.listdir(upload_folder):

        if filename.startswith(
            f"{user_id}_"
        ):

            full_path = os.path.join(
                upload_folder,
                filename
            )

            if os.path.isfile(full_path):

                user_files.append(filename)

    if not user_files:

        print(
            "NO RESUME FOUND FOR USER:",
            user_id
        )

        return None, None

    user_files.sort(
        key=lambda filename:
        os.path.getmtime(
            os.path.join(
                upload_folder,
                filename
            )
        ),
        reverse=True
    )

    filename = user_files[0]

    filepath = os.path.join(
        upload_folder,
        filename
    )

    print("================================")
    print("LATEST RESUME")
    print("User ID:", user_id)
    print("Filename:", filename)
    print("Path:", filepath)
    print(
        "Exists:",
        os.path.exists(filepath)
    )

    if os.path.exists(filepath):

        print(
            "File Size:",
            os.path.getsize(filepath)
        )

    print("================================")

    return filename, filepath


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

        filename, filepath = get_latest_resume()

        return render_template(
            "upload_resume.html",
            filename=filename
        )

    if "resume" not in request.files:

        return render_template(
            "upload_resume.html",
            error="No file selected."
        )

    file = request.files["resume"]

    if file.filename == "":

        return render_template(
            "upload_resume.html",
            error="Please select a resume."
        )

    if not allowed_file(file.filename):

        return render_template(
            "upload_resume.html",
            error="Only PDF and DOCX files are allowed."
        )

    filename = secure_filename(
        file.filename
    )

    user_id = session["user_id"]

    new_filename = (
        f"{user_id}_{filename}"
    )

    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        new_filename
    )

    file.save(upload_path)

    print("================================")
    print("RESUME UPLOADED")
    print("User ID:", user_id)
    print("Original:", filename)
    print("Saved:", new_filename)
    print(
        "Path:",
        os.path.abspath(upload_path)
    )
    print(
        "File exists:",
        os.path.exists(upload_path)
    )

    if os.path.exists(upload_path):

        print(
            "File size:",
            os.path.getsize(upload_path)
        )

    print("================================")

    return render_template(
        "resume_uploaded.html",
        filename=filename
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(filepath):

    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text
            text += "\n"

    return text


# =========================================================
# DOCX TEXT EXTRACTION
# =========================================================

def extract_text_from_docx(filepath):

    document = Document(filepath)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text
        text += "\n"

    return text


# =========================================================
# RESUME TEXT EXTRACTION
# =========================================================

def extract_resume_text(filepath):

    extension = filepath.rsplit(
        ".",
        1
    )[1].lower()

    if extension == "pdf":

        return extract_text_from_pdf(
            filepath
        )

    elif extension == "docx":

        return extract_text_from_docx(
            filepath
        )

    return ""


# =========================================================
# COMMON SKILLS
# =========================================================

SKILLS_LIST = [

    "python",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "sql",
    "flask",
    "django",
    "machine learning",
    "data science",
    "excel",
    "communication",
    "leadership",
    "git",
    "github",
    "react",
    "node.js",
    "mongodb",
    "power bi"

]


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route("/resume_analysis")
def resume_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    filename, filepath = get_latest_resume()

    if not filepath:

        return render_template(
            "resume_analysis.html",
            filename=None,
            skills=[],
            missing_skills=[],
            score=0,
            suggestions=[
                "Please upload your resume first."
            ]
        )

    try:

        resume_text = extract_resume_text(
            filepath
        )

    except Exception as error:

        return render_template(
            "resume_analysis.html",
            filename=filename,
            skills=[],
            missing_skills=[],
            score=0,
            suggestions=[
                "Could not read your resume.",
                "Please upload a text-based PDF or DOCX file.",
                str(error)
            ]
        )

    if not resume_text.strip():

        return render_template(
            "resume_analysis.html",
            filename=filename,
            skills=[],
            missing_skills=[],
            score=0,
            suggestions=[
                "Could not read this resume.",
                "Please upload a text-based PDF or DOCX file."
            ]
        )

    text_lower = resume_text.lower()

    found_skills = []

    for skill in SKILLS_LIST:

        if skill.lower() in text_lower:

            found_skills.append(skill)

    missing_skills = []

    for skill in SKILLS_LIST:

        if skill not in found_skills:

            missing_skills.append(skill)

    score = 30 + (
        len(found_skills) * 7
    )

    if score > 100:

        score = 100

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

    if "objective" not in text_lower:

        suggestions.append(
            "Add a clear career objective."
        )

    if not suggestions:

        suggestions.append(
            "Your resume has good basic information. Keep it updated."
        )

    return render_template(
        "resume_analysis.html",
        filename=filename,
        skills=found_skills,
        missing_skills=missing_skills,
        score=score,
        suggestions=suggestions
    )


# =========================================================
# SKILL ANALYSIS
# =========================================================

@app.route("/skill_analysis")
def skill_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    filename, filepath = get_latest_resume()

    if not filename:

        return """
        <h2>No Resume Found</h2>
        <p>Please upload your resume first.</p>
        <a href="/upload_resume">
        Upload Resume
        </a>
        """

    try:

        resume_text = extract_resume_text(
            filepath
        )

    except Exception as error:

        return f"""
        <h2>Could Not Read Resume</h2>
        <p>{error}</p>
        """

    if not resume_text.strip():

        return """
        <h2>Could Not Read Resume</h2>
        <p>
        Please upload a text-based PDF or DOCX.
        </p>
        """

    text_lower = resume_text.lower()

    found_skills = []
    missing_skills = []

    for skill in SKILLS_LIST:

        if skill.lower() in text_lower:

            found_skills.append(skill)

        else:

            missing_skills.append(skill)

    score = int(
        (
            len(found_skills)
            / len(SKILLS_LIST)
        ) * 100
    )

    return render_template(
        "skill_analysis.html",
        filename=filename,
        found_skills=found_skills,
        missing_skills=missing_skills,
        score=score
    )


# =========================================================
# DEFAULT JOBS
# =========================================================

JOBS = [

    {
        "title": "Python Developer",
        "company": "Tech Solutions",
        "location": "Pune",
        "skills": [
            "python",
            "flask",
            "sql",
            "git"
        ]
    },

    {
        "title": "Web Developer",
        "company": "WebWorks",
        "location": "Pune",
        "skills": [
            "html",
            "css",
            "javascript",
            "react"
        ]
    },

    {
        "title": "Data Analyst",
        "company": "DataTech",
        "location": "Mumbai",
        "skills": [
            "python",
            "sql",
            "excel",
            "power bi"
        ]
    },

    {
        "title": "Machine Learning Intern",
        "company": "AI Labs",
        "location": "Pune",
        "skills": [
            "python",
            "machine learning",
            "data science"
        ]
    },

    {
        "title": "Backend Developer",
        "company": "Software Hub",
        "location": "Bangalore",
        "skills": [
            "python",
            "flask",
            "sql",
            "mongodb"
        ]
    }

]


# =========================================================
# RECOMMENDED JOBS
# =========================================================

@app.route("/jobs")
def jobs():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    filename, filepath = get_latest_resume()

    candidate_skills = []

    if filename:

        try:

            resume_text = extract_resume_text(
                filepath
            )

            text_lower = resume_text.lower()

            for skill in SKILLS_LIST:

                if skill.lower() in text_lower:

                    candidate_skills.append(skill)

        except Exception:

            candidate_skills = []

    recommended_jobs = []

    for job in JOBS:

        required_skills = job["skills"]

        matched_skills = []

        for skill in required_skills:

            if skill in candidate_skills:

                matched_skills.append(skill)

        if required_skills:

            match_percentage = int(
                len(matched_skills)
                / len(required_skills)
                * 100
            )

        else:

            match_percentage = 0

        recommended_jobs.append({

            "title": job["title"],

            "company": job["company"],

            "location": job["location"],

            "skills": required_skills,

            "matched_skills": matched_skills,

            "match": match_percentage,

            "database_job": False

        })

    conn = get_db()

    database_jobs = conn.execute("""
        SELECT *
        FROM jobs
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    for job in database_jobs:

        required_skills = [

            skill.strip().lower()

            for skill in job["skills"].split(",")

            if skill.strip()

        ]

        matched_skills = [

            skill

            for skill in required_skills

            if skill in candidate_skills

        ]

        if required_skills:

            match_percentage = int(
                len(matched_skills)
                / len(required_skills)
                * 100
            )

        else:

            match_percentage = 0

        recommended_jobs.append({

            "id": job["id"],

            "title": job["title"],

            "company": job["company"],

            "location": job["location"],

            "skills": required_skills,

            "matched_skills": matched_skills,

            "match": match_percentage,

            "description": job["description"],

            "database_job": True

        })

    recommended_jobs.sort(
        key=lambda job: job["match"],
        reverse=True
    )

    return render_template(
        "jobs.html",
        name=session["user_name"],
        jobs=recommended_jobs
    )


# =========================================================
# APPLY FOR JOB
# =========================================================

@app.route(
    "/apply/<int:job_id>",
    methods=["POST"]
)
def apply_job(job_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get(
        "user_role",
        ""
    ).lower() != "candidate":

        return redirect(
            url_for("dashboard")
        )

    conn = get_db()

    job = conn.execute("""
        SELECT *
        FROM jobs
        WHERE id = ?
    """, (
        job_id,
    )).fetchone()

    if not job:

        conn.close()

        return """
        <h2>Job not found.</h2>
        <a href="/jobs">
        Back to Jobs
        </a>
        """

    existing_application = conn.execute("""
        SELECT *
        FROM applications
        WHERE job_id = ?
        AND candidate_id = ?
    """, (
        job_id,
        session["user_id"]
    )).fetchone()

    if existing_application:

        conn.close()

        return redirect(
            url_for("my_applications")
        )

    cursor = conn.execute("""
        INSERT INTO applications
        (
            job_id,
            candidate_id,
            status
        )
        VALUES (?, ?, ?)
    """, (
        job_id,
        session["user_id"],
        "Applied"
    ))

    application_id = cursor.lastrowid

    message = (
        f"📩 Your application for "
        f"{job['title']} at "
        f"{job['company']} "
        f"has been submitted successfully."
    )

    conn.execute("""
        INSERT INTO notifications
        (
            candidate_id,
            application_id,
            message
        )
        VALUES (?, ?, ?)
    """, (
        session["user_id"],
        application_id,
        message
    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for("my_applications")
    )


# =========================================================
# RECRUITER - UPDATE APPLICATION STATUS
# =========================================================

@app.route(
    "/recruiter/application/<int:application_id>/<status>",
    methods=["POST"]
)
def update_application_status(
    application_id,
    status
):

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

    if status not in [
        "Shortlisted",
        "Rejected"
    ]:

        return redirect(
            url_for("recruiter_candidates")
        )

    conn = get_db()

    application = conn.execute("""
        SELECT
            applications.id,
            applications.candidate_id,
            applications.status,
            jobs.title,
            jobs.company
        FROM applications
        JOIN jobs
        ON applications.job_id = jobs.id
        WHERE applications.id = ?
        AND jobs.recruiter_id = ?
    """, (
        application_id,
        session["user_id"]
    )).fetchone()

    if application:

        conn.execute("""
            UPDATE applications
            SET status = ?
            WHERE id = ?
        """, (
            status,
            application_id
        ))

        if status == "Shortlisted":

            message = (
                f"🎉 Your application for "
                f"{application['title']} at "
                f"{application['company']} "
                f"has been shortlisted!"
            )

        else:

            message = (
                f"❌ Your application for "
                f"{application['title']} at "
                f"{application['company']} "
                f"was rejected."
            )

        conn.execute("""
            INSERT INTO notifications
            (
                candidate_id,
                application_id,
                message
            )
            VALUES (?, ?, ?)
        """, (
            application["candidate_id"],
            application_id,
            message
        ))

        conn.commit()

    conn.close()

    return redirect(
        url_for("recruiter_candidates")
    )


# =========================================================
# CANDIDATE - MY APPLICATIONS
# =========================================================

@app.route("/my_applications")
def my_applications():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get(
        "user_role",
        ""
    ).lower() != "candidate":

        return redirect(
            url_for("dashboard")
        )

    conn = get_db()

    applications = conn.execute("""
        SELECT
            applications.id,
            applications.status,
            applications.applied_at,
            jobs.title,
            jobs.company,
            jobs.location,
            jobs.skills
        FROM applications
        JOIN jobs
        ON applications.job_id = jobs.id
        WHERE applications.candidate_id = ?
        ORDER BY applications.applied_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "my_applications.html",
        applications=applications,
        name=session.get(
            "user_name",
            "Candidate"
        )
    )


# =========================================================
# CANDIDATE - NOTIFICATIONS
# =========================================================

@app.route("/notifications")
def notifications():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get(
        "user_role",
        ""
    ).lower() != "candidate":

        return redirect(
            url_for("dashboard")
        )

    conn = get_db()

    notifications_list = conn.execute("""
        SELECT
            id,
            message,
            is_read,
            created_at
        FROM notifications
        WHERE candidate_id = ?
        ORDER BY created_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE candidate_id = ?
    """, (
        session["user_id"],
    ))

    conn.commit()

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications_list,
        name=session.get(
            "user_name",
            "Candidate"
        )
    )


# =========================================================
# INTERVIEW KEYWORDS
# =========================================================

INTERVIEW_KEYWORDS = {

    "python": [
        "programming",
        "language",
        "python",
        "simple",
        "easy",
        "development"
    ],

    "list_tuple": [
        "list",
        "tuple",
        "mutable",
        "immutable"
    ],

    "sql": [
        "database",
        "sql",
        "query",
        "data",
        "table"
    ],

    "html_css": [
        "html",
        "css",
        "structure",
        "style",
        "design"
    ],

    "machine_learning": [
        "machine learning",
        "data",
        "model",
        "prediction",
        "algorithm"
    ],

    "about": [
        "name",
        "education",
        "student",
        "skills",
        "project",
        "experience"
    ],

    "strengths": [
        "hardworking",
        "communication",
        "team",
        "learning",
        "problem",
        "leadership"
    ],

    "weaknesses": [
        "weakness",
        "improve",
        "improving",
        "learning",
        "time management"
    ],

    "hire": [
        "skills",
        "hardworking",
        "team",
        "learn",
        "contribute",
        "experience"
    ],

    "future": [
        "career",
        "skills",
        "learn",
        "growth",
        "company",
        "experience"
    ]

}


# =========================================================
# CHECK INTERVIEW ANSWER
# =========================================================

def check_interview_answer(
    question,
    answer
):

    answer_lower = answer.lower()

    question_lower = question.lower()

    if "python" in question_lower:

        keywords = INTERVIEW_KEYWORDS["python"]

    elif (
        "list" in question_lower
        and "tuple" in question_lower
    ):

        keywords = INTERVIEW_KEYWORDS["list_tuple"]

    elif "sql" in question_lower:

        keywords = INTERVIEW_KEYWORDS["sql"]

    elif (
        "html" in question_lower
        and "css" in question_lower
    ):

        keywords = INTERVIEW_KEYWORDS["html_css"]

    elif "machine learning" in question_lower:

        keywords = INTERVIEW_KEYWORDS[
            "machine_learning"
        ]

    elif "tell me about yourself" in question_lower:

        keywords = INTERVIEW_KEYWORDS["about"]

    elif "strength" in question_lower:

        keywords = INTERVIEW_KEYWORDS["strengths"]

    elif "weakness" in question_lower:

        keywords = INTERVIEW_KEYWORDS["weaknesses"]

    elif "hire" in question_lower:

        keywords = INTERVIEW_KEYWORDS["hire"]

    elif "five years" in question_lower:

        keywords = INTERVIEW_KEYWORDS["future"]

    else:

        keywords = []

    matched = 0

    for keyword in keywords:

        if keyword in answer_lower:

            matched += 1

    if not answer.strip():

        return 0

    if not keywords:

        if len(answer.split()) >= 8:

            return 1

        return 0

    if matched >= 2:

        return 1

    if (
        len(answer.split()) >= 8
        and matched >= 1
    ):

        return 1

    return 0


# =========================================================
# FALLBACK INTERVIEW QUESTIONS
# =========================================================

def generate_fallback_questions(
    resume_text,
    question_count=10,
    interview_type="resume",
    previous_questions=None,
    previous_answers=None
):

    resume_lower = resume_text.lower()

    previous_questions = previous_questions or []
    previous_answers = previous_answers or []

    questions = []

    # -----------------------------------------------------
    # DETECT SKILLS FROM RESUME
    # -----------------------------------------------------

    detected_skills = []

    for skill in SKILLS_LIST:

        if skill.lower() in resume_lower:

            detected_skills.append(skill)

    # -----------------------------------------------------
    # FOLLOW-UP QUESTIONS
    # -----------------------------------------------------

    if previous_answers:

        last_answer = previous_answers[-1].strip()

        if last_answer:

            last_question = ""

            if previous_questions:

                last_question = (
                    previous_questions[-1].lower()
                )

            if "project" in last_question:

                questions.append(
                    "Can you explain the main challenge you faced in that project and how you solved it?"
                )

            elif (
                "python" in last_question
                or "java" in last_question
                or "c++" in last_question
            ):

                questions.append(
                    "Can you describe a practical example where you used this technology and explain your contribution?"
                )

            elif "skill" in last_question:

                questions.append(
                    "Which of your technical skills are you most confident in, and how have you demonstrated that skill in a project?"
                )

            elif "experience" in last_question:

                questions.append(
                    "What was your main responsibility in that experience, and what did you learn from it?"
                )

            else:

                questions.append(
                    "Could you explain your previous answer in more detail and give a practical example from your experience?"
                )

    # -----------------------------------------------------
    # TECHNICAL QUESTIONS
    # -----------------------------------------------------

    if interview_type == "technical":

        for skill in detected_skills:

            skill_lower = skill.lower()

            if skill_lower == "python":

                questions.append(
                    "What is Python, and why did you choose Python for your projects?"
                )

                questions.append(
                    "Can you explain an important Python concept that you used in your project?"
                )

            elif skill_lower == "java":

                questions.append(
                    "What are the main features of Java, and how have you used Java in your projects?"
                )

            elif skill_lower == "c++":

                questions.append(
                    "What are the important concepts of C++ that you have used in your projects?"
                )

            elif skill_lower == "sql":

                questions.append(
                    "How did you use SQL or databases in your project?"
                )

                questions.append(
                    "What is the difference between a primary key and a foreign key in SQL?"
                )

            elif skill_lower == "html":

                questions.append(
                    "How did you use HTML to structure your web application?"
                )

            elif skill_lower == "css":

                questions.append(
                    "How did you use CSS to make your application responsive and user-friendly?"
                )

            elif skill_lower == "javascript":

                questions.append(
                    "How did you use JavaScript to add functionality to your web application?"
                )

            elif skill_lower == "flask":

                questions.append(
                    "Why did you choose Flask for your project, and how did you use it?"
                )

                questions.append(
                    "Can you explain how routing works in your Flask application?"
                )

            elif skill_lower == "machine learning":

                questions.append(
                    "What machine learning techniques have you used, and how were they applied in your project?"
                )

            elif skill_lower == "react":

                questions.append(
                    "How have you used React in your projects?"
                )

            elif skill_lower == "mongodb":

                questions.append(
                    "How did you use MongoDB and why was it suitable for your project?"
                )

            elif skill_lower == "git":

                questions.append(
                    "How did you use Git for version control during your project?"
                )

            elif skill_lower == "github":

                questions.append(
                    "How did you use GitHub for collaboration and project management?"
                )

    # -----------------------------------------------------
    # HR QUESTIONS
    # -----------------------------------------------------

    elif interview_type == "hr":

        questions.extend([

            "Tell me about yourself and your educational background.",

            "What are your strongest skills according to your resume?",

            "Can you describe one project from your resume that you are most proud of?",

            "What was your specific contribution to that project?",

            "What challenges did you face during your project and how did you overcome them?",

            "What are your strengths and weaknesses?",

            "Why should we hire you for this position?",

            "Where do you see yourself in the next five years?",

            "What are your career goals?",

            "Why are you interested in this role?"

        ])

    # -----------------------------------------------------
    # GENERAL RESUME QUESTIONS
    # -----------------------------------------------------

    else:

        questions.extend([

            "Tell me about yourself and your educational background.",

            "Can you explain the main project mentioned in your resume?",

            "What was your specific contribution to that project?",

            "What technical skills did you use in your project?",

            "What was the biggest challenge you faced while working on your project?",

            "How did you solve a difficult problem during your project?",

            "What did you learn from your project experience?",

            "Which skill mentioned in your resume are you most confident about?",

            "Can you describe your strengths and areas you want to improve?",

            "Why should we hire you?"

        ])

    # -----------------------------------------------------
    # SKILL-SPECIFIC QUESTIONS
    # -----------------------------------------------------

    for skill in detected_skills:

        if skill.lower() == "python":

            questions.append(
                "Can you explain how you used Python in your project?"
            )

        elif skill.lower() == "sql":

            questions.append(
                "Can you explain how SQL was used in your project?"
            )

        elif skill.lower() == "html":

            questions.append(
                "How did you use HTML while developing your project?"
            )

        elif skill.lower() == "css":

            questions.append(
                "How did you use CSS to improve the user interface?"
            )

        elif skill.lower() == "flask":

            questions.append(
                "How did Flask help you build the backend of your project?"
            )

        elif skill.lower() == "machine learning":

            questions.append(
                "How did you apply machine learning concepts in your project?"
            )

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    unique_questions = []

    previous_lower = [
        q.lower().strip()
        for q in previous_questions
    ]

    for question in questions:

        clean_question = question.strip()

        if not clean_question:

            continue

        if clean_question.lower() in [
            q.lower()
            for q in unique_questions
        ]:

            continue

        if clean_question.lower() in previous_lower:

            continue

        unique_questions.append(
            clean_question
        )

    # -----------------------------------------------------
    # GENERIC QUESTIONS
    # -----------------------------------------------------

    generic_questions = [

        "What is one important lesson you learned while working on your projects?",

        "How do you handle a difficult technical problem?",

        "How do you work effectively in a team?",

        "How do you keep improving your technical skills?",

        "What type of role are you looking for?",

        "What are your career goals?",

        "Why are you interested in this position?",

        "Why should we select you for this position?"

    ]

    for question in generic_questions:

        if len(unique_questions) >= question_count:

            break

        if question.lower() not in [
            q.lower()
            for q in unique_questions
        ]:

            if question.lower() not in previous_lower:

                unique_questions.append(
                    question
                )

    return unique_questions[:question_count]


# =========================================================
# GENERATE RESUME INTERVIEW QUESTIONS
# =========================================================

def generate_resume_interview_questions(
    resume_text,
    question_count=10,
    interview_type="resume",
    previous_questions=None,
    previous_answers=None
):

    resume_text = resume_text[:15000]

    previous_questions = previous_questions or []
    previous_answers = previous_answers or []

    conversation_context = ""

    if previous_questions and previous_answers:

        conversation_context = """
Previous interview questions and candidate answers:

"""

        for i in range(
            min(
                len(previous_questions),
                len(previous_answers)
            )
        ):

            conversation_context += (
                f"Question {i + 1}: "
                f"{previous_questions[i]}\n"
            )

            conversation_context += (
                f"Answer {i + 1}: "
                f"{previous_answers[i]}\n\n"
            )

    # -----------------------------------------------------
    # INTERVIEW TYPE
    # -----------------------------------------------------

    if interview_type == "technical":

        interview_instruction = """
Create technical interview questions based only on
technologies, programming languages, tools, frameworks,
databases, and projects mentioned in the resume.

Do not ask about technologies that are not present
in the resume.
"""

    elif interview_type == "hr":

        interview_instruction = """
Create HR interview questions using information from
the candidate's resume.

Focus on education, experience, projects, teamwork,
communication, strengths, weaknesses, career goals,
responsibilities, achievements, and motivation.
"""

    else:

        interview_instruction = """
Create detailed resume-based interview questions.

Focus on skills, projects, education, experience,
technologies, responsibilities, contributions,
challenges, achievements, and learning.
"""

    # -----------------------------------------------------
    # GEMINI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are an AI interviewer for HireSmart AI.

Candidate Resume:

-------------------------
{resume_text}
-------------------------

Interview Type:
{interview_type}

Number of Questions:
{question_count}

{interview_instruction}

IMPORTANT RULES:

1. Questions must be relevant to the candidate's resume.

2. For technical questions, only use technologies
   actually mentioned in the resume.

3. Questions should be suitable for a real job interview.

4. Do not repeat previous questions.

5. Ask follow-up questions when previous answers
   are available.

6. Follow-up questions should explore the candidate's
   previous answer in more depth.

7. Do not invent candidate experience.

8. Return ONLY a numbered list of questions.

{conversation_context}

Generate exactly {question_count} questions.
"""

    # -----------------------------------------------------
    # TRY GEMINI
    # -----------------------------------------------------

    result = ask_gemini(prompt)

    # -----------------------------------------------------
    # FALLBACK IF GEMINI FAILS
    # -----------------------------------------------------

    if not result:

        print("================================")
        print("USING FALLBACK INTERVIEW QUESTIONS")
        print("================================")

        return generate_fallback_questions(
            resume_text,
            question_count=question_count,
            interview_type=interview_type,
            previous_questions=previous_questions,
            previous_answers=previous_answers
        )

    # -----------------------------------------------------
    # PARSE GEMINI RESPONSE
    # -----------------------------------------------------

    questions = []

    for line in result.splitlines():

        line = line.strip()

        if not line:

            continue

        clean_line = line.lstrip("*- ")

        if (
            len(clean_line) >= 3
            and clean_line[0].isdigit()
        ):

            separator_position = -1

            for separator in [".", ")", "-"]:

                position = clean_line.find(
                    separator,
                    1
                )

                if position != -1:

                    separator_position = position

                    break

            if separator_position != -1:

                question = clean_line[
                    separator_position + 1:
                ].strip()

                if question:

                    questions.append(
                        question
                    )

    # -----------------------------------------------------
    # SECOND PARSER
    # -----------------------------------------------------

    if len(questions) < question_count:

        questions = []

        for line in result.splitlines():

            line = line.strip()

            if not line:

                continue

            line = line.lstrip(
                "0123456789.-) "
            ).strip()

            if "?" in line:

                questions.append(
                    line
                )

    # -----------------------------------------------------
    # INVALID GEMINI RESPONSE
    # -----------------------------------------------------

    if not questions:

        print("Gemini response could not be parsed.")
        print("Using fallback questions.")

        return generate_fallback_questions(
            resume_text,
            question_count=question_count,
            interview_type=interview_type,
            previous_questions=previous_questions,
            previous_answers=previous_answers
        )

    return questions[:question_count]


# =========================================================
# INTERVIEW SETUP
# =========================================================

@app.route(
    "/interview",
    methods=["GET", "POST"]
)
def interview():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    filename, filepath = get_latest_resume()

    # -----------------------------------------------------
    # SHOW INTERVIEW SETUP
    # -----------------------------------------------------

    if request.method == "GET":

        if not filepath:

            return render_template(
                "interview.html",
                filename=None,
                resume_uploaded=False,
                error="Please upload your resume before starting the interview."
            )

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
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
            error="Please upload your resume before starting the interview."
        )

    # -----------------------------------------------------
    # GET INTERVIEW SETTINGS
    # -----------------------------------------------------

    interview_type = request.form.get(
        "interview_type",
        "resume"
    )

    try:

        question_count = int(
            request.form.get(
                "question_count",
                10
            )
        )

    except (ValueError, TypeError):

        question_count = 10

    try:

        duration = int(
            request.form.get(
                "duration",
                30
            )
        )

    except (ValueError, TypeError):

        duration = 30

    # -----------------------------------------------------
    # VALIDATE SETTINGS
    # -----------------------------------------------------

    allowed_question_counts = [
        5,
        10,
        15,
        20
    ]

    allowed_durations = [
        10,
        15,
        30,
        45,
        60
    ]

    allowed_interview_types = [
        "resume",
        "technical",
        "hr"
    ]

    if question_count not in allowed_question_counts:

        question_count = 10

    if duration not in allowed_durations:

        duration = 30

    if interview_type not in allowed_interview_types:

        interview_type = "resume"

    # -----------------------------------------------------
    # EXTRACT RESUME TEXT
    # -----------------------------------------------------

    try:

        resume_text = extract_resume_text(
            filepath
        )

    except Exception as error:

        print(
            "RESUME EXTRACTION ERROR:",
            error
        )

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error="Unable to read your resume."
        )

    if not resume_text or not resume_text.strip():

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error="Unable to extract text from your resume."
        )

    # -----------------------------------------------------
    # GENERATE FIRST QUESTION
    #
    # Gemini is tried automatically.
    # If Gemini fails or quota is exceeded,
    # fallback questions are used.
    # -----------------------------------------------------

    questions = generate_resume_interview_questions(
        resume_text,
        question_count=1,
        interview_type=interview_type
    )

    if not questions:

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error="Unable to generate interview questions. Please try again."
        )

    # -----------------------------------------------------
    # START INTERVIEW SESSION
    # -----------------------------------------------------

    session["interview_questions"] = questions

    session["interview_answers"] = []

    session["interview_scores"] = []

    session["interview_index"] = 0

    session["interview_score"] = 0

    session["interview_total"] = question_count

    session["interview_type"] = interview_type

    session["interview_duration"] = duration

    session["interview_start_time"] = time.time()

    session["interview_time_expired"] = False

    # -----------------------------------------------------
    # GO TO FIRST QUESTION
    # -----------------------------------------------------

    return redirect(
        url_for("interview_question")
    )


# =========================================================
# INTERVIEW QUESTION
# =========================================================

@app.route(
    "/interview/question",
    methods=["GET", "POST"]
)
def interview_question():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

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

    total = session.get(
        "interview_total",
        10
    )

    interview_type = session.get(
        "interview_type",
        "resume"
    )

    duration = session.get(
        "interview_duration",
        30
    )

    start_time = session.get(
        "interview_start_time"
    )

    # -----------------------------------------------------
    # CHECK INTERVIEW DATA
    # -----------------------------------------------------

    if not questions or start_time is None:

        return redirect(
            url_for("interview")
        )

    # -----------------------------------------------------
    # CALCULATE REMAINING TIME
    # -----------------------------------------------------

    elapsed_seconds = (
        time.time() - start_time
    )

    total_seconds = (
        duration * 60
    )

    remaining_seconds = max(
        0,
        int(
            total_seconds -
            elapsed_seconds
        )
    )

    # -----------------------------------------------------
    # TIME EXPIRED
    # -----------------------------------------------------

    if remaining_seconds <= 0:

        session[
            "interview_time_expired"
        ] = True

        return redirect(
            url_for("interview_result")
        )

    # -----------------------------------------------------
    # QUESTION LIMIT
    # -----------------------------------------------------

    if index >= total:

        return redirect(
            url_for("interview_result")
        )

    # -----------------------------------------------------
    # CURRENT QUESTION
    # -----------------------------------------------------

    question = questions[index]

    # -----------------------------------------------------
    # SUBMIT ANSWER
    # -----------------------------------------------------

    if request.method == "POST":

        answer = request.form.get(
            "answer",
            ""
        ).strip()

        browser_time_expired = request.form.get(
            "time_expired",
            "0"
        )

        if browser_time_expired == "1":

            session[
                "interview_time_expired"
            ] = True

        # -------------------------------------------------
        # CHECK SERVER TIME
        # -------------------------------------------------

        elapsed_seconds = (
            time.time() - start_time
        )

        remaining_seconds = max(
            0,
            int(
                total_seconds -
                elapsed_seconds
            )
        )

        # -------------------------------------------------
        # TIME EXPIRED
        # -------------------------------------------------

        if remaining_seconds <= 0:

            session[
                "interview_time_expired"
            ] = True

            if answer:

                score = check_interview_answer(
                    question,
                    answer
                )

                answers.append(
                    answer
                )

                scores.append(
                    score
                )

                session[
                    "interview_answers"
                ] = answers

                session[
                    "interview_scores"
                ] = scores

                session[
                    "interview_score"
                ] = sum(scores)

            return redirect(
                url_for("interview_result")
            )

        # -------------------------------------------------
        # EMPTY ANSWER
        # -------------------------------------------------

        if not answer:

            return render_template(
                "interview_question.html",
                question=question,
                number=index + 1,
                total=total,
                remaining_seconds=remaining_seconds,
                duration=duration,
                interview_type=interview_type,
                error="Please enter an answer before continuing."
            )

        # -------------------------------------------------
        # CHECK ANSWER
        # -------------------------------------------------

        score = check_interview_answer(
            question,
            answer
        )

        answers.append(
            answer
        )

        scores.append(
            score
        )

        session[
            "interview_answers"
        ] = answers

        session[
            "interview_scores"
        ] = scores

        session[
            "interview_score"
        ] = sum(scores)

        # -------------------------------------------------
        # MOVE TO NEXT QUESTION
        # -------------------------------------------------

        index += 1

        session[
            "interview_index"
        ] = index

        # -------------------------------------------------
        # QUESTION LIMIT REACHED
        # -------------------------------------------------

        if index >= total:

            return redirect(
                url_for("interview_result")
            )

        # -------------------------------------------------
        # GET LATEST RESUME
        # -------------------------------------------------

        filename, filepath = get_latest_resume()

        if not filepath:

            return redirect(
                url_for("interview_result")
            )

        # -------------------------------------------------
        # EXTRACT RESUME TEXT
        # -------------------------------------------------

        try:

            resume_text = extract_resume_text(
                filepath
            )

        except Exception as error:

            print(
                "RESUME EXTRACTION ERROR:",
                error
            )

            return redirect(
                url_for("interview_result")
            )

        if not resume_text or not resume_text.strip():

            return redirect(
                url_for("interview_result")
            )

        # -------------------------------------------------
        # GENERATE FOLLOW-UP QUESTION
        #
        # Gemini is tried first.
        # If quota is exceeded, fallback logic is used.
        # -------------------------------------------------

        previous_questions = questions

        previous_answers = answers

        next_questions = (
            generate_resume_interview_questions(
                resume_text,
                question_count=1,
                interview_type=interview_type,
                previous_questions=previous_questions,
                previous_answers=previous_answers
            )
        )

        # -------------------------------------------------
        # ADD NEXT QUESTION
        # -------------------------------------------------

        if next_questions:

            questions.append(
                next_questions[0]
            )

            session[
                "interview_questions"
            ] = questions

        else:

            return redirect(
                url_for("interview_result")
            )

        # -------------------------------------------------
        # CALCULATE REMAINING TIME
        # -------------------------------------------------

        remaining_seconds = max(
            0,
            int(
                total_seconds -
                (
                    time.time() -
                    start_time
                )
            )
        )

        # -------------------------------------------------
        # CHECK TIME AGAIN
        # -------------------------------------------------

        if remaining_seconds <= 0:

            session[
                "interview_time_expired"
            ] = True

            return redirect(
                url_for("interview_result")
            )

        return redirect(
            url_for("interview_question")
        )

    # -----------------------------------------------------
    # DISPLAY CURRENT QUESTION
    # -----------------------------------------------------

    return render_template(
        "interview_question.html",
        question=question,
        number=index + 1,
        total=total,
        remaining_seconds=remaining_seconds,
        duration=duration,
        interview_type=interview_type,
        error=None
    )


# =========================================================
# INTERVIEW RESULT
# =========================================================

@app.route("/interview/result")
def interview_result():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    score = session.get(
        "interview_score",
        0
    )

    total = session.get(
        "interview_total",
        0
    )

    answers = session.get(
        "interview_answers",
        []
    )

    try:

        score = int(score)

        total = int(total)

    except (
        ValueError,
        TypeError
    ):

        score = 0

        total = 0

    # -----------------------------------------------------
    # USE ANSWERED QUESTIONS FOR RESULT
    # -----------------------------------------------------

    answered_count = len(answers)

    if answered_count > 0:

        percentage = int(
            (score / answered_count) * 100
        )

    else:

        percentage = 0

    if percentage >= 80:

        message = "Excellent Performance! 🎉"

    elif percentage >= 60:

        message = "Good Performance! 👍"

    elif percentage >= 40:

        message = "Keep Practicing! 💪"

    else:

        message = "You Need More Practice. 📚"

    return render_template(
        "interview_result.html",
        name=session.get(
            "user_name",
            "Candidate"
        ),
        score=score,
        total=total,
        percentage=percentage,
        message=message
    )


# =========================================================
# TEST GEMINI
# =========================================================

@app.route("/test_gemini")
def test_gemini():

    if not gemini_client:

        return """
        <h1>Gemini Test</h1>

        <p>
        Gemini API key is not configured.
        </p>

        <p>
        Add GEMINI_API_KEY in Render Environment Variables.
        </p>

        <p>
        The interview can still use fallback questions.
        </p>
        """

    result = ask_gemini(
        "Say hello to HireSmart AI in one sentence."
    )

    if not result:

        return """
        <h1>Gemini Test Failed</h1>

        <p>
        Gemini returned an error or quota limit was reached.
        </p>

        <p>
        The interview system will use fallback questions.
        </p>

        <hr>

        <a href="/interview">
            Start Resume Interview
        </a>
        """

    return f"""
    <h1>Gemini Test Successful</h1>

    <p>{result}</p>

    <hr>

    <a href="/interview">
        Start Resume Interview
    </a>
    """


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
# INITIALIZE DATABASE
# =========================================================

create_table()


# =========================================================
# SHOW REGISTERED ROUTES
# =========================================================

print("================================")
print("REGISTERED FLASK ROUTES")
print(app.url_map)
print("================================")


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=False
    )