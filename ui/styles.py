"""
Custom CSS Styling for Streamlit Application
Professional dark/light theme compatible design
"""

CUSTOM_CSS = """
<style>
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Header styling with gradient text */
    .app-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Metric cards with gradient backgrounds */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    }
    
    /* Grade badges - color coded pills */
    .grade-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .grade-A {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .grade-B {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
    }
    
    .grade-C {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }
    
    .grade-D {
        background: linear-gradient(135deg, #fa709a, #fee140);
        color: white;
    }
    
    .grade-F {
        background: linear-gradient(135deg, #eb3349, #f45c43);
        color: white;
    }
    
    /* Skill pills */
    .skill-pill {
        display: inline-block;
        padding: 0.4rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .skill-matched {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .skill-missing {
        background: linear-gradient(135deg, #eb3349, #f45c43);
        color: white;
    }
    
    /* Progress bars */
    .progress-bar {
        width: 100%;
        height: 25px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 15px;
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px dashed rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: rgba(102, 126, 234, 0.05);
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(102, 126, 234, 0.1);
        transition: background-color 0.2s ease;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    
    .stError {
        background: linear-gradient(135deg, #eb3349, #f45c43);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(235, 51, 73, 0.3);
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Card containers */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Recommendation boxes */
    .recommendation-box {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .recommendation-strong {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .recommendation-good {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
    }
    
    .recommendation-average {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }
    
    .recommendation-poor {
        background: linear-gradient(135deg, #eb3349, #f45c43);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
</style>
"""


def get_custom_css():
    """Return custom CSS string for Streamlit"""
    return CUSTOM_CSS


def create_grade_badge_html(grade: str) -> str:
    """
    Create HTML for grade badge
    
    Args:
        grade (str): Grade letter (A, B, C, D, F)
        
    Returns:
        str: HTML string for badge
    """
    return f'<span class="grade-badge grade-{grade}">{grade}</span>'


def create_skill_pill_html(skill: str, matched: bool = True) -> str:
    """
    Create HTML for skill pill
    
    Args:
        skill (str): Skill name
        matched (bool): Whether skill is matched or missing
        
    Returns:
        str: HTML string for pill
    """
    pill_class = "skill-matched" if matched else "skill-missing"
    return f'<span class="skill-pill {pill_class}">{skill}</span>'


def create_recommendation_box_html(grade: str, recommendation: str) -> str:
    """
    Create HTML for recommendation box
    
    Args:
        grade (str): Grade letter
        recommendation (str): Recommendation text
        
    Returns:
        str: HTML string for recommendation box
    """
    if grade in ['A', 'B']:
        box_class = "recommendation-strong" if grade == 'A' else "recommendation-good"
        icon = "✅"
    elif grade == 'C':
        box_class = "recommendation-average"
        icon = "⚠️"
    else:
        box_class = "recommendation-poor"
        icon = "❌"
    
    return f'<div class="recommendation-box {box_class}">{icon} {recommendation}</div>'
