"""
Skills Database Module
Comprehensive database of technical and soft skills for extraction from resumes
"""

# Technical skills organized by category
TECHNICAL_SKILLS = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "R", "MATLAB", "Scala", "Perl", "Dart",
        "Objective-C", "Shell", "Bash", "PowerShell", "SQL", "HTML", "CSS"
    ],
    "web_frameworks": [
        "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "Node.js", "Express.js", "Next.js", "Laravel", "Ruby on Rails", "ASP.NET",
        "Svelte", "Nuxt.js", "Gatsby", "jQuery", "Bootstrap", "Tailwind CSS"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j", "Firebase", "MariaDB", "CouchDB",
        "Microsoft SQL Server", "Firestore", "Supabase", "PlanetScale"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud", "GCP", "Heroku", "DigitalOcean",
        "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "CircleCI",
        "GitHub Actions", "GitLab CI", "CloudFormation", "Pulumi", "Vercel", "Netlify"
    ],
    "data_science_ml": [
        "TensorFlow", "PyTorch", "scikit-learn", "Keras", "Pandas", "NumPy",
        "Matplotlib", "Seaborn", "BERT", "GPT", "Hugging Face", "OpenCV",
        "NLTK", "spaCy", "XGBoost", "LightGBM", "CatBoost", "Transformers",
        "LangChain", "LlamaIndex", "Stable Diffusion", "YOLO", "CNN", "RNN", "LSTM"
    ],
    "data_engineering": [
        "Apache Spark", "Hadoop", "Kafka", "Airflow", "dbt", "Tableau",
        "Power BI", "Looker", "Snowflake", "BigQuery", "Databricks", "Redshift",
        "Apache Flink", "Apache Beam", "Prefect", "Dagster", "Metabase"
    ],
    "tools_and_platforms": [
        "Git", "GitHub", "GitLab", "Jira", "Confluence", "Slack", "Jenkins",
        "CircleCI", "Linux", "Unix", "Bash", "PowerShell", "VS Code", "IntelliJ",
        "PyCharm", "Postman", "Figma", "Adobe XD", "Sketch", "Notion", "Trello"
    ]
}

# Soft skills and competencies
SOFT_SKILLS = [
    "Leadership", "Communication", "Problem Solving", "Team Collaboration",
    "Project Management", "Critical Thinking", "Time Management", "Agile",
    "Scrum", "Mentoring", "Analytical Thinking", "Creativity", "Adaptability",
    "Conflict Resolution", "Negotiation", "Public Speaking", "Presentation",
    "Strategic Planning", "Decision Making", "Emotional Intelligence"
]


def get_all_skills_flat():
    """
    Get all skills as a single flat list
    
    Returns:
        list: All technical and soft skills combined
    """
    all_skills = []
    
    # Technical skills se sab categories ko flat list mein add karo
    for category, skills in TECHNICAL_SKILLS.items():
        all_skills.extend(skills)
    
    # Soft skills bhi add karo
    all_skills.extend(SOFT_SKILLS)
    
    return all_skills


def extract_skills_from_text(text: str):
    """
    Extract skills from resume text using case-insensitive matching
    
    Args:
        text (str): Resume text to search for skills
        
    Returns:
        dict: Categorized matched skills
            {
                "technical": {category_name: [matched_skills]},
                "soft": [matched_soft_skills],
                "all_skills_flat": [all matched skills combined]
            }
    """
    if not text:
        return {
            "technical": {},
            "soft": [],
            "all_skills_flat": []
        }
    
    # Text ko lowercase mein convert karo for case-insensitive matching
    text_lower = text.lower()
    
    # Technical skills extract karo by category
    technical_matched = {}
    for category, skills in TECHNICAL_SKILLS.items():
        matched_in_category = []
        for skill in skills:
            # Case-insensitive search - skill ko lowercase mein check karo
            if skill.lower() in text_lower:
                matched_in_category.append(skill)
        
        if matched_in_category:
            technical_matched[category] = matched_in_category
    
    # Soft skills extract karo
    soft_matched = []
    for skill in SOFT_SKILLS:
        if skill.lower() in text_lower:
            soft_matched.append(skill)
    
    # All matched skills ko ek flat list mein combine karo
    all_matched = []
    for skills_list in technical_matched.values():
        all_matched.extend(skills_list)
    all_matched.extend(soft_matched)
    
    return {
        "technical": technical_matched,
        "soft": soft_matched,
        "all_skills_flat": all_matched
    }


def get_skills_by_category(category: str):
    """
    Get skills for a specific technical category
    
    Args:
        category (str): Category name (e.g., 'programming_languages')
        
    Returns:
        list: Skills in that category, or empty list if category not found
    """
    return TECHNICAL_SKILLS.get(category, [])


def get_all_categories():
    """
    Get list of all technical skill categories
    
    Returns:
        list: Category names
    """
    return list(TECHNICAL_SKILLS.keys())
