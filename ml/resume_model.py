# =========================================================
# HIRESMART AI - RESUME ANALYSIS MODEL
# =========================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# COMMON SKILLS
# =========================================================

SKILLS = [
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
# EXTRACT SKILLS FROM RESUME
# =========================================================

def extract_skills(resume_text):

    if not resume_text:
        return []

    text = resume_text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


# =========================================================
# FIND MISSING SKILLS
# =========================================================

def find_missing_skills(resume_text):

    if not resume_text:
        return SKILLS.copy()

    found_skills = extract_skills(resume_text)

    missing_skills = [
        skill
        for skill in SKILLS
        if skill not in found_skills
    ]

    return missing_skills


# =========================================================
# RESUME SCORE
# =========================================================

def calculate_resume_score(resume_text):

    if not resume_text:
        return 0

    text = resume_text.lower()

    score = 0

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    found_skills = extract_skills(text)

    skill_score = min(
        len(found_skills) * 5,
        40
    )

    score += skill_score

    # -----------------------------------------------------
    # Resume sections
    # -----------------------------------------------------

    sections = {
        "education": 10,
        "experience": 10,
        "project": 10,
        "objective": 10,
        "certificate": 5,
        "contact": 5
    }

    for section, points in sections.items():

        if section in text:
            score += points

    return min(score, 100)


# =========================================================
# RESUME QUALITY SUGGESTIONS
# =========================================================

def get_resume_suggestions(resume_text):

    suggestions = []

    if not resume_text:
        return [
            "Upload a valid text-based resume."
        ]

    text = resume_text.lower()

    found_skills = extract_skills(text)

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    if len(found_skills) < 5:

        suggestions.append(
            "Add more relevant technical skills."
        )

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------

    if "education" not in text:

        suggestions.append(
            "Add an Education section."
        )

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    if "experience" not in text:

        suggestions.append(
            "Add internship, training, or work experience."
        )

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    if "project" not in text:

        suggestions.append(
            "Add academic or personal projects."
        )

    # -----------------------------------------------------
    # Career Objective
    # -----------------------------------------------------

    if "objective" not in text:

        suggestions.append(
            "Add a clear career objective or professional summary."
        )

    # -----------------------------------------------------
    # Contact
    # -----------------------------------------------------

    if "email" not in text:

        suggestions.append(
            "Make sure your email address is included."
        )

    if not suggestions:

        suggestions.append(
            "Your resume has good basic information. Keep it updated."
        )

    return suggestions


# =========================================================
# AI JOB MATCHING
# =========================================================

def calculate_job_match(resume_text, job_description):

    if not resume_text or not job_description:
        return 0

    documents = [
        resume_text.lower(),
        job_description.lower()
    ]

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        vectors = vectorizer.fit_transform(
            documents
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        score = int(
            similarity * 100
        )

        return min(score, 100)

    except ValueError:

        return 0


# =========================================================
# MATCH LEVEL
# =========================================================

def get_match_level(score):

    if score >= 80:

        return "Excellent Match"

    elif score >= 60:

        return "Good Match"

    elif score >= 40:

        return "Average Match"

    else:

        return "Low Match"


# =========================================================
# COMPLETE RESUME ANALYSIS
# =========================================================

def analyze_resume(resume_text):

    found_skills = extract_skills(
        resume_text
    )

    missing_skills = find_missing_skills(
        resume_text
    )

    score = calculate_resume_score(
        resume_text
    )

    suggestions = get_resume_suggestions(
        resume_text
    )

    return {
        "score": score,
        "skills": found_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions
    }