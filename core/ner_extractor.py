"""
Named Entity Recognition (NER) Module
Extract structured information from resumes using spaCy and regex patterns
"""

import re
import spacy
from utils.skills_database import extract_skills_from_text


# spaCy model load karo (globally, taake baar baar load na ho)
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Warning: spaCy model 'en_core_web_lg' not found. Please run: python -m spacy download en_core_web_lg")
    nlp = None


def extract_candidate_name(text: str) -> str:
    """
    Extract candidate name from resume using spaCy NER
    
    Args:
        text (str): Resume text
        
    Returns:
        str: Candidate name or "Unknown Candidate"
    """
    if not text or not nlp:
        return "Unknown Candidate"
    
    # First 500 characters se name extract karo (usually top mein hota hai)
    text_start = text[:500]
    
    # spaCy NER run karo
    doc = nlp(text_start)
    
    # PERSON entities dhundo
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # First person entity ko name consider karo
            return ent.text.strip()
    
    # Agar NER se nahi mila, to first line try karo
    # First line usually name hoti hai resumes mein
    first_line = text.split('\n')[0].strip()
    
    # Check karo agar first line name jaisi lagti hai (2-4 words, title case)
    words = first_line.split()
    if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
        return first_line
    
    return "Unknown Candidate"


def extract_contact_info(text: str) -> dict:
    """
    Extract contact information using regex patterns
    
    Args:
        text (str): Resume text
        
    Returns:
        dict: {"email": str, "phone": str, "linkedin": str, "github": str}
    """
    contact = {
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    }
    
    if not text:
        return contact
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact["email"] = email_match.group(0)
    
    # Phone pattern - multiple formats support karo
    # Formats: +92-333-1234567, (333) 123-4567, 03331234567, 333-123-4567
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\d{11}',  # 11 digit Pakistani
        r'\d{10}'   # 10 digit
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact["phone"] = phone_match.group(0)
            break
    
    # LinkedIn URL
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group(0)
    
    # GitHub URL
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact["github"] = github_match.group(0)
    
    return contact


def extract_education(text: str) -> list:
    """
    Extract education information (degrees, institutions, years)
    
    Args:
        text (str): Resume text (preferably education section)
        
    Returns:
        list: [{"degree": str, "institution": str, "year": str}]
    """
    education_list = []
    
    if not text or not nlp:
        return education_list
    
    # Degree keywords
    degree_patterns = [
        r'Bachelor(?:\s+of\s+(?:Science|Arts|Engineering|Technology|Business|Commerce))?',
        r'Master(?:\s+of\s+(?:Science|Arts|Engineering|Technology|Business|Commerce))?',
        r'PhD|Doctor\s+of\s+Philosophy',
        r'MBA|Master\s+of\s+Business\s+Administration',
        r'B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Tech',
        r'M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Tech',
        r'Associate(?:\s+Degree)?',
        r'Diploma'
    ]
    
    # Text ko lines mein split karo
    lines = text.split('\n')
    
    for line in lines:
        # Degree pattern match karo
        for pattern in degree_patterns:
            degree_match = re.search(pattern, line, re.IGNORECASE)
            if degree_match:
                degree = degree_match.group(0)
                
                # Year extract karo (4 digit number)
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                year = year_match.group(0) if year_match else ""
                
                # Institution name extract karo using spaCy ORG entities
                institution = ""
                if nlp:
                    doc = nlp(line)
                    for ent in doc.ents:
                        if ent.label_ == "ORG":
                            institution = ent.text
                            break
                
                # Agar institution nahi mila, to line ka remaining part use karo
                if not institution:
                    # Degree ke baad ka text institution ho sakta hai
                    remaining = line[degree_match.end():].strip()
                    # Year remove karo
                    if year:
                        remaining = remaining.replace(year, '').strip()
                    # First 50 chars tak institution consider karo
                    institution = remaining[:50].strip()
                
                education_list.append({
                    "degree": degree,
                    "institution": institution,
                    "year": year
                })
                break  # Ek degree per line
    
    return education_list


def extract_experience_years(text: str) -> float:
    """
    Extract total years of experience from resume
    
    Args:
        text (str): Resume text (preferably experience section)
        
    Returns:
        float: Total years of experience
    """
    if not text:
        return 0.0
    
    # Pattern 1: "X years of experience" pattern
    exp_pattern1 = r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience'
    match1 = re.search(exp_pattern1, text, re.IGNORECASE)
    if match1:
        return float(match1.group(1))
    
    # Pattern 2: Date ranges calculate karo (2019-2023 = 4 years)
    # Format: YYYY-YYYY or YYYY - YYYY
    date_ranges = re.findall(r'\b(20\d{2})\s*[-–]\s*(20\d{2}|Present|Current)\b', text, re.IGNORECASE)
    
    total_years = 0.0
    for start_year, end_year in date_ranges:
        start = int(start_year)
        # Agar "Present" ya "Current" hai to current year use karo
        if end_year.lower() in ['present', 'current']:
            end = 2026  # Current year
        else:
            end = int(end_year)
        
        years = end - start
        if years > 0:
            total_years += years
    
    if total_years > 0:
        return float(total_years)
    
    # Pattern 3: Agar kuch nahi mila, to job entries count karo (rough estimate)
    # "Experience" section mein kitni baar company/position mentioned hai
    job_indicators = len(re.findall(r'\b(?:worked|employed|position|role)\b', text, re.IGNORECASE))
    
    # Har job ko average 2 years assume karo
    if job_indicators > 0:
        return float(job_indicators * 2)
    
    return 0.0


def extract_all_entities(text: str, sections: dict) -> dict:
    """
    Extract all entities and create complete candidate profile
    
    Args:
        text (str): Full resume text
        sections (dict): Segmented resume sections
        
    Returns:
        dict: Complete candidate profile with all extracted information
    """
    # Name extract karo
    name = extract_candidate_name(text)
    
    # Contact info extract karo
    contact = extract_contact_info(text)
    
    # Education extract karo (education section se preferably)
    education_text = sections.get("education", "") or text
    education = extract_education(education_text)
    
    # Experience years calculate karo
    experience_text = sections.get("experience", "") or text
    experience_years = extract_experience_years(experience_text)
    
    # Skills extract karo (skills section + full text)
    skills_text = sections.get("skills", "") + "\n" + text
    skills = extract_skills_from_text(skills_text)
    
    # Complete profile banao
    profile = {
        "name": name,
        "email": contact["email"],
        "phone": contact["phone"],
        "linkedin": contact["linkedin"],
        "github": contact["github"],
        "education": education,
        "experience_years": experience_years,
        "skills": skills,
        "total_skills_count": len(skills["all_skills_flat"])
    }
    
    return profile
