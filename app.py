from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

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


if (
    GEMINI_API_KEY
    and GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE"
):

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
    print("================================")


# =========================================================
# ASK GEMINI
# =========================================================

def ask_gemini(prompt):

    if gemini_client is None:

        print("================================")
        print("Gemini client is not initialized.")
        print("Check your GEMINI_API_KEY.")
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

            print(
                "Full Gemini response:",
                response
            )

            return ""

        print("================================")
        print("GEMINI SUCCESS")
        print("RESPONSE:")
        print(result)
        print("================================")

        return result.strip()

    except Exception as error:

        print("================================")
        print("GEMINI ERROR")
        print("TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("DETAIL:", repr(error))
        print("================================")

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
# GENERATE INTERVIEW QUESTIONS
# =========================================================

def generate_resume_interview_questions(
    resume_text
):

    resume_text = resume_text[:15000]

    prompt = f"""
You are an AI interviewer for HireSmart AI.

Read the candidate's resume below and create interview questions
based ONLY on information present in the resume.

Resume:

-------------------------

{resume_text}

-------------------------

Create exactly 5 interview questions.

The questions should include:

1. One question about the candidate's skills.

2. One question about a project mentioned in the resume.

3. One question about education or experience if available.

4. One technical question related to a technology actually mentioned in the resume.

5. One question about the candidate's role, contribution, or learning.

Do not ask about technologies that are not mentioned in the resume.

Return ONLY the questions as a numbered list.

Example:

1. What is your experience with Python?

2. Explain the project mentioned in your resume.

3. How did you use SQL in your project?

4. What challenges did you face?

5. What was your contribution to the project?
"""

    result = ask_gemini(prompt)

    if not result:

        return []

    questions = []

    for line in result.split("\n"):

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

    if len(questions) < 5:

        questions = []

        for line in result.splitlines():

            line = line.strip()

            if not line:

                continue

            line = line.lstrip(
                "0123456789.-) "
            ).strip()

            if "?" in line:

                questions.append(line)

    return questions[:5]


# =========================================================
# START INTERVIEW
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

    if request.method == "GET":

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=bool(filepath),
            error=None
        )

    if not filepath:

        return render_template(
            "interview.html",
            filename=None,
            resume_uploaded=False,
            error="Please upload your resume first."
        )

    print("================================")
    print("STARTING RESUME INTERVIEW")
    print("Resume:", filename)
    print("Path:", filepath)
    print(
        "Exists:",
        os.path.exists(filepath)
    )
    print("================================")

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
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error="Could not read your resume."
        )

    if not resume_text.strip():

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error=(
                "Your resume does not contain "
                "readable text."
            )
        )

    print(
        "Resume text extracted successfully."
    )

    print(
        "Resume text length:",
        len(resume_text)
    )

    if not gemini_client:

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error=(
                "Gemini AI is not configured. "
                "Please add your Gemini API key "
                "in Render Environment Variables."
            )
        )

    questions = generate_resume_interview_questions(
        resume_text
    )

    if not questions:

        return render_template(
            "interview.html",
            filename=filename,
            resume_uploaded=True,
            error=(
                "Gemini could not generate interview "
                "questions. Please check the Render "
                "logs for the exact Gemini error."
            )
        )

    print(
        "Generated questions:",
        questions
    )

    session["interview_questions"] = questions

    session["interview_answers"] = []

    session["interview_scores"] = []

    session["interview_index"] = 0

    session["interview_score"] = 0

    session["interview_total"] = len(
        questions
    )

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

    if not questions:

        return redirect(
            url_for("interview")
        )

    if index >= len(questions):

        return redirect(
            url_for("interview_result")
        )

    if request.method == "POST":

        answer = request.form.get(
            "answer",
            ""
        ).strip()

        if not answer:

            return render_template(
                "interview_question.html",
                question=questions[index],
                number=index + 1,
                total=len(questions),
                error="Please enter your answer."
            )

        answer_score = check_interview_answer(
            questions[index],
            answer
        )

        answers.append(answer)

        scores.append(answer_score)

        session["interview_answers"] = answers

        session["interview_scores"] = scores

        session["interview_score"] = sum(
            scores
        )

        session["interview_index"] = (
            index + 1
        )

        if index + 1 >= len(questions):

            return redirect(
                url_for("interview_result")
            )

        return redirect(
            url_for("interview_question")
        )

    return render_template(
        "interview_question.html",
        question=questions[index],
        number=index + 1,
        total=len(questions)
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

    try:

        score = int(score)

        total = int(total)

    except (
        ValueError,
        TypeError
    ):

        score = 0

        total = 0

    if total > 0:

        percentage = int(
            (score / total) * 100
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
        """

    result = ask_gemini(
        "Say hello to HireSmart AI in one sentence."
    )

    if not result:

        return """
        <h1>Gemini Test Failed</h1>

        <p>
        Gemini returned an error.
        </p>

        <p>
        Check the Render logs for the exact
        Gemini error message.
        </p>
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
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )