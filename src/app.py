#!/usr/bin/env python3
"""
Powerlifting Training Insights Dashboard v2

A beautiful, intuitive dashboard that anyone can understand.
Uses dates instead of weeks, provides plain-English interpretations,
and breaks down metrics by lift.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from data_processor import (
    load_training_data,
    get_main_lift_data,
    get_lift_specific_data,
    get_weekly_volume,
    get_rpe_distribution,
    get_rpe_by_lift,
    get_accessory_frequency,
    get_accessory_by_category,
    get_block_comparison,
    get_training_frequency,
    get_summary_stats,
    get_insights,
    get_current_prs,
    get_pr_history,
    get_skipped_exercises,
    get_monthly_summary,
    COLORS,
    GOAL_PRS
)

from interpretations import (
    interpret_rpe,
    interpret_rpe_average,
    interpret_bench_squat_ratio,
    interpret_deadlift_squat_ratio,
    interpret_tonnage,
    interpret_goal_progress,
    interpret_consistency,
    interpret_sessions_per_week,
    interpret_skipped_lift,
    TERM_DEFINITIONS
)

# Page configuration
st.set_page_config(
    page_title="Training Insights",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hero cards */
    .hero-card {
        background: linear-gradient(135deg, var(--color1) 0%, var(--color2) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .hero-card h2 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: white !important;
    }

    .hero-card p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }

    /* Metric interpretation */
    .interpretation {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Insight cards */
    .insight-high {
        background: #FFF5F5;
        border-left: 4px solid #FF6B6B;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }

    .insight-medium {
        background: #FFF8F0;
        border-left: 4px solid #FFA94D;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }

    .insight-low {
        background: #F0FFF4;
        border-left: 4px solid #51CF66;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }

    /* Definition tooltip */
    .definition {
        color: #667eea;
        border-bottom: 1px dotted #667eea;
        cursor: help;
    }

    /* Section headers */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }

    /* Lift section cards */
    .lift-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* RPE zones */
    .rpe-easy { color: #51CF66; }
    .rpe-moderate { color: #FCC419; }
    .rpe-hard { color: #FF6B6B; }
</style>
""", unsafe_allow_html=True)


def format_weight(w):
    """Format weight preserving .5kg increments."""
    if w is None or pd.isna(w):
        return "—"
    if w == int(w):
        return f"{int(w)}"
    return f"{w:.1f}"


def create_header(stats):
    """Create the header with title and date range."""
    st.markdown("# 🏋️ Powerlifting Training Insights")

    start = stats['start_date'].strftime('%B %Y')
    end = stats['end_date'].strftime('%B %Y')
    months = int(stats['training_duration_months'])

    st.markdown(f"""
    *{months} months of training data ({start} - {end}) • {stats['total_weeks']} weeks • {stats['total_sessions']} sessions*
    """)


def create_hero_section(stats):
    """Create hero section with current PRs and goals."""
    prs = stats['current_prs']

    st.markdown("---")

    # Main lift PRs with progress to goal
    col1, col2, col3, col4 = st.columns(4)

    lifts = [
        ('Squat', '#FF6B6B', '#FF8E8E'),
        ('Bench Press', '#4ECDC4', '#6EE7DF'),
        ('Deadlift', '#45B7D1', '#65D7F1'),
    ]

    # Get progress data for trend indicators
    lift_progress = {}
    for lift, _, _ in lifts:
        lift_data = get_lift_specific_data(lift)
        if lift_data and lift_data['first_10_avg'] and lift_data['last_10_avg']:
            gain = lift_data['last_10_avg'] - lift_data['first_10_avg']
            lift_progress[lift] = gain

    for col, (lift, c1, c2) in zip([col1, col2, col3], lifts):
        with col:
            pr = prs.get(lift, 0)
            goal = GOAL_PRS.get(lift, pr)
            progress = min(100, (pr / goal) * 100) if goal > 0 else 0
            goal_info = interpret_goal_progress(pr, goal, lift)

            # Get trend
            gain = lift_progress.get(lift, 0)
            trend = "↑" if gain > 0 else ("↓" if gain < 0 else "→")
            trend_text = f"+{gain:.0f}kg" if gain > 0 else (f"{gain:.0f}kg" if gain < 0 else "stable")

            st.markdown(f"""
            <div class="hero-card" style="--color1: {c1}; --color2: {c2};">
                <h2>{format_weight(pr)} kg</h2>
                <p>{lift}</p>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">{trend} {trend_text}</p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(progress / 100)
            st.caption(f"{goal_info['emoji']} {progress:.0f}% to {goal}kg goal")

    with col4:
        total = stats['total_pr']
        total_goal = sum(GOAL_PRS.values())
        progress = min(100, (total / total_goal) * 100)

        # Calculate total trend
        total_gain = sum(lift_progress.values())
        total_trend = "↑" if total_gain > 0 else ("↓" if total_gain < 0 else "→")
        total_trend_text = f"+{total_gain:.0f}kg" if total_gain > 0 else (f"{total_gain:.0f}kg" if total_gain < 0 else "stable")

        st.markdown(f"""
        <div class="hero-card" style="--color1: #667eea; --color2: #764ba2;">
            <h2>{format_weight(total)} kg</h2>
            <p>Total</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">{total_trend} {total_trend_text}</p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(progress / 100)
        st.caption(f"🎯 {progress:.0f}% to {total_goal}kg goal")


def create_summary_interpretation(stats):
    """Create a plain-English summary of training."""
    st.markdown("### 📝 What This Means")

    total_tonnage = stats['volume_squat'] + stats['volume_bench'] + stats['volume_deadlift']
    tonnage_text = interpret_tonnage(total_tonnage)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="interpretation">
        <strong>Your Training Journey</strong><br><br>

        Over the past **{int(stats['training_duration_months'])} months**, you've:
        <ul>
            <li>Trained **{stats['total_weeks']} weeks** with {stats['total_sessions']} total sessions</li>
            <li>Averaged **{stats['avg_sessions_per_week']:.1f} sessions per week**</li>
            <li>Lifted {tonnage_text}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # RPE interpretation
        rpe_interp = interpret_rpe(stats['mean_rpe'])
        st.markdown(f"""
        <div class="interpretation">
        <strong>Training Intensity</strong><br><br>

        Your average effort level is **{stats['mean_rpe']:.1f}/10** ({rpe_interp['level']}).<br><br>

        {rpe_interp['meaning']}<br><br>

        <em>{rpe_interp['implication']}</em>
        </div>
        """, unsafe_allow_html=True)


def create_lift_section(lift: str, color: str):
    """Create a detailed section for a single lift."""
    lift_data = get_lift_specific_data(lift)
    if not lift_data:
        return

    st.markdown(f"### {lift}")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Progress chart with monthly data for cleaner view
        monthly = lift_data['monthly']
        if not monthly.empty:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=monthly['month'],
                y=monthly['actual_weight'],
                mode='lines+markers',
                name='Monthly Best',
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate="<b>%{x}</b><br>Best: %{y:.1f} kg<extra></extra>"
            ))

            # Add trend line
            if len(monthly) > 3:
                z = np.polyfit(range(len(monthly)), monthly['actual_weight'], 1)
                p = np.poly1d(z)
                fig.add_trace(go.Scatter(
                    x=monthly['month'],
                    y=p(range(len(monthly))),
                    mode='lines',
                    name='Trend',
                    line=dict(color=color, width=1, dash='dash'),
                    hoverinfo='skip'
                ))

            # Add PR line
            fig.add_hline(
                y=lift_data['pr'],
                line_dash="dot",
                line_color="gold",
                annotation_text=f"PR: {format_weight(lift_data['pr'])}kg",
                annotation_position="right"
            )

            fig.update_layout(
                height=300,
                xaxis_title="Month",
                yaxis_title="Weight (kg)",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=20, t=30, b=50),
                xaxis=dict(tickangle=-45)
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Key stats
        st.metric("Personal Record", f"{format_weight(lift_data['pr'])} kg")

        # Progress interpretation
        if lift_data['first_10_avg'] and lift_data['last_10_avg']:
            gain = lift_data['last_10_avg'] - lift_data['first_10_avg']
            gain_pct = (gain / lift_data['first_10_avg']) * 100 if lift_data['first_10_avg'] > 0 else 0
            st.metric(
                "Progress",
                f"+{gain:.1f} kg",
                f"{gain_pct:.0f}% improvement"
            )

        # RPE breakdown
        if lift_data['mean_rpe']:
            rpe_info = interpret_rpe(lift_data['mean_rpe'])
            st.markdown(f"""
            **Avg Effort:** {lift_data['mean_rpe']:.1f}/10 ({rpe_info['level']})

            - Easy sets: {lift_data['rpe_low_pct']:.0f}%
            - Moderate: {lift_data['rpe_mid_pct']:.0f}%
            - Hard sets: {lift_data['rpe_high_pct']:.0f}%
            """)


def create_lift_comparison(stats):
    """Create lift ratio analysis."""
    st.markdown("### ⚖️ Are Your Lifts Balanced?")

    st.markdown("""
    *In powerlifting, certain ratios between lifts indicate balanced strength development.
    Here's how your lifts compare:*
    """)

    prs = stats['current_prs']
    squat = prs.get('Squat', 220)
    bench = prs.get('Bench Press', 135)
    deadlift = prs.get('Deadlift', 262.5)

    col1, col2 = st.columns(2)

    with col1:
        # Bench vs Squat
        bench_ratio = interpret_bench_squat_ratio(bench, squat)

        status_color = {
            'needs_attention': '#FF6B6B',
            'developing': '#FFA94D',
            'balanced': '#51CF66',
            'bench_dominant': '#74C0FC'
        }[bench_ratio['status']]

        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {status_color};">
        <h4>{bench_ratio['emoji']} Bench Press vs Squat</h4>
        <p>{bench_ratio['detail']}</p>
        <p><strong>→ {bench_ratio['action']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Deadlift vs Squat
        dl_ratio = interpret_deadlift_squat_ratio(deadlift, squat)

        status_color = {
            'squat_dominant': '#FFA94D',
            'balanced': '#51CF66',
            'deadlift_dominant': '#74C0FC'
        }[dl_ratio['status']]

        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {status_color};">
        <h4>{dl_ratio['emoji']} Deadlift vs Squat</h4>
        <p>{dl_ratio['detail']}</p>
        <p><strong>→ {dl_ratio['action']}</strong></p>
        </div>
        """, unsafe_allow_html=True)


def create_training_consistency(stats, freq_df):
    """Create training consistency section."""
    st.markdown("### 📅 Training Consistency")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Monthly training frequency
        monthly = get_monthly_summary()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=monthly['month_label'],
            y=monthly['week_order'],
            marker_color='#667eea',
            hovertemplate="<b>%{x}</b><br>Weeks trained: %{y}<extra></extra>"
        ))

        avg_weeks = monthly['week_order'].mean()
        fig.add_hline(
            y=avg_weeks,
            line_dash="dash",
            line_color="#FF6B6B",
            annotation_text=f"Avg: {avg_weeks:.1f} weeks/month"
        )

        fig.update_layout(
            height=250,
            xaxis_title="Month",
            yaxis_title="Weeks Trained",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=20, t=20, b=50),
            xaxis=dict(tickangle=-45)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Consistency stats
        consistency_text = interpret_consistency(stats['total_weeks'], 81)
        freq_text = interpret_sessions_per_week(stats['avg_sessions_per_week'])

        st.markdown(f"""
        <div class="interpretation">
        {consistency_text}
        <br><br>
        {freq_text}
        </div>
        """, unsafe_allow_html=True)


def create_skipped_sessions():
    """Show skipped sessions in a helpful way."""
    skipped = get_skipped_exercises()

    if skipped.empty:
        st.success("🎉 **Perfect consistency!** You haven't skipped any planned main lifts.")
        return

    st.markdown("### ⏭️ Skipped Sessions")

    st.markdown("""
    *These are sessions where a main lift was planned but not completed.
    Everyone misses sessions sometimes - what matters is the overall pattern.*
    """)

    # Summary by lift
    skip_counts = skipped.groupby('exercise').size().to_dict()

    col1, col2, col3 = st.columns(3)

    for col, lift in zip([col1, col2, col3], ['Squat', 'Bench Press', 'Deadlift']):
        with col:
            count = skip_counts.get(lift, 0)
            interpretation = interpret_skipped_lift(lift, count, 81)
            st.markdown(f"""
            **{lift}**: {count} skipped

            {interpretation}
            """)


def create_accessory_analysis():
    """Create accessory exercise analysis."""
    st.markdown("### 🎯 Supporting Exercises")

    st.markdown("""
    *Accessory exercises support your main lifts by strengthening weak points
    and building muscle. Here's your focus:*
    """)

    accessories_by_cat = get_accessory_by_category()

    cols = st.columns(3)

    important_cats = ['Back', 'Arms', 'Legs', 'Core']

    for i, cat in enumerate(important_cats[:3]):
        with cols[i]:
            if cat in accessories_by_cat:
                cat_data = accessories_by_cat[cat].head(3)
                st.markdown(f"**{cat}**")
                for _, row in cat_data.iterrows():
                    # Clean up exercise name
                    name = row['canonical_name']
                    if len(name) > 25:
                        name = name[:22] + "..."
                    st.markdown(f"• {name}")


def create_insights_section():
    """Create actionable insights section."""
    st.markdown("### 💡 Key Insights & Recommendations")

    insights = get_insights()

    # Group by priority
    high = [i for i in insights if i['priority'] == 'high']
    medium = [i for i in insights if i['priority'] == 'medium']
    low = [i for i in insights if i['priority'] == 'low']

    if high:
        st.markdown("#### 🔴 Priority Actions")
        for insight in high:
            st.markdown(f"""
            <div class="insight-high">
            <strong>{insight['title']}</strong><br>
            {insight['message']}
            </div>
            """, unsafe_allow_html=True)

    if medium:
        st.markdown("#### 🟡 Suggested Improvements")
        for insight in medium:
            st.markdown(f"""
            <div class="insight-medium">
            <strong>{insight['title']}</strong><br>
            {insight['message']}
            </div>
            """, unsafe_allow_html=True)

    if low:
        st.markdown("#### 🟢 What's Working")
        for insight in low:
            st.markdown(f"""
            <div class="insight-low">
            <strong>{insight['title']}</strong><br>
            {insight['message']}
            </div>
            """, unsafe_allow_html=True)


def create_glossary():
    """Create a glossary of powerlifting terms."""
    with st.expander("📖 Glossary - What Do These Terms Mean?"):
        for term, definition in TERM_DEFINITIONS.items():
            st.markdown(f"**{term}**: {definition}")


def main():
    """Main application."""
    try:
        # Load all data
        stats = get_summary_stats()
        freq_df = get_training_frequency()

        # Create sections
        create_header(stats)
        create_hero_section(stats)

        st.markdown("---")
        create_summary_interpretation(stats)

        st.markdown("---")
        st.markdown("## 📊 Your Lifts in Detail")

        # Individual lift sections
        for lift, color in [('Squat', '#FF6B6B'), ('Bench Press', '#4ECDC4'), ('Deadlift', '#45B7D1')]:
            create_lift_section(lift, color)
            st.markdown("---")

        create_lift_comparison(stats)

        st.markdown("---")
        create_training_consistency(stats, freq_df)

        st.markdown("---")
        create_skipped_sessions()

        st.markdown("---")
        create_accessory_analysis()

        st.markdown("---")
        create_insights_section()

        st.markdown("---")
        create_glossary()

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #999; padding: 1rem 0;">
            <p>Built for powerlifters who want to understand their progress</p>
            <p style="font-size: 0.8rem;">Data updates automatically when you add new training weeks</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the training data file exists.")
        import traceback
        st.code(traceback.format_exc())


if __name__ == '__main__':
    main()
