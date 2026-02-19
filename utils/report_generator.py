"""
PDF Report Generator Module
Generate professional PDF screening reports using ReportLab
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import pandas as pd


def generate_pdf_report(results_df: pd.DataFrame, jd_analysis: dict, job_description: str) -> bytes:
    """
    Generate professional PDF screening report
    
    Args:
        results_df (pd.DataFrame): Processed results dataframe
        jd_analysis (dict): Extracted JD requirements
        job_description (str): Original job description
        
    Returns:
        bytes: PDF file as bytes
    """
    # BytesIO buffer banao
    buffer = BytesIO()
    
    # PDF document setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles define karo
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Story (content) list banao
    story = []
    
    # === PAGE 1: SUMMARY ===
    
    # Title
    title = Paragraph("📋 Resume Screening Report", title_style)
    story.append(title)
    
    # Date
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(date_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Job Title
    job_title = jd_analysis.get('job_title', 'Position')[:100]
    story.append(Paragraph(f"<b>Position:</b> {job_title}", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Requirements
    story.append(Paragraph("Key Requirements:", heading_style))
    
    req_text = f"""
    • <b>Required Skills:</b> {len(jd_analysis.get('required_skills', []))} skills identified<br/>
    • <b>Minimum Experience:</b> {jd_analysis.get('min_experience_years', 0)} years<br/>
    • <b>Education:</b> {jd_analysis.get('education_requirement', 'Not specified')}<br/>
    """
    story.append(Paragraph(req_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary Statistics
    story.append(Paragraph("Summary Statistics:", heading_style))
    
    total_screened = len(results_df)
    avg_score = results_df['final_score'].mean()
    top_score = results_df['final_score'].max()
    shortlisted = len(results_df[results_df['grade'].isin(['A', 'B'])])
    
    stats_text = f"""
    • <b>Total Resumes Screened:</b> {total_screened}<br/>
    • <b>Average Match Score:</b> {avg_score:.1f}%<br/>
    • <b>Top Score:</b> {top_score:.1f}%<br/>
    • <b>Shortlisted (A+B grades):</b> {shortlisted} candidates<br/>
    """
    story.append(Paragraph(stats_text, normal_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Top 5 Candidates Table
    story.append(Paragraph("🏆 Top 5 Candidates:", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Top 5 ka data prepare karo
    top5 = results_df.head(5)
    
    table_data = [['Rank', 'Name', 'Grade', 'Score', 'Skills Match', 'Experience']]
    
    for idx, row in top5.iterrows():
        table_data.append([
            str(row['rank']),
            str(row['name'])[:25],
            str(row['grade']),
            f"{row['final_score']:.1f}%",
            f"{row['skills_score']:.0f}%",
            f"{row['experience_years']:.1f} yrs"
        ])
    
    # Table banao
    table = Table(table_data, colWidths=[0.6*inch, 2*inch, 0.6*inch, 0.8*inch, 1*inch, 1*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(table)
    story.append(PageBreak())
    
    # === PAGE 2+: INDIVIDUAL CANDIDATE DETAILS ===
    
    for idx, row in results_df.head(10).iterrows():  # Top 10 candidates
        story.append(Paragraph(f"Candidate #{row['rank']}: {row['name']}", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Basic Info
        info_text = f"""
        <b>Email:</b> {row.get('email', 'N/A')}<br/>
        <b>Phone:</b> {row.get('phone', 'N/A')}<br/>
        <b>Experience:</b> {row['experience_years']:.1f} years<br/>
        <b>Total Skills:</b> {row['total_skills_count']}<br/>
        """
        story.append(Paragraph(info_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Scores
        story.append(Paragraph("Score Breakdown:", ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')))
        
        scores_text = f"""
        • <b>Final Score:</b> {row['final_score']:.1f}% (Grade: {row['grade']})<br/>
        • <b>Semantic Match:</b> {row['semantic_score']:.1f}%<br/>
        • <b>Skills Match:</b> {row['skills_score']:.1f}%<br/>
        • <b>Experience Match:</b> {row['experience_score']:.1f}%<br/>
        • <b>Education Match:</b> {row['education_score']:.1f}%<br/>
        """
        story.append(Paragraph(scores_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Matched Skills
        matched_skills = row.get('matched_skills', [])
        if matched_skills:
            matched_text = "✅ <b>Matched Skills:</b> " + ", ".join(matched_skills[:10])
            story.append(Paragraph(matched_text, normal_style))
            story.append(Spacer(1, 0.1*inch))
        
        # Missing Skills
        missing_skills = row.get('missing_skills', [])
        if missing_skills:
            missing_text = "❌ <b>Missing Skills:</b> " + ", ".join(missing_skills[:10])
            story.append(Paragraph(missing_text, normal_style))
            story.append(Spacer(1, 0.1*inch))
        
        # Recommendation
        story.append(Paragraph(f"<b>Recommendation:</b> {row['recommendation']}", normal_style))
        
        # Page break after every 2 candidates
        if idx % 2 == 1:
            story.append(PageBreak())
        else:
            story.append(Spacer(1, 0.5*inch))
    
    # Build PDF
    doc.build(story)
    
    # Buffer se bytes nikalo
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
