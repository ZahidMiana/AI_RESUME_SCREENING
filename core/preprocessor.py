"""
Text Preprocessor Module
Clean, normalize, and segment resume text for NLP processing
"""

import re


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing special characters and extra whitespace
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Special characters remove karo except useful ones
    # Keep: . , @ # + / - ( )
    text = re.sub(r'[^\w\s.,@#+/()\-]', ' ', text)
    
    # Multiple spaces ko single space mein convert karo
    text = re.sub(r'\s+', ' ', text)
    
    # Extra newlines remove karo
    text = re.sub(r'\n+', '\n', text)
    
    # Leading/trailing whitespace remove karo
    text = text.strip()
    
    return text


def normalize_text(text: str) -> str:
    """
    Normalize text by expanding abbreviations and standardizing terms
    
    Args:
        text (str): Text to normalize
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Common abbreviations expand karo
    abbreviations = {
        r'\byrs?\b': 'years',
        r'\byr\b': 'year',
        r'\bexp\b': 'experience',
        r'\bmgmt\b': 'management',
        r'\bdept\b': 'department',
        r'\bcert\b': 'certification',
        r'\bcerts\b': 'certifications',
        r'\bB\.?S\.?\b': 'Bachelor of Science',
        r'\bB\.?A\.?\b': 'Bachelor of Arts',
        r'\bM\.?S\.?\b': 'Master of Science',
        r'\bM\.?A\.?\b': 'Master of Arts',
        r'\bMBA\b': 'Master of Business Administration',
        r'\bPhD\b': 'Doctor of Philosophy',
        r'\bB\.?E\.?\b': 'Bachelor of Engineering',
        r'\bM\.?E\.?\b': 'Master of Engineering',
        r'\bB\.?Tech\b': 'Bachelor of Technology',
        r'\bM\.?Tech\b': 'Master of Technology',
    }
    
    # Case-insensitive replacement
    for abbr, full_form in abbreviations.items():
        text = re.sub(abbr, full_form, text, flags=re.IGNORECASE)
    
    return text


def segment_resume(text: str) -> dict:
    """
    Segment resume into different sections using keyword detection
    
    Args:
        text (str): Full resume text
        
    Returns:
        dict: {
            "contact": str,
            "summary": str,
            "experience": str,
            "education": str,
            "skills": str,
            "projects": str,
            "certifications": str,
            "full_text": str
        }
    """
    if not text:
        return {
            "contact": "",
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "certifications": "",
            "full_text": ""
        }
    
    # Section headers ke patterns define karo (case-insensitive)
    section_patterns = {
        "contact": r'(?:contact|personal\s+information|contact\s+information)',
        "summary": r'(?:summary|profile|objective|about\s+me|professional\s+summary)',
        "experience": r'(?:experience|work\s+experience|employment|work\s+history|professional\s+experience)',
        "education": r'(?:education|academic|qualification|educational\s+background)',
        "skills": r'(?:skills|technical\s+skills|core\s+competencies|expertise|technologies)',
        "projects": r'(?:projects|personal\s+projects|academic\s+projects)',
        "certifications": r'(?:certifications?|certificates?|licenses?|training)'
    }
    
    # Text ko lines mein split karo
    lines = text.split('\n')
    
    # Initialize sections
    sections = {
        "contact": [],
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "full_text": text
    }
    
    current_section = None
    
    # Har line ko process karo
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check karo agar ye line koi section header hai
        is_header = False
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line_stripped, re.IGNORECASE):
                current_section = section_name
                is_header = True
                break
        
        # Agar header nahi hai aur current section set hai, to content add karo
        if not is_header and current_section:
            sections[current_section].append(line_stripped)
    
    # Lists ko strings mein convert karo
    for section_name in sections:
        if section_name != "full_text":
            sections[section_name] = "\n".join(sections[section_name])
    
    # Agar koi section nahi mila, to first 500 chars ko contact consider karo
    if not sections["contact"] and not sections["summary"]:
        sections["contact"] = text[:500]
    
    return sections


def preprocess_resume(text: str) -> dict:
    """
    Complete preprocessing pipeline: clean, normalize, and segment
    
    Args:
        text (str): Raw resume text
        
    Returns:
        dict: Preprocessed sections with cleaned text
    """
    # Step 1: Clean karo
    cleaned = clean_text(text)
    
    # Step 2: Normalize karo
    normalized = normalize_text(cleaned)
    
    # Step 3: Segment karo
    sections = segment_resume(normalized)
    
    return sections
