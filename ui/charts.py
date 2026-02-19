"""
Visualization Charts Module
All Plotly charts for the dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def plot_candidate_ranking_bar(df: pd.DataFrame):
    """
    Horizontal bar chart of candidates ranked by score
    
    Args:
        df (pd.DataFrame): Results dataframe
        
    Returns:
        plotly.Figure: Bar chart
    """
    # Grade se color mapping
    color_map = {
        'A': '#38ef7d',  # Green
        'B': '#00f2fe',  # Blue
        'C': '#f5576c',  # Pink
        'D': '#fee140',  # Yellow
        'F': '#f45c43'   # Red
    }
    
    # Colors assign karo based on grade
    colors = [color_map.get(grade, '#667eea') for grade in df['grade']]
    
    # Top 10 candidates tak limit karo for readability
    df_plot = df.head(10).copy()
    colors = colors[:10]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_plot['final_score'],
            y=df_plot['name'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.3)', width=2)
            ),
            text=df_plot['final_score'].round(1),
            textposition='outside',
            textfont=dict(size=12, color='white', family='Arial Black'),
            hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<br>Grade: %{customdata}<extra></extra>',
            customdata=df_plot['grade']
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🏆 Top Candidate Rankings',
            'font': {'size': 24, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Match Score (%)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400,
        margin=dict(l=150, r=50, t=80, b=50),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            range=[0, 100]
        ),
        yaxis=dict(
            categoryorder='total ascending'
        )
    )
    
    return fig


def plot_score_breakdown_radar(candidate_data: dict):
    """
    Radar/Spider chart showing score breakdown for one candidate
    
    Args:
        candidate_data (dict): Single candidate's data
        
    Returns:
        plotly.Figure: Radar chart
    """
    categories = ['Semantic<br>Match', 'Skills<br>Match', 'Experience<br>Match', 'Education<br>Match']
    
    values = [
        candidate_data.get('semantic_score', 0),
        candidate_data.get('skills_score', 0),
        candidate_data.get('experience_score', 0),
        candidate_data.get('education_score', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.4)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2'),
        name=candidate_data.get('name', 'Candidate')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.3)',
                tickfont=dict(color='white')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.3)',
                linecolor='rgba(255,255,255,0.5)'
            ),
            bgcolor='rgba(0,0,0,0.1)'
        ),
        showlegend=False,
        title={
            'text': f"📊 Score Breakdown — {candidate_data.get('name', 'Candidate')}",
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400
    )
    
    return fig


def plot_skills_heatmap(all_candidates: list, required_skills: list):
    """
    Heatmap showing which candidates have which required skills
    
    Args:
        all_candidates (list): List of candidate dicts
        required_skills (list): List of required skills
        
    Returns:
        plotly.Figure: Heatmap
    """
    if not required_skills or not all_candidates:
        # Empty heatmap
        fig = go.Figure()
        fig.add_annotation(
            text="No required skills detected in job description",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='white')
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        return fig
    
    # Top 10 required skills tak limit karo
    required_skills = required_skills[:10]
    
    # Matrix banao: rows=candidates, columns=skills
    candidate_names = [c.get('name', 'Unknown')[:20] for c in all_candidates[:10]]
    
    matrix = []
    for candidate in all_candidates[:10]:
        matched_skills_lower = [s.lower() for s in candidate.get('matched_skills', [])]
        row = []
        for skill in required_skills:
            # Check karo agar candidate ke paas ye skill hai
            has_skill = any(skill.lower() in ms or ms in skill.lower() for ms in matched_skills_lower)
            row.append(1 if has_skill else 0)
        matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=required_skills,
        y=candidate_names,
        colorscale=[[0, '#f45c43'], [1, '#38ef7d']],  # Red to Green
        showscale=False,
        hovertemplate='Candidate: %{y}<br>Skill: %{x}<br>Has Skill: %{customdata}<extra></extra>',
        customdata=[['✅' if val == 1 else '❌' for val in row] for row in matrix]
    ))
    
    fig.update_layout(
        title={
            'text': '🔥 Skills Heatmap — Candidate × Required Skills',
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Required Skills',
        yaxis_title='Candidates',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        height=400,
        xaxis=dict(tickangle=-45)
    )
    
    return fig


def plot_score_distribution(df: pd.DataFrame):
    """
    Histogram showing distribution of scores across all candidates
    
    Args:
        df (pd.DataFrame): Results dataframe
        
    Returns:
        plotly.Figure: Histogram
    """
    fig = go.Figure()
    
    # Histogram banao
    fig.add_trace(go.Histogram(
        x=df['final_score'],
        nbinsx=20,
        marker=dict(
            color='#667eea',
            line=dict(color='white', width=1)
        ),
        hovertemplate='Score Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Grade threshold lines add karo
    thresholds = [
        (80, 'A', '#38ef7d'),
        (65, 'B', '#00f2fe'),
        (50, 'C', '#f5576c'),
        (35, 'D', '#fee140')
    ]
    
    for threshold, grade, color in thresholds:
        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color=color,
            line_width=2,
            annotation_text=f"Grade {grade}",
            annotation_position="top",
            annotation_font_color=color
        )
    
    fig.update_layout(
        title={
            'text': '📈 Score Distribution',
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Match Score (%)',
        yaxis_title='Number of Candidates',
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400,
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            range=[0, 100]
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)'
        )
    )
    
    return fig


def plot_experience_vs_score(df: pd.DataFrame):
    """
    Scatter plot: Experience vs Score with bubble size = skills count
    
    Args:
        df (pd.DataFrame): Results dataframe
        
    Returns:
        plotly.Figure: Scatter plot
    """
    # Grade se color mapping
    color_map = {
        'A': '#38ef7d',
        'B': '#00f2fe',
        'C': '#f5576c',
        'D': '#fee140',
        'F': '#f45c43'
    }
    
    colors = [color_map.get(grade, '#667eea') for grade in df['grade']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['experience_years'],
        y=df['final_score'],
        mode='markers',
        marker=dict(
            size=df['total_skills_count'],
            sizemode='diameter',
            sizeref=2,
            sizemin=5,
            color=colors,
            line=dict(color='white', width=2),
            opacity=0.8
        ),
        text=df['name'],
        hovertemplate='<b>%{text}</b><br>Experience: %{x} years<br>Score: %{y:.1f}%<br>Skills: %{marker.size}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '💼 Experience vs Match Score',
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Years of Experience',
        yaxis_title='Match Score (%)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400,
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            range=[0, 100]
        )
    )
    
    return fig


def plot_skills_overlap_donut(candidate_skills: list, required_skills: list):
    """
    Donut chart showing matched vs missing skills
    
    Args:
        candidate_skills (list): Candidate's skills
        required_skills (list): Required skills from JD
        
    Returns:
        plotly.Figure: Donut chart
    """
    if not required_skills:
        # No required skills
        labels = ['Candidate Skills']
        values = [len(candidate_skills)]
        colors = ['#667eea']
    else:
        # Calculate matched and missing
        matched_count = 0
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        
        for req_skill in required_skills:
            if any(req_skill.lower() in cs or cs in req_skill.lower() for cs in candidate_skills_lower):
                matched_count += 1
        
        missing_count = len(required_skills) - matched_count
        
        labels = ['✅ Matched Skills', '❌ Missing Skills']
        values = [matched_count, missing_count]
        colors = ['#38ef7d', '#f45c43']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Center text add karo
    if required_skills:
        match_percent = (values[0] / sum(values) * 100) if sum(values) > 0 else 0
        center_text = f"{match_percent:.0f}%<br>Match"
    else:
        center_text = "N/A"
    
    fig.add_annotation(
        text=center_text,
        x=0.5, y=0.5,
        font=dict(size=24, color='white', family='Arial Black'),
        showarrow=False
    )
    
    fig.update_layout(
        title={
            'text': '🎯 Skills Match Overview',
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig
