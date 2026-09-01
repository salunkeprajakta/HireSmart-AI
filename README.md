
# 🤖 HireSmart AI – AI-Powered Recruitment & Candidate Management Platform

HireSmart AI is an AI-powered web-based recruitment platform designed to simplify and improve the hiring process for both candidates and recruiters.

The platform provides separate candidate and recruiter dashboards and combines resume processing, skill analysis, job matching, job applications, candidate management, notifications, and Google Gemini AI-powered interviews into a single recruitment system.

---

# 🏗️ System Architecture

HireSmart AI follows a web-based client-server architecture where the Flask backend handles application logic, authentication, resume processing, job management, and AI-powered functionality. SQLite is used for storing application data, while Google Gemini AI provides intelligent interview question generation.

```text
                         ┌──────────────────────────┐
                         │          USERS           │
                         │                          │
                         │ Candidates / Recruiters  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │          FLASK WEB APP          │
                    │                                 │
                    │ • Authentication                │
                    │ • Candidate Dashboard           │
                    │ • Recruiter Dashboard           │
                    │ • Profile Management            │
                    │ • Job Management                │
                    │ • Resume Processing             │
                    │ • Applications                 │
                    │ • Notifications                │
                    │ • AI Interview                 │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌───────────────────┐         ┌──────────────────────┐
          │    SQLITE DB      │         │     AI PROCESSING    │
          │                   │         │                      │
          │ • Users           │         │ • Resume Analysis    │
          │ • Jobs            │         │ • Skill Analysis     │
          │ • Applications    │         │ • Interview Questions│
          │ • Notifications   │         │ • Answer Evaluation  │
          └─────────┬─────────┘         └──────────┬───────────┘
                    │                              │
                    │                              ▼
                    │                   ┌──────────────────────┐
                    │                   │    GOOGLE GEMINI AI  │
                    │                   │                      │
                    │                   │ • AI Questions       │
                    │                   │ • Resume Context     │
                    │                   │ • Interview Support  │
                    │                   └──────────────────────┘
                    │
                    ▼
          ┌───────────────────────┐
          │    APPLICATION DATA  │
          │                       │
          │ • Candidate Profiles  │
          │ • Recruiter Profiles  │
          │ • Jobs                │
          │ • Applications        │
          │ • Notifications       │
          └───────────────────────┘
````

---

# 🔄 Architecture Flow

1. The user accesses the HireSmart AI web application.
2. Users register and log in as either a Candidate or Recruiter.
3. Flask manages authentication and role-based access.
4. Candidates can create profiles and upload resumes.
5. Resume files are processed and their text is extracted.
6. The application performs resume and skill analysis.
7. Candidate skills are used for job matching and recommendations.
8. Candidates can apply for available jobs and track applications.
9. Recruiters can post jobs and manage candidates and applications.
10. Notifications are generated for application status updates.
11. Candidates can start an AI-powered interview using information from their resume.
12. Google Gemini AI generates personalized interview questions.
13. Candidate answers are evaluated and an interview score/result is displayed.

---

# 📌 Problem Statement

Traditional recruitment processes can require significant manual effort for both candidates and recruiters.

Candidates may have difficulty understanding the skills present in their resumes, identifying missing skills, finding suitable jobs, and preparing for interviews.

Recruiters may need to manually review candidate information, manage job applications, and evaluate candidates.

HireSmart AI addresses these challenges by providing a centralized recruitment platform with resume analysis, skill detection, job matching, application management, candidate management, and AI-powered interview functionality.

---

# ✨ Key Features

## 👩‍🎓 Candidate Features

### 🔐 Candidate Authentication

* Candidate registration
* Candidate login
* Session-based authentication
* Logout functionality

### 👤 Candidate Profile

Candidates can manage profile information including:

* Name
* Email
* Phone
* Education
* Skills
* Experience

### 📄 Resume Upload

Candidates can upload resumes for analysis.

Supported formats:

* PDF
* DOCX

### 📝 Resume Analysis

The platform extracts text from uploaded resumes and performs analysis.

Features include:

* Resume text extraction
* Resume scoring
* Skill identification
* Missing skill identification
* Resume improvement suggestions

### 🧠 Skill Analysis

The system analyzes the extracted resume text and identifies relevant technical and soft skills.

Examples include:

* Python
* Java
* C++
* HTML
* CSS
* JavaScript
* SQL
* Flask
* Django
* Machine Learning
* Data Science
* Git
* GitHub
* React
* Node.js
* MongoDB
* Power BI
* Communication
* Leadership

### 💼 Job Search & Recommendations

Candidates can:

* Browse available jobs
* View job requirements
* Check skill matching
* Receive job recommendations
* Apply for suitable jobs

### 📋 Job Applications

Candidates can:

* Apply for jobs
* View submitted applications
* Track application status
* Receive notifications

### 🔔 Notifications

Candidates can receive notifications related to their job applications.

### 🎤 AI-Powered Interview

Candidates can attend an AI-powered interview based on their uploaded resume.

The system:

* Uses resume information
* Generates personalized questions
* Collects candidate answers
* Evaluates answers
* Calculates an interview score
* Displays the final result

---

# 👨‍💼 Recruiter Features

## 🔐 Recruiter Authentication

Recruiters can:

* Register
* Login
* Logout

## 📊 Recruiter Dashboard

The recruiter dashboard provides access to recruitment-related functionality.

## 💼 Job Posting

Recruiters can create job opportunities containing information such as:

* Job title
* Company
* Location
* Required skills
* Job description

## 📋 Job Management

Recruiters can:

* View posted jobs
* Manage job opportunities

## 👥 Candidate Management

Recruiters can view available candidates and review information such as:

* Candidate name
* Skills
* Education
* Experience
* Contact information

## 📑 Application Management

Recruiters can review candidate applications and update application status.

Supported actions include:

* Shortlist candidate
* Reject candidate

---

# 🧠 AI Features

HireSmart AI integrates **Google Gemini AI** for AI-powered interview functionality.

## 🎤 Resume-Based Interview Questions

The candidate's resume is used as the context for generating interview questions.

The system can generate questions related to:

* Skills
* Projects
* Education
* Experience
* Technologies
* Candidate contributions
* Learning

The AI interview process is designed to create questions relevant to the candidate's resume instead of asking unrelated questions.

## 🔄 AI Interview Flow

```text
Candidate Resume
       ↓
Resume Text Extraction
       ↓
Resume Analysis
       ↓
Resume Context
       ↓
Google Gemini AI
       ↓
Personalized Interview Questions
       ↓
Candidate Answers
       ↓
Answer Evaluation
       ↓
Interview Score
       ↓
Interview Result
```

---

# 📄 Resume Processing

HireSmart AI supports resume processing for PDF and DOCX files.

## PDF

PDF text is extracted using the PyPDF library.

## DOCX

DOCX text is extracted using the python-docx library.

## Resume Processing Flow

```text
Upload Resume
      ↓
Validate File
      ↓
Save Resume
      ↓
Extract Text
      ↓
Analyze Resume
      ↓
Detect Skills
      ↓
Identify Missing Skills
      ↓
Generate Resume Suggestions
```

---

# 💼 Job Matching

HireSmart AI uses candidate skills to calculate compatibility with job requirements.

For example:

```text
Candidate Skills:
Python
Flask
SQL
Git

Required Skills:
Python
Flask
SQL
Git

Match:
100%
```

The matching process helps candidates discover jobs that better correspond to their skills.

---

# 🧩 How HireSmart AI Works

### Candidate Flow

```text
Register
   ↓
Login
   ↓
Candidate Dashboard
   ↓
Complete Profile
   ↓
Upload Resume
   ↓
Resume Analysis
   ↓
Skill Analysis
   ↓
Browse / Recommended Jobs
   ↓
Apply for Job
   ↓
Track Application
   ↓
AI Interview
   ↓
Interview Result
```

### Recruiter Flow

```text
Register
   ↓
Login
   ↓
Recruiter Dashboard
   ↓
Create Job
   ↓
Manage Jobs
   ↓
View Candidates
   ↓
Review Applications
   ↓
Shortlist / Reject
   ↓
Candidate Notification
```

---

# 🛠️ Technology Stack

| Technology       | Purpose                                   |
| ---------------- | ----------------------------------------- |
| Python           | Backend programming                       |
| Flask            | Web application framework                 |
| HTML             | Frontend structure                        |
| CSS              | User interface styling                    |
| JavaScript       | Frontend interactivity                    |
| SQLite           | Database management                       |
| SQL              | Database queries                          |
| Google Gemini AI | AI-powered interview functionality        |
| PyPDF            | PDF resume text extraction                |
| python-docx      | DOCX resume text extraction               |
| Werkzeug         | Password hashing and secure file handling |

---

# 📂 Project Structure

```text
HireSmart-AI/
│
├── app.py
├── ai_matching.py
├── database.py
├── recommendation.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── ml/
│   └── resume_model.py
│
├── static/
│   └── style.css
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── candidate_dashboard.html
│   ├── recruiter_dashboard.html
│   ├── profile.html
│   ├── upload_resume.html
│   ├── upload_success.html
│   ├── resume_uploaded.html
│   ├── resume_analysis.html
│   ├── skill_analysis.html
│   ├── jobs.html
│   ├── post_job.html
│   ├── recruiter_jobs.html
│   ├── recruiter_candidates.html
│   ├── my_applications.html
│   ├── notifications.html
│   ├── interview.html
│   ├── interview_question.html
│   └── interview_result.html
│
└── uploads/
    └── .gitkeep
```

---

# 🗄️ Database

HireSmart AI uses **SQLite** for storing application data.

The main database tables are:

### Users

Stores candidate and recruiter information.

```text
users
├── id
├── name
├── email
├── password
├── role
├── phone
├── education
├── skills
└── experience
```

### Jobs

Stores recruiter-created job opportunities.

```text
jobs
├── id
├── recruiter_id
├── title
├── company
├── location
├── skills
├── description
└── created_at
```

### Applications

Stores candidate job applications.

```text
applications
├── id
├── job_id
├── candidate_id
├── status
└── applied_at
```

### Notifications

Stores candidate application notifications.

```text
notifications
├── id
├── candidate_id
├── application_id
├── message
├── is_read
└── created_at
```

---

# 🔌 Application Routes

## General Routes

| Method   | Endpoint    | Purpose                 |
| -------- | ----------- | ----------------------- |
| GET      | `/`         | Application entry point |
| GET/POST | `/register` | User registration       |
| GET/POST | `/login`    | User login              |
| GET      | `/logout`   | Logout                  |

## Candidate Routes

| Method   | Endpoint           | Purpose                     |
| -------- | ------------------ | --------------------------- |
| GET      | `/dashboard`       | Candidate dashboard         |
| GET/POST | `/profile`         | Candidate profile           |
| GET/POST | `/upload_resume`   | Resume upload               |
| GET      | `/resume_analysis` | Resume analysis             |
| GET      | `/skill_analysis`  | Skill analysis              |
| GET      | `/jobs`            | Job listing/recommendations |
| POST     | `/apply/<job_id>`  | Apply for job               |
| GET      | `/my_applications` | Application tracking        |
| GET      | `/notifications`   | Candidate notifications     |

## Recruiter Routes

| Method   | Endpoint                                           | Purpose                   |
| -------- | -------------------------------------------------- | ------------------------- |
| GET      | `/recruiter/dashboard`                             | Recruiter dashboard       |
| GET/POST | `/recruiter/post_job`                              | Create job                |
| GET      | `/recruiter/jobs`                                  | Recruiter jobs            |
| GET      | `/recruiter/candidates`                            | Candidate management      |
| POST     | `/recruiter/application/<application_id>/<status>` | Update application status |

## AI Interview Routes

| Method   | Endpoint              | Purpose                         |
| -------- | --------------------- | ------------------------------- |
| GET/POST | `/interview`          | Start interview                 |
| GET/POST | `/interview/question` | Interview questions and answers |
| GET      | `/interview/result`   | Interview result                |
| GET      | `/test_gemini`        | Test Gemini integration         |

---

# ⚙️ Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.x
* pip
* Git
* Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/prajakta033/HireSmart-AI.git
cd HireSmart-AI
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate Virtual Environment

### Windows

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Gemini API Configuration

The Gemini API key should **not** be stored directly inside the source code.

The application reads the API key from the environment.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Never upload:

```text
.env
API keys
Passwords
Secret credentials
```

to GitHub.

---

# ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

---

# 🧪 Testing

The major application workflows include:

### Candidate Testing

* Registration
* Login
* Profile management
* Resume upload
* PDF extraction
* DOCX extraction
* Resume analysis
* Skill analysis
* Job matching
* Job recommendations
* Job application
* Application tracking
* Notifications
* AI interview
* Interview questions
* Interview evaluation
* Interview result

### Recruiter Testing

* Registration
* Login
* Recruiter dashboard
* Job posting
* Job management
* Candidate viewing
* Application review
* Candidate shortlisting
* Candidate rejection

### Gemini Testing

The application provides a Gemini testing route:

```text
/test_gemini
```

which can be used to verify the Gemini AI connection.

---

# 🔐 Security

HireSmart AI follows basic security practices including:

* Password hashing using Werkzeug
* Secure uploaded filenames
* Session-based authentication
* Candidate/recruiter role checks
* Environment variables for API keys
* `.gitignore` protection for sensitive files
* Restricted handling of uploaded resumes

Sensitive information should never be committed to the public GitHub repository.

---

# 🎯 Project Objectives

The main objectives of HireSmart AI are:

1. To simplify the recruitment process.
2. To provide separate dashboards for candidates and recruiters.
3. To automate basic resume analysis.
4. To identify skills from candidate resumes.
5. To identify missing skills.
6. To recommend jobs based on candidate skills.
7. To allow candidates to apply for suitable jobs.
8. To help recruiters manage jobs and candidates.
9. To provide application status tracking and notifications.
10. To generate resume-based AI interview questions.
11. To evaluate interview performance.
12. To improve the efficiency of candidate screening and interview preparation.

---

# ✅ Current Implementation

The current project includes:

* Candidate authentication
* Recruiter authentication
* Candidate dashboard
* Recruiter dashboard
* Profile management
* Resume upload
* PDF resume processing
* DOCX resume processing
* Resume text extraction
* Resume analysis
* Skill detection
* Skill analysis
* Missing skill identification
* Job listing
* Skill-based job matching
* Job recommendations
* Job applications
* Application tracking
* Notifications
* Job posting
* Candidate management
* Application status management
* Candidate shortlisting
* Candidate rejection
* Google Gemini AI integration
* AI interview question generation
* Resume-based interview
* Interview answer evaluation
* Interview score
* Interview result

---

# 🚀 Future Enhancements

Possible future improvements include:

* Advanced AI candidate ranking
* Advanced candidate-job matching
* Personalized job recommendation system
* Advanced recruiter analytics
* Email notifications
* Interview scheduling
* Improved AI interview evaluation
* Admin dashboard
* Advanced candidate filtering
* Cloud deployment
* More advanced resume scoring
* AI-generated interview feedback
* Improved candidate ranking algorithms

---

# 🌟 Why HireSmart AI?

HireSmart AI combines recruitment management with resume intelligence and generative AI.

Candidates can:

* Analyze their resumes
* Understand their skills
* Identify missing skills
* Discover suitable jobs
* Apply for jobs
* Prepare through AI-powered interviews
* View interview performance

Recruiters can:

* Post jobs
* Manage job opportunities
* View candidates
* Review applications
* Shortlist candidates
* Reject candidates
* Manage the recruitment process

This provides a single platform for important candidate and recruiter activities.

---

# 📚 Academic Purpose

HireSmart AI is developed as an academic software project to demonstrate the practical application of:

* Python programming
* Flask web development
* Database management
* SQL
* Resume processing
* Skill detection
* Job matching
* Web application development
* Generative AI
* Recruitment management

---

# 👩‍💻 Author

**Prajakta Salunke**

**Project:** HireSmart AI – AI-Powered Recruitment & Candidate Management Platform

---

# 📄 License

This project is developed for educational and academic purposes.

