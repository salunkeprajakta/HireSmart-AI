# =========================================================
# HIRESMART AI - AI JOB MATCHING
# =========================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_job_match(resume_text, job_text):
    """
    Calculate similarity between a candidate resume
    and a job description using TF-IDF.
    """

    if not resume_text or not job_text:
        return 0

    documents = [
        resume_text.lower(),
        job_text.lower()
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:
        vectors = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        percentage = int(similarity * 100)

        if percentage > 100:
            percentage = 100

        return percentage

    except ValueError:
        return 0


def get_match_level(score):
    """
    Return a simple match level.
    """

    if score >= 80:
        return "Excellent Match"

    elif score >= 60:
        return "Good Match"

    elif score >= 40:
        return "Average Match"

    else:
        return "Low Match"