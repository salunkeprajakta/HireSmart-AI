
# 🤖 HireSmart AI – AI-Powered Recruitment & Candidate Management Platform

HireSmart AI is an AI-powered web-based recruitment platform designed to simplify and improve the hiring process for both candidates and recruiters.

The platform provides separate dashboards for candidates and recruiters and combines resume processing, skill analysis, job matching, job applications, candidate management, notifications, and AI-powered interviews into a single recruitment system.

---

#### 🔐 Authentication
- Candidate registration
- Candidate login
- Session-based authentication
- Logout functionality
- Forgot password functionality

#### 👤 Candidate Profile
Candidates can manage:
- Name
- Email
- Phone
- Education
- Skills
- Experience

#### 📄 Resume Upload
Candidates can upload resumes for analysis.

Supported formats:
- PDF
- DOCX

#### 📝 Resume Analysis
The system extracts text from uploaded resumes and performs analysis.

Features include:
- Resume text extraction
- Resume scoring
- Skill identification
- Missing skill identification
- Resume improvement suggestions

#### 🧠 Skill Analysis
The system identifies relevant technical and soft skills from the resume.

Examples:
- Python
- Java
- C++
- HTML
- CSS
- JavaScript
- SQL
- Flask
- Django
- Machine Learning
- Data Science
- Git
- GitHub
- React
- Node.js
- MongoDB
- Power BI
- Communication
- Leadership

#### 💼 Job Search & Recommendations
Candidates can:
- Browse available jobs
- View job requirements
- Check skill matching
- Receive job recommendations
- Apply for suitable jobs

#### 📋 Job Applications
Candidates can:
- Apply for jobs
- View submitted applications
- Track application status
- Receive notifications

#### 🔔 Notifications
Candidates receive notifications related to their job applications and application status.

#### 🎤 AI-Powered Interview
Candidates can attend an AI-powered interview based on their resume.

The system:
- Uses resume information
- Generates personalized interview questions
- Collects candidate answers
- Evaluates answers
- Calculates an interview score
- Displays the final result

---

## 👨‍💼 Recruiter Features

### 🔐 Recruiter Authentication
Recruiters can:
- Register
- Login
- Logout

### 📊 Recruiter Dashboard
The recruiter dashboard provides access to recruitment-related functionality.

### 💼 Job Posting
Recruiters can create job opportunities containing:
- Job title
- Company
- Location
- Required skills
- Job description

### 📋 Job Management
Recruiters can:
- View posted jobs
- Manage job opportunities

### 👥 Candidate Management
Recruiters can view candidate information such as:
- Candidate name
- Skills
- Education
- Experience
- Contact information

### 📑 Application Management
Recruiters can review candidate applications and update application status.

Supported actions:
- Shortlist candidate
- Reject candidate

---

# 🧠 AI Features

HireSmart AI integrates Google Gemini AI for AI-powered interview functionality.

## 🎤 Resume-Based Interview Questions

The candidate's resume is used as context for generating interview questions.

Questions can be related to:
- Skills
- Projects
- Education
- Experience
- Technologies
- Candidate contributions
- Learning

The purpose is to generate questions relevant to the candidate instead of asking completely unrelated questions.

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
````

---

# 📄 Resume Processing

HireSmart AI supports resume processing for PDF and DOCX files.

### PDF Resume Processing

PDF text is extracted using the PyPDF library.

### DOCX Resume Processing

DOCX text is extracted using the python-docx library.

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
Generate Resume Suggestions
```

---

# 💼 Job Matching

HireSmart AI uses candidate skills to calculate compatibility with job requirements.

Example:

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

# 🔄 Application Workflow

## 👩‍🎓 Candidate Flow

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

## 👨‍💼 Recruiter Flow

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
│   ├── interview_result.html
│   └── forgot_password.html
│
└── uploads/
    └── .gitkeep
```

---

# 🗄️ Database

HireSmart AI uses SQLite for storing application data.

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
git clone https://github.com/salunkeprajakta/HireSmart-AI.git
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

The Gemini API key should not be stored directly inside the source code.

The application reads the API key from an environment variable.

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
* Interview questions
* Interview evaluation
* Interview result

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
10. Generate resume-based AI interview questions.
11. Evaluate interview performance.
12. Improve candidate screening and interview preparation.

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

### Candidates can:

* Analyze their resumes
* Understand their skills
* Identify missing skills
* Discover suitable jobs
* Apply for jobs
* Prepare through AI-powered interviews
* View interview performance

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

[HireSmart-AI GitHub Repository](https://github.com/salunkeprajakta/HireSmart-AI?utm_source=chatgpt.com)
