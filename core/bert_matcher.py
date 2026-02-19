"""
BERT Semantic Matching Engine
Core intelligence module using BERT transformers for semantic similarity
"""

import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skills_database import get_all_skills_flat


# Global model variable (will be loaded once and cached)
_bert_model = None


def load_bert_model(model_name: str = 'all-MiniLM-L6-v2'):
    """
    Load BERT model for semantic encoding
    Should be cached in Streamlit using @st.cache_resource
    
    Args:
        model_name (str): Model name from sentence-transformers
        
    Returns:
        SentenceTransformer: Loaded model
    """
    global _bert_model
    
    if _bert_model is None:
        print(f"Loading BERT model: {model_name}...")
        _bert_model = SentenceTransformer(model_name)
        print("Model loaded successfully!")
    
    return _bert_model


def get_bert_embedding(text: str, model):
    """
    Generate BERT embedding for text
    
    Args:
        text (str): Text to encode
        model: SentenceTransformer model
        
    Returns:
        numpy.ndarray: Embedding vector
    """
    if not text or not text.strip():
        # Empty text ke liye zero vector return karo
        return np.zeros(384)  # MiniLM-L6 ka embedding size 384 hai
    
    # Text ko encode karo
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def calculate_semantic_similarity(text1: str, text2: str, model) -> float:
    """
    Calculate cosine similarity between two texts using BERT embeddings
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        model: SentenceTransformer model
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Dono texts ke embeddings generate karo
    emb1 = get_bert_embedding(text1, model)
    emb2 = get_bert_embedding(text2, model)
    
    # Cosine similarity calculate karo
    # Reshape karo for sklearn (needs 2D array)
    emb1 = emb1.reshape(1, -1)
    emb2 = emb2.reshape(1, -1)
    
    similarity = cosine_similarity(emb1, emb2)[0][0]
    
    # Ensure value is between 0 and 1
    similarity = max(0.0, min(1.0, similarity))
    
    return float(similarity)


def calculate_section_similarities(resume_sections: dict, job_description: str, model) -> dict:
    """
    Calculate similarity scores for each resume section separately
    
    Args:
        resume_sections (dict): Segmented resume sections
        job_description (str): Job description text
        model: SentenceTransformer model
        
    Returns:
        dict: {"skills": float, "experience": float, "education": float, "overall": float}
    """
    similarities = {
        "skills": 0.0,
        "experience": 0.0,
        "education": 0.0,
        "overall": 0.0
    }
    
    # Skills section similarity
    skills_text = resume_sections.get("skills", "")
    if skills_text:
        similarities["skills"] = calculate_semantic_similarity(skills_text, job_description, model)
    
    # Experience section similarity
    experience_text = resume_sections.get("experience", "")
    if experience_text:
        similarities["experience"] = calculate_semantic_similarity(experience_text, job_description, model)
    
    # Education section similarity
    education_text = resume_sections.get("education", "")
    if education_text:
        similarities["education"] = calculate_semantic_similarity(education_text, job_description, model)
    
    # Overall resume similarity
    full_text = resume_sections.get("full_text", "")
    if full_text:
        similarities["overall"] = calculate_semantic_similarity(full_text, job_description, model)
    
    return similarities


def extract_keywords_from_jd(job_description: str) -> dict:
    """
    Extract key requirements from job description
    
    Args:
        job_description (str): Job description text
        
    Returns:
        dict: {
            "required_skills": list,
            "preferred_skills": list,
            "min_experience_years": float,
            "education_requirement": str,
            "job_title": str
        }
    """
    jd_lower = job_description.lower()
    
    # Skills extract karo from JD
    all_skills = get_all_skills_flat()
    required_skills = []
    
    for skill in all_skills:
        if skill.lower() in jd_lower:
            required_skills.append(skill)
    
    # Experience requirement extract karo
    # Patterns: "3+ years", "3-5 years", "minimum 3 years"
    exp_patterns = [
        r'(\d+)\s*\+\s*years?',
        r'(\d+)\s*to\s*\d+\s*years?',
        r'(\d+)\s*-\s*\d+\s*years?',
        r'minimum\s+(\d+)\s*years?',
        r'at\s+least\s+(\d+)\s*years?'
    ]
    
    min_experience = 0.0
    for pattern in exp_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            min_experience = float(match.group(1))
            break
    
    # Education requirement extract karo
    education_req = ""
    if re.search(r'phd|doctor', jd_lower):
        education_req = "PhD"
    elif re.search(r'master|m\.?s\.?|m\.?a\.?|mba', jd_lower):
        education_req = "Master"
    elif re.search(r'bachelor|b\.?s\.?|b\.?a\.?|b\.?e\.?|b\.?tech', jd_lower):
        education_req = "Bachelor"
    
    # Job title extract karo (first line usually)
    first_line = job_description.split('\n')[0].strip()
    job_title = first_line[:100] if first_line else "Position"
    
    # Preferred vs Required skills (simple heuristic)
    # Agar JD mein "required" ke paas mention hai to required, else preferred
    preferred_skills = []
    # For simplicity, sab ko required consider karo
    
    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "min_experience_years": min_experience,
        "education_requirement": education_req,
        "job_title": job_title
    }


def calculate_keyword_match_score(candidate_skills: list, required_skills: list) -> float:
    """
    Calculate percentage of required skills that candidate has
    
    Args:
        candidate_skills (list): Skills found in candidate's resume
        required_skills (list): Skills required in job description
        
    Returns:
        float: Match score between 0 and 1
    """
    if not required_skills:
        # Agar koi required skills nahi to full score
        return 1.0
    
    if not candidate_skills:
        # Agar candidate ke paas koi skills nahi
        return 0.0
    
    # Case-insensitive comparison ke liye lowercase mein convert karo
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    required_skills_lower = [s.lower() for s in required_skills]
    
    # Matched skills count karo
    matched_count = 0
    for req_skill in required_skills_lower:
        # Exact match ya fuzzy match (partial string match)
        for cand_skill in candidate_skills_lower:
            if req_skill in cand_skill or cand_skill in req_skill:
                matched_count += 1
                break
    
    # Percentage calculate karo
    match_score = matched_count / len(required_skills)
    
    return match_score


def get_missing_skills(candidate_skills: list, required_skills: list) -> list:
    """
    Get list of required skills that candidate is missing
    
    Args:
        candidate_skills (list): Skills found in candidate's resume
        required_skills (list): Skills required in job description
        
    Returns:
        list: Missing skills
    """
    if not required_skills:
        return []
    
    # Case-insensitive comparison
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    
    missing = []
    for req_skill in required_skills:
        # Check karo agar skill candidate ke paas hai ya nahi
        found = False
        for cand_skill in candidate_skills_lower:
            if req_skill.lower() in cand_skill or cand_skill in req_skill.lower():
                found = True
                break
        
        if not found:
            missing.append(req_skill)
    
    return missing


def get_matched_skills(candidate_skills: list, required_skills: list) -> list:
    """
    Get list of required skills that candidate has
    
    Args:
        candidate_skills (list): Skills found in candidate's resume
        required_skills (list): Skills required in job description
        
    Returns:
        list: Matched skills
    """
    if not required_skills:
        return candidate_skills
    
    # Case-insensitive comparison
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    
    matched = []
    for req_skill in required_skills:
        # Check karo agar skill candidate ke paas hai
        for cand_skill_lower, cand_skill_original in zip(candidate_skills_lower, candidate_skills):
            if req_skill.lower() in cand_skill_lower or cand_skill_lower in req_skill.lower():
                matched.append(cand_skill_original)
                break
    
    return matched
