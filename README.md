# 🤖 HireSmart AI – AI-Powered Recruitment & Candidate Management Platform

HireSmart AI is an AI-powered web-based recruitment and candidate management platform designed to simplify and improve the hiring process for both candidates and recruiters.

The platform provides separate dashboards for candidates and recruiters and combines authentication, profile management, resume processing, resume analysis, skill analysis, job matching, job applications, notifications, candidate management, and AI-powered interviews into a single recruitment system.

---

# ✨ Key Features

## 👩‍🎓 Candidate Features

### 🔐 Authentication

Candidates can:

* Register an account
* Login securely
* Logout
* Use session-based authentication
* Access forgot-password functionality

---

### 👤 Candidate Profile

Candidates can manage their profile information, including:

* Name
* Email
* Phone
* Education
* Skills
* Experience

---

### 📄 Resume Upload

Candidates can upload resumes for analysis.

**Supported formats:**

* PDF
* DOCX

The uploaded resume is processed and analyzed by the application.

---

### 📝 Resume Analysis

HireSmart AI extracts and analyzes resume content.

Features include:

* Resume text extraction
* Resume scoring
* Skill identification
* Missing skill identification
* Resume improvement suggestions

---

### 🧠 Skill Analysis

The system identifies technical and soft skills from candidate resumes.

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
* Excel
* Communication
* Leadership
* Git
* GitHub
* React
* Node.js
* MongoDB
* Power BI

---

### 💼 Job Search & Recommendations

Candidates can:

* Browse available jobs
* View job requirements
* Check skill matching
* Receive skill-based job recommendations
* Apply for suitable jobs

---

### 📋 Job Applications

Candidates can:

* Apply for jobs
* View submitted applications
* Track application status
* Receive notifications about application updates

---

### 🔔 Notifications

Candidates receive notifications related to their job applications.

Examples include:

* Application updates
* Shortlisting
* Rejection
* Recruitment status changes

---

# 🎤 AI-Powered Interview

HireSmart AI provides an AI-powered interview system using Google Gemini AI.

The interview system uses information from the candidate's resume to generate relevant interview questions.

---

## ⚙️ Interview Configuration

The interview can be configured according to the candidate's requirements.

### Question Count

Available options:

* 10 questions
* 20 questions
* 30 questions

### Interview Duration

Available options:

* 15 minutes
* 20 minutes
* 30 minutes

### Interview Types

The system supports:

* HR Interview
* Technical Interview

---

## 📄 Resume-Based Interview Questions

The AI uses information from the candidate's resume as context.

Questions can be generated around:

* Skills
* Projects
* Education
* Experience
* Technologies
* Candidate contributions
* Learning
* Achievements

This helps create personalized interview questions instead of relying only on generic questions.

---

## 🔄 Adaptive Follow-Up Questions

The interview system can generate follow-up questions based on the candidate's previous answers and resume information.

### Interview Flow

```text
Candidate Resume
       ↓
Interview Type
       ↓
Initial Question
       ↓
Candidate Answer
       ↓
Previous Answer Analysis
       ↓
Follow-Up Question
       ↓
Next Question
       ↓
Final Evaluation
```

This makes the interview more interactive and personalized.

---

## ⏱️ Interview Timer

The interview includes a visible countdown timer based on the selected duration.

The timer:

* Displays the remaining interview time
* Updates continuously
* Warns the candidate when time is running low
* Automatically submits the interview when the time expires
* Prevents the interview from continuing after the time limit

---

## 📊 Interview Result

After completing the interview or when the time expires, the candidate receives:

* Interview score
* Performance percentage
* Performance feedback
* Final interview result

### Interview Completion Flow

```text
Interview Started
       ↓
Questions & Answers
       ↓
Timer Running
       ↓
Time Limit Reached
       ↓
Automatic Submission
       ↓
Interview Result
```

---

# 🧠 AI Features

HireSmart AI integrates **Google Gemini AI** for personalized interview functionality.

### AI Capabilities

* Resume-based interview question generation
* Detailed interview questions
* Technical interview questions
* HR interview questions
* Adaptive follow-up questions
* Resume-context-aware questioning
* Interview answer evaluation
* Interview performance analysis

---

# 🔄 AI Interview Architecture

```text
                  Candidate Resume
                         ↓
                Resume Text Extraction
                         ↓
                  Resume Information
                         ↓
                  Interview Settings
              ┌──────────┼───────────┐
              ↓          ↓           ↓
          Question     Duration    Interview
           Count                    Type
              └──────────┼───────────┘
                         ↓
                  Google Gemini AI
                         ↓
              Personalized Questions
                         ↓
                  Candidate Answer
                         ↓
                 Answer Evaluation
                         ↓
               Adaptive Follow-Up
                         ↓
                  Next Question
                         ↓
                  Interview Complete
                         ↓
                Final Score & Result
```

---

# 📄 Resume Processing

HireSmart AI supports resume processing for both PDF and DOCX files.

## PDF Resume Processing

PDF resume text is extracted using the **PyPDF** library.

## DOCX Resume Processing

DOCX resume text is extracted using the **python-docx** library.

### Resume Processing Flow

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
Generate Suggestions
```

---

# 💼 Job Matching

HireSmart AI calculates job compatibility based on candidate skills and required job skills.

### Example

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

The matching system helps candidates discover jobs that better correspond to their existing skills.

---

# 👨‍💼 Recruiter Features

## 🔐 Recruiter Authentication

Recruiters can:

* Register
* Login
* Logout

---

## 📊 Recruiter Dashboard

The recruiter dashboard provides access to recruitment-related functionality.

Recruiters can manage jobs, candidates, and applications from the dashboard.

---

## 💼 Job Posting

Recruiters can create job opportunities containing:

* Job title
* Company
* Location
* Required skills
* Job description

---

## 📋 Job Management

Recruiters can:

* View posted jobs
* Manage job opportunities

---

## 👥 Candidate Management

Recruiters can view candidate information such as:

* Candidate name
* Skills
* Education
* Experience
* Contact information

---

## 📑 Application Management

Recruiters can review candidate applications and update their status.

Supported actions include:

* Shortlist candidate
* Reject candidate

Candidates receive notifications when their application status changes.

---

# 🔄 Application Workflow

## 👩‍🎓 Candidate Workflow

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

---

## 👨‍💼 Recruiter Workflow

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

# 🏗️ System Architecture

HireSmart AI follows a web-based client-server architecture.

```text
                    ┌──────────────────────────┐
                    │          USERS           │
                    │                          │
                    │ Candidates / Recruiters  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       FLASK WEB APP      │
                    │                          │
                    │ Authentication           │
                    │ Candidate Dashboard      │
                    │ Recruiter Dashboard      │
                    │ Profile Management       │
                    │ Job Management           │
                    │ Resume Processing        │
                    │ Applications             │
                    │ Notifications            │
                    │ AI Interview             │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 │                                │
                 ▼                                ▼
       ┌───────────────────┐          ┌─────────────────────┐
       │     SQLITE DB     │          │    AI PROCESSING    │
       │                   │          │                     │
       │ Users             │          │ Resume Analysis     │
       │ Jobs              │          │ Skill Analysis      │
       │ Applications      │          │ Interview Questions │
       │ Notifications     │          │ Answer Evaluation   │
       └───────────────────┘          └──────────┬──────────┘
                                                 │
                                                 ▼
                                      ┌─────────────────────┐
                                      │   GOOGLE GEMINI AI  │
                                      │                     │
                                      │ AI Questions        │
                                      │ Resume Context      │
                                      │ Interview Support   │
                                      └─────────────────────┘
```

---

# 🛠️ Technology Stack

| Technology       | Purpose                                    |
| ---------------- | ------------------------------------------ |
| Python           | Backend programming                        |
| Flask            | Web application framework                  |
| HTML             | Frontend structure                         |
| CSS              | User interface styling                     |
| JavaScript       | Frontend interactivity and interview timer |
| SQLite           | Database management                        |
| SQL              | Database queries                           |
| Google Gemini AI | AI-powered interview functionality         |
| PyPDF            | PDF resume text extraction                 |
| python-docx      | DOCX resume text extraction                |
| Werkzeug         | Password hashing and secure file handling  |

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
│   ├── interview_result.html
│   └── forgot_password.html
│
└── uploads/
    └── .gitkeep
```

---

# 🗄️ Database

HireSmart AI uses **SQLite** for storing application data.

## Users

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

## Jobs

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

## Applications

Stores candidate job applications.

```text
applications
├── id
├── job_id
├── candidate_id
├── status
└── applied_at
```

## Notifications

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

| Method   | Endpoint           | Purpose                 |
| -------- | ------------------ | ----------------------- |
| GET      | `/`                | Application entry point |
| GET/POST | `/register`        | User registration       |
| GET/POST | `/login`           | User login              |
| GET      | `/logout`          | Logout                  |
| GET      | `/forgot-password` | Forgot password         |

---

## Candidate Routes

| Method   | Endpoint           | Purpose                         |
| -------- | ------------------ | ------------------------------- |
| GET      | `/dashboard`       | Candidate dashboard             |
| GET/POST | `/profile`         | Candidate profile               |
| GET/POST | `/upload_resume`   | Resume upload                   |
| GET      | `/resume_analysis` | Resume analysis                 |
| GET      | `/skill_analysis`  | Skill analysis                  |
| GET      | `/jobs`            | Job listing and recommendations |
| POST     | `/apply/<job_id>`  | Apply for a job                 |
| GET      | `/my_applications` | Application tracking            |
| GET      | `/notifications`   | Candidate notifications         |

---

## Recruiter Routes

| Method   | Endpoint                                           | Purpose                   |
| -------- | -------------------------------------------------- | ------------------------- |
| GET      | `/recruiter/dashboard`                             | Recruiter dashboard       |
| GET/POST | `/recruiter/post_job`                              | Create job                |
| GET      | `/recruiter/jobs`                                  | Recruiter job management  |
| GET      | `/recruiter/candidates`                            | Candidate management      |
| POST     | `/recruiter/application/<application_id>/<status>` | Update application status |

---

## AI Interview Routes

| Method   | Endpoint              | Purpose                               |
| -------- | --------------------- | ------------------------------------- |
| GET/POST | `/interview`          | Configure and start interview         |
| GET/POST | `/interview/question` | Display questions and collect answers |
| GET      | `/interview/result`   | Display interview result              |
| GET      | `/test_gemini`        | Test Gemini AI integration            |

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
git clone https://github.com/salunkeprajakta/HireSmart-AI.git
cd HireSmart-AI
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate the Virtual Environment

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

The Gemini API key should never be stored directly inside the source code.

The application reads the key from the `GEMINI_API_KEY` environment variable.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Never upload the following to GitHub:

```text
.env
API keys
Passwords
Secret credentials
```

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

Open the address in your web browser.

---

# 🧪 Testing

## Candidate Testing

Major candidate workflows include:

* Registration
* Login
* Forgot password
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
* Configurable interview questions
* Interview timer
* Resume-based questions
* Follow-up questions
* Interview evaluation
* Interview result

---

## Recruiter Testing

Major recruiter workflows include:

* Registration
* Login
* Recruiter dashboard
* Job posting
* Job management
* Candidate viewing
* Application review
* Candidate shortlisting
* Candidate rejection
* Application status management

---

## Gemini Testing

The application provides:

```text
/test_gemini
```

This route can be used to verify the Gemini AI connection.

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

1. Simplify the recruitment process.
2. Provide separate dashboards for candidates and recruiters.
3. Automate basic resume analysis.
4. Identify skills from candidate resumes.
5. Identify missing skills.
6. Recommend jobs based on candidate skills.
7. Allow candidates to apply for suitable jobs.
8. Help recruiters manage jobs and candidates.
9. Provide application status tracking and notifications.
10. Generate personalized resume-based interview questions.
11. Provide configurable interview duration and question count.
12. Generate adaptive follow-up questions.
13. Evaluate interview performance.
14. Improve candidate interview preparation and recruitment management.

---

# ✅ Current Implementation

The current project includes:

* Candidate authentication
* Recruiter authentication
* Forgot password functionality
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
* HR interview mode
* Technical interview mode
* Configurable interview question count
* Configurable interview duration
* Interview countdown timer
* Automatic interview submission on timeout
* Adaptive follow-up questions
* Interview answer evaluation
* Interview score
* Interview performance percentage
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
* Face-to-face/video interview mode
* Speech-to-text interview interaction
* Improved AI interview evaluation
* Admin dashboard
* Advanced candidate filtering
* Cloud database integration
* Advanced resume scoring
* AI-generated interview feedback
* Improved candidate ranking algorithms

---

# 🌟 Why HireSmart AI?

HireSmart AI combines recruitment management, resume intelligence, skill analysis, job matching, and generative AI into a single platform.

### Candidates can:

* Manage their professional profile
* Upload and analyze resumes
* Understand their skills
* Identify missing skills
* Discover suitable jobs
* Apply for jobs
* Track applications
* Practice through AI-powered interviews
* Receive interview performance results

### Recruiters can:

* Post jobs
* Manage job opportunities
* View candidates
* Review applications
* Shortlist candidates
* Reject candidates
* Manage the recruitment process

HireSmart AI provides a centralized platform for important candidate and recruiter activities.

---

# 📚 Academic Purpose

HireSmart AI is developed as an academic software project to demonstrate the practical application of:

* Python programming
* Flask web development
* HTML, CSS and JavaScript
* Database management
* SQL
* Resume processing
* Skill detection
* Job matching
* Web application development
* Generative AI
* Recruitment management
* AI-powered interview systems

---

# 🌐 Project Links

### GitHub Repository

[https://github.com/salunkeprajakta/HireSmart-AI](https://github.com/salunkeprajakta/HireSmart-AI)

### Live Deployment

[https://hiresmart-ai-1-dmbg.onrender.com](https://hiresmart-ai-1-dmbg.onrender.com)

---

# 👩‍💻 Author

**Prajakta Salunke**

**Project:** HireSmart AI – AI-Powered Recruitment & Candidate Management Platform

---

# 📄 License

This project is developed for educational and academic purposes.
