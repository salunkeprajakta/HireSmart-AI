# =========================================================
# HIRESMART AI - JOB RECOMMENDATION SYSTEM
# =========================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# CALCULATE JOB MATCH
# =========================================================

def calculate_match(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    resume_text = resume_text.lower()
    job_text = job_text.lower()

    documents = [
        resume_text,
        job_text
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

        score = int(similarity * 100)

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
# RECOMMEND JOBS
# =========================================================

def recommend_jobs(resume_text, jobs):

    recommendations = []

    if not resume_text:
        return recommendations

    for job in jobs:

        # -------------------------------------------------
        # Create job text
        # -------------------------------------------------

        job_title = job.get(
            "title",
            ""
        )

        company = job.get(
            "company",
            ""
        )

        location = job.get(
            "location",
            ""
        )

        skills = job.get(
            "skills",
            ""
        )

        description = job.get(
            "description",
            ""
        )

        # -------------------------------------------------
        # Convert skills list to text
        # -------------------------------------------------

        if isinstance(skills, list):

            skills_text = " ".join(
                skills
            )

        else:

            skills_text = str(
                skills
            )

        # -------------------------------------------------
        # Complete job text
        # -------------------------------------------------

        job_text = " ".join([
            job_title,
            company,
            location,
            skills_text,
            description
        ])

        # -------------------------------------------------
        # Calculate AI match
        # -------------------------------------------------

        score = calculate_match(
            resume_text,
            job_text
        )

        # -------------------------------------------------
        # Match level
        # -------------------------------------------------

        match_level = get_match_level(
            score
        )

        # -------------------------------------------------
        # Add recommendation
        # -------------------------------------------------

        recommendation = {

            "id": job.get("id"),

            "title": job_title,

            "company": company,

            "location": location,

            "skills": skills,

            "description": description,

            "match": score,

            "match_level": match_level

        }

        recommendations.append(
            recommendation
        )

    # -----------------------------------------------------
    # Highest matching jobs first
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda job: job["match"],
        reverse=True
    )

    return recommendations