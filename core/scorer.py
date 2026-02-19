"""
Scoring and Ranking Module
Combine all signals into final candidate score with detailed breakdown
"""

import pandas as pd
from core.extractor import extract_text
from core.preprocessor import preprocess_resume
from core.ner_extractor import extract_all_entities
from core.bert_matcher import (
    calculate_section_similarities,
    calculate_keyword_match_score,
    get_missing_skills,
    get_matched_skills
)


# Scoring weights (configurable)
SCORE_WEIGHTS = {
    "semantic_similarity": 0.40,  # BERT overall similarity
    "skills_match": 0.30,         # Keyword/skills overlap
    "experience_match": 0.20,     # Experience years vs requirement
    "education_match": 0.10       # Education level match
}


def calculate_experience_score(candidate_years: float, required_years: float) -> float:
    """
    Calculate experience match score
    
    Args:
        candidate_years (float): Candidate's years of experience
        required_years (float): Required years in JD
        
    Returns:
        float: Score between 0 and 1
    """
    # Agar requirement nahi hai to full score
    if required_years == 0:
        return 1.0
    
    # Agar candidate requirement se zyada ya barabar hai
    if candidate_years >= required_years:
        return 1.0
    
    # Agar 75% se zyada hai
    if candidate_years >= required_years * 0.75:
        return 0.75
    
    # Agar 50% se zyada hai
    if candidate_years >= required_years * 0.5:
        return 0.5
    
    # Proportional score
    return candidate_years / required_years


def calculate_education_score(candidate_education: list, required_education: str) -> float:
    """
    Calculate education match score
    
    Args:
        candidate_education (list): List of candidate's degrees
        required_education (str): Required education level
        
    Returns:
        float: Score between 0 and 1
    """
    # Education levels mapping
    education_levels = {
        "PhD": 4,
        "Doctor": 4,
        "Master": 3,
        "MBA": 3,
        "Bachelor": 2,
        "Associate": 1,
        "Diploma": 1
    }
    
    # Agar koi requirement nahi to full score
    if not required_education:
        return 1.0
    
    # Required level nikalo
    required_level = education_levels.get(required_education, 0)
    
    # Candidate ka highest level nikalo
    candidate_level = 0
    for edu in candidate_education:
        degree = edu.get("degree", "")
        for edu_name, level in education_levels.items():
            if edu_name.lower() in degree.lower():
                candidate_level = max(candidate_level, level)
    
    # Agar candidate ka level requirement se zyada ya barabar
    if candidate_level >= required_level:
        return 1.0
    
    # Proportional score
    if required_level > 0:
        return candidate_level / required_level
    
    return 0.5  # Default moderate score


def calculate_final_score(
    semantic_scores: dict,
    keyword_score: float,
    experience_score: float,
    education_score: float,
    weights: dict = None
) -> dict:
    """
    Combine all scores using weights to get final score
    
    Args:
        semantic_scores (dict): BERT similarity scores
        keyword_score (float): Skills match score
        experience_score (float): Experience match score
        education_score (float): Education match score
        weights (dict): Optional custom weights
        
    Returns:
        dict: {
            "final_score": float (0-100),
            "grade": str,
            "recommendation": str,
            "score_breakdown": dict
        }
    """
    if weights is None:
        weights = SCORE_WEIGHTS
    
    # Overall semantic score use karo
    semantic_score = semantic_scores.get("overall", 0.0)
    
    # Weighted sum calculate karo
    final_score = (
        semantic_score * weights["semantic_similarity"] +
        keyword_score * weights["skills_match"] +
        experience_score * weights["experience_match"] +
        education_score * weights["education_match"]
    )
    
    # 0-100 scale mein convert karo
    final_score_percent = final_score * 100
    
    # Grade assign karo
    if final_score_percent >= 80:
        grade = "A"
        recommendation = "Strong Match — Shortlist Immediately"
    elif final_score_percent >= 65:
        grade = "B"
        recommendation = "Good Match — Worth Interviewing"
    elif final_score_percent >= 50:
        grade = "C"
        recommendation = "Average Match — Review Manually"
    elif final_score_percent >= 35:
        grade = "D"
        recommendation = "Below Average — Missing Key Requirements"
    else:
        grade = "F"
        recommendation = "Poor Match — Not Suitable"
    
    return {
        "final_score": round(final_score_percent, 2),
        "grade": grade,
        "recommendation": recommendation,
        "score_breakdown": {
            "semantic_score": round(semantic_score * 100, 2),
            "skills_score": round(keyword_score * 100, 2),
            "experience_score": round(experience_score * 100, 2),
            "education_score": round(education_score * 100, 2)
        }
    }


def process_single_resume(uploaded_file, job_description: str, jd_analysis: dict, model) -> dict:
    """
    Complete pipeline for processing one resume
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        job_description (str): Job description text
        jd_analysis (dict): Extracted JD requirements
        model: BERT model
        
    Returns:
        dict: Complete candidate result with all scores and info
    """
    # Step 1: Extract text from file
    extraction_result = extract_text(uploaded_file)
    
    if not extraction_result["extraction_success"]:
        # Agar extraction fail ho gaya
        return {
            "filename": extraction_result["filename"],
            "name": "Extraction Failed",
            "error": extraction_result["error_message"],
            "final_score": 0.0,
            "grade": "F"
        }
    
    raw_text = extraction_result["raw_text"]
    
    # Step 2: Preprocess and segment text
    sections = preprocess_resume(raw_text)
    
    # Step 3: Extract entities and skills
    candidate_profile = extract_all_entities(raw_text, sections)
    
    # Step 4: Calculate BERT semantic similarities
    semantic_scores = calculate_section_similarities(sections, job_description, model)
    
    # Step 5: Calculate keyword match score
    candidate_skills = candidate_profile["skills"]["all_skills_flat"]
    required_skills = jd_analysis["required_skills"]
    keyword_score = calculate_keyword_match_score(candidate_skills, required_skills)
    
    # Step 6: Calculate experience score
    experience_score = calculate_experience_score(
        candidate_profile["experience_years"],
        jd_analysis["min_experience_years"]
    )
    
    # Step 7: Calculate education score
    education_score = calculate_education_score(
        candidate_profile["education"],
        jd_analysis["education_requirement"]
    )
    
    # Step 8: Calculate final score
    final_result = calculate_final_score(
        semantic_scores,
        keyword_score,
        experience_score,
        education_score
    )
    
    # Step 9: Get matched and missing skills
    matched_skills = get_matched_skills(candidate_skills, required_skills)
    missing_skills = get_missing_skills(candidate_skills, required_skills)
    
    # Combine everything into complete result
    result = {
        "filename": extraction_result["filename"],
        "name": candidate_profile["name"],
        "email": candidate_profile["email"],
        "phone": candidate_profile["phone"],
        "linkedin": candidate_profile["linkedin"],
        "github": candidate_profile["github"],
        "education": candidate_profile["education"],
        "experience_years": candidate_profile["experience_years"],
        "total_skills_count": candidate_profile["total_skills_count"],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_skills_count": len(matched_skills),
        "missing_skills_count": len(missing_skills),
        "final_score": final_result["final_score"],
        "grade": final_result["grade"],
        "recommendation": final_result["recommendation"],
        "semantic_score": final_result["score_breakdown"]["semantic_score"],
        "skills_score": final_result["score_breakdown"]["skills_score"],
        "experience_score": final_result["score_breakdown"]["experience_score"],
        "education_score": final_result["score_breakdown"]["education_score"],
        "skills_detail": candidate_profile["skills"]  # Full categorized skills
    }
    
    return result


def process_all_resumes(uploaded_files: list, job_description: str, model) -> pd.DataFrame:
    """
    Process multiple resumes and return ranked DataFrame
    
    Args:
        uploaded_files (list): List of Streamlit UploadedFile objects
        job_description (str): Job description text
        model: BERT model
        
    Returns:
        pd.DataFrame: Sorted DataFrame with all candidates ranked
    """
    from core.bert_matcher import extract_keywords_from_jd
    
    # JD ko ek baar analyze karo
    jd_analysis = extract_keywords_from_jd(job_description)
    
    # Har resume ko process karo
    results = []
    for uploaded_file in uploaded_files:
        result = process_single_resume(uploaded_file, job_description, jd_analysis, model)
        results.append(result)
    
    # DataFrame banao
    df = pd.DataFrame(results)
    
    # Final score se sort karo (descending)
    df = df.sort_values("final_score", ascending=False)
    
    # Rank column add karo
    df.insert(0, "rank", range(1, len(df) + 1))
    
    # Index reset karo
    df = df.reset_index(drop=True)
    
    return df
