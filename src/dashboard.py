#!/usr/bin/env python3
"""
Powerlifting Training Insights Dashboard

Streamlit application for visualizing training progression,
volume analysis, and providing actionable insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from datetime import datetime
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Powerlifting Training Insights",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_db_config():
    """Get database configuration from Streamlit secrets or environment variables."""
    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    try:
        # Access secrets directly - will raise exception if not configured
        db_host = st.secrets["database"]["DB_HOST"]
        return {
            'host': db_host,
            'port': int(st.secrets["database"]["DB_PORT"]),
            'database': st.secrets["database"]["DB_NAME"],
            'user': st.secrets["database"]["DB_USER"],
            'password': st.secrets["database"]["DB_PASSWORD"]
        }
    except (KeyError, FileNotFoundError, Exception):
        pass  # No secrets file or missing keys, fall back to environment variables

    # Fall back to environment variables (for local/Docker deployment)
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'database': os.environ.get('DB_NAME', 'training_insights'),
        'user': os.environ.get('DB_USER', 'powerlifter'),
        'password': os.environ.get('DB_PASSWORD', 'stronglifts')
    }


DB_CONFIG = get_db_config()

# Current PRs (confirmed by user)
CURRENT_PRS = {
    'Squat': 220,
    'Bench Press': 135,
    'Sumo Deadlift': 260
}

# Color scheme
COLORS = {
    'Squat': '#FF6B6B',
    'Bench Press': '#4ECDC4',
    'Sumo Deadlift': '#45B7D1',
    'squat': '#FF6B6B',
    'bench': '#4ECDC4',
    'deadlift': '#45B7D1',
    'accessory': '#96CEB4'
}


@st.cache_resource
def get_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=300)
def load_main_lift_data():
    """Load main lift progression data."""
    conn = get_connection()
    query = """
        SELECT
            tw.sequence_order,
            tw.sheet_name,
            e.canonical_name as exercise,
            MAX(ts.actual_weight) as top_weight,
            AVG(ts.actual_rpe) as avg_rpe,
            SUM(ts.sets * COALESCE(ts.reps_numeric, 1) * COALESCE(ts.actual_weight, 0)) as tonnage,
            COUNT(*) as total_sets
        FROM training_sets ts
        JOIN training_sessions tsess ON ts.session_id = tsess.id
        JOIN training_weeks tw ON tsess.week_id = tw.id
        JOIN exercises e ON ts.exercise_id = e.id
        WHERE e.is_main_lift = TRUE
          AND ts.actual_weight IS NOT NULL
          AND ts.data_quality_flag = 'valid'
        GROUP BY tw.sequence_order, tw.sheet_name, e.canonical_name
        ORDER BY tw.sequence_order, e.canonical_name
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_weekly_volume():
    """Load weekly volume summary."""
    conn = get_connection()
    query = """
        SELECT
            tw.sequence_order,
            tw.sheet_name,
            e.category,
            COUNT(DISTINCT tsess.id) as sessions,
            SUM(ts.sets) as total_sets,
            SUM(ts.sets * COALESCE(ts.reps_numeric, 1) * COALESCE(ts.actual_weight, 0)) as tonnage
        FROM training_sets ts
        JOIN training_sessions tsess ON ts.session_id = tsess.id
        JOIN training_weeks tw ON tsess.week_id = tw.id
        JOIN exercises e ON ts.exercise_id = e.id
        WHERE ts.actual_weight IS NOT NULL
          AND ts.reps_numeric IS NOT NULL
        GROUP BY tw.sequence_order, tw.sheet_name, e.category
        ORDER BY tw.sequence_order, e.category
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_rpe_distribution():
    """Load RPE distribution data."""
    conn = get_connection()
    query = """
        SELECT
            ts.actual_rpe,
            e.canonical_name,
            e.is_main_lift,
            e.category
        FROM training_sets ts
        JOIN exercises e ON ts.exercise_id = e.id
        WHERE ts.actual_rpe IS NOT NULL
          AND ts.actual_rpe BETWEEN 1 AND 10
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_accessory_frequency():
    """Load accessory exercise frequency."""
    conn = get_connection()
    query = """
        SELECT
            e.canonical_name,
            e.category,
            COUNT(*) as frequency,
            SUM(ts.sets) as total_sets
        FROM training_sets ts
        JOIN exercises e ON ts.exercise_id = e.id
        WHERE e.is_main_lift = FALSE
        GROUP BY e.canonical_name, e.category
        ORDER BY frequency DESC
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_block_comparison():
    """Load block-by-block comparison data."""
    conn = get_connection()
    query = """
        SELECT
            tb.name as block_name,
            tb.block_type,
            tb.sequence_order as block_order,
            e.canonical_name as exercise,
            MAX(ts.actual_weight) as max_weight,
            AVG(ts.actual_weight) as avg_weight,
            SUM(ts.sets * COALESCE(ts.reps_numeric, 1) * COALESCE(ts.actual_weight, 0)) as tonnage,
            COUNT(*) as total_sets
        FROM training_sets ts
        JOIN training_sessions tsess ON ts.session_id = tsess.id
        JOIN training_weeks tw ON tsess.week_id = tw.id
        JOIN training_blocks tb ON tw.block_id = tb.id
        JOIN exercises e ON ts.exercise_id = e.id
        WHERE e.is_main_lift = TRUE
          AND ts.actual_weight IS NOT NULL
        GROUP BY tb.name, tb.block_type, tb.sequence_order, e.canonical_name
        ORDER BY tb.sequence_order, e.canonical_name
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_training_frequency():
    """Load training frequency data."""
    conn = get_connection()
    query = """
        SELECT
            tw.sequence_order,
            tw.sheet_name,
            COUNT(DISTINCT tsess.id) as sessions_per_week,
            COUNT(DISTINCT CASE WHEN e.category = 'squat' THEN tsess.id END) as squat_sessions,
            COUNT(DISTINCT CASE WHEN e.category = 'bench' THEN tsess.id END) as bench_sessions,
            COUNT(DISTINCT CASE WHEN e.category = 'deadlift' THEN tsess.id END) as deadlift_sessions
        FROM training_weeks tw
        JOIN training_sessions tsess ON tsess.week_id = tw.id
        LEFT JOIN training_sets ts ON ts.session_id = tsess.id
        LEFT JOIN exercises e ON ts.exercise_id = e.id
        GROUP BY tw.sequence_order, tw.sheet_name
        ORDER BY tw.sequence_order
    """
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=300)
def load_data_quality_summary():
    """Load data quality issues summary."""
    conn = get_connection()
    query = """
        SELECT
            issue_type,
            COUNT(*) as count
        FROM data_quality_log
        GROUP BY issue_type
        ORDER BY count DESC
    """
    df = pd.read_sql(query, conn)
    return df


def calculate_e1rm(weight, reps):
    """Calculate estimated 1RM using Epley formula."""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def main():
    # Title
    st.title("🏋️ Powerlifting Training Insights")
    st.markdown("---")

    # Current PRs display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Squat PR", f"{CURRENT_PRS['Squat']} kg", delta=None)
    with col2:
        st.metric("Bench PR", f"{CURRENT_PRS['Bench Press']} kg", delta=None)
    with col3:
        st.metric("Deadlift PR", f"{CURRENT_PRS['Sumo Deadlift']} kg", delta=None)
    with col4:
        total = sum(CURRENT_PRS.values())
        st.metric("Total", f"{total} kg", delta=None)

    st.markdown("---")

    # Sidebar filters
    st.sidebar.header("Filters")

    # Load data
    main_lift_df = load_main_lift_data()
    weekly_volume_df = load_weekly_volume()
    rpe_df = load_rpe_distribution()
    accessory_df = load_accessory_frequency()
    block_df = load_block_comparison()
    frequency_df = load_training_frequency()

    # Week range filter
    max_week = main_lift_df['sequence_order'].max() if not main_lift_df.empty else 0
    if pd.isna(max_week) or max_week == 0:
        st.error("No training data found. Please run the ingestion script first.")
        st.stop()

    week_range = st.sidebar.slider(
        "Week Range",
        min_value=0,
        max_value=int(max_week),
        value=(0, int(max_week)),
        step=1
    )

    # Filter by week range
    main_lift_filtered = main_lift_df[
        (main_lift_df['sequence_order'] >= week_range[0]) &
        (main_lift_df['sequence_order'] <= week_range[1])
    ]

    # Lift selection
    lifts = ['All'] + list(main_lift_df['exercise'].unique())
    selected_lift = st.sidebar.selectbox("Select Lift", lifts)

    # =============================
    # MAIN LIFT PROGRESSION
    # =============================
    st.header("📈 Main Lift Progression")

    if selected_lift == 'All':
        lift_data = main_lift_filtered
    else:
        lift_data = main_lift_filtered[main_lift_filtered['exercise'] == selected_lift]

    # Line chart for progression
    fig_progression = px.line(
        lift_data,
        x='sequence_order',
        y='top_weight',
        color='exercise',
        color_discrete_map=COLORS,
        title='Top Weight by Week',
        labels={'sequence_order': 'Week', 'top_weight': 'Weight (kg)', 'exercise': 'Exercise'},
        markers=True
    )
    fig_progression.update_layout(
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    st.plotly_chart(fig_progression, use_container_width=True)

    # Progression stats
    col1, col2, col3 = st.columns(3)

    for i, lift in enumerate(['Squat', 'Bench Press', 'Sumo Deadlift']):
        lift_progression = main_lift_filtered[main_lift_filtered['exercise'] == lift]
        if not lift_progression.empty:
            first_10 = lift_progression.head(10)['top_weight'].mean()
            last_10 = lift_progression.tail(10)['top_weight'].mean()
            max_weight = lift_progression['top_weight'].max()
            weeks_trained = len(lift_progression)

            if first_10 > 0 and weeks_trained > 1:
                rate = (last_10 - first_10) / weeks_trained
            else:
                rate = 0

            with [col1, col2, col3][i]:
                st.subheader(lift)
                st.write(f"**Max Weight:** {max_weight:.1f} kg")
                st.write(f"**Avg (First 10 wks):** {first_10:.1f} kg")
                st.write(f"**Avg (Last 10 wks):** {last_10:.1f} kg")
                st.write(f"**Progression Rate:** {rate:+.2f} kg/week")

    st.markdown("---")

    # =============================
    # VOLUME ANALYSIS
    # =============================
    st.header("📊 Volume Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Weekly tonnage by category
        volume_filtered = weekly_volume_df[
            (weekly_volume_df['sequence_order'] >= week_range[0]) &
            (weekly_volume_df['sequence_order'] <= week_range[1])
        ]

        # Aggregate by week and category for main lifts
        volume_main = volume_filtered[volume_filtered['category'].isin(['squat', 'bench', 'deadlift'])]

        fig_volume = px.bar(
            volume_main,
            x='sequence_order',
            y='tonnage',
            color='category',
            color_discrete_map=COLORS,
            title='Weekly Tonnage by Lift Category',
            labels={'sequence_order': 'Week', 'tonnage': 'Tonnage (kg)', 'category': 'Category'},
            barmode='stack'
        )
        fig_volume.update_layout(height=400)
        st.plotly_chart(fig_volume, use_container_width=True)

    with col2:
        # Weekly sets distribution
        fig_sets = px.area(
            volume_main.groupby(['sequence_order', 'category'])['total_sets'].sum().reset_index(),
            x='sequence_order',
            y='total_sets',
            color='category',
            color_discrete_map=COLORS,
            title='Weekly Sets by Category',
            labels={'sequence_order': 'Week', 'total_sets': 'Total Sets', 'category': 'Category'}
        )
        fig_sets.update_layout(height=400)
        st.plotly_chart(fig_sets, use_container_width=True)

    st.markdown("---")

    # =============================
    # RPE / INTENSITY ANALYSIS
    # =============================
    st.header("💪 Intensity Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # RPE histogram
        rpe_main = rpe_df[rpe_df['is_main_lift'] == True]

        fig_rpe = px.histogram(
            rpe_main,
            x='actual_rpe',
            color='canonical_name',
            color_discrete_map=COLORS,
            title='RPE Distribution (Main Lifts)',
            labels={'actual_rpe': 'RPE', 'count': 'Frequency', 'canonical_name': 'Exercise'},
            nbins=20,
            barmode='overlay',
            opacity=0.7
        )
        fig_rpe.update_layout(height=400)
        st.plotly_chart(fig_rpe, use_container_width=True)

    with col2:
        # RPE summary stats
        rpe_summary = rpe_main.groupby('canonical_name')['actual_rpe'].agg(['mean', 'std', 'min', 'max']).round(1)
        rpe_summary.columns = ['Mean RPE', 'Std Dev', 'Min', 'Max']
        st.subheader("RPE Statistics (Main Lifts)")
        st.dataframe(rpe_summary, use_container_width=True)

        # Average RPE gauge
        avg_rpe = rpe_main['actual_rpe'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_rpe,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Average Training RPE"},
            gauge={
                'axis': {'range': [0, 10], 'tickwidth': 1},
                'bar': {'color': "#FF6B6B"},
                'steps': [
                    {'range': [0, 5], 'color': "lightgreen"},
                    {'range': [5, 7], 'color': "yellow"},
                    {'range': [7, 8.5], 'color': "orange"},
                    {'range': [8.5, 10], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': avg_rpe
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # =============================
    # BLOCK-BY-BLOCK COMPARISON
    # =============================
    st.header("🔄 Block-by-Block Comparison")

    # Filter out 'Current' reference block
    block_filtered = block_df[block_df['block_name'] != 'Current']

    col1, col2 = st.columns(2)

    with col1:
        # Max weight by block
        fig_block_max = px.bar(
            block_filtered,
            x='block_name',
            y='max_weight',
            color='exercise',
            color_discrete_map=COLORS,
            title='Max Weight by Training Block',
            labels={'block_name': 'Block', 'max_weight': 'Max Weight (kg)', 'exercise': 'Exercise'},
            barmode='group'
        )
        fig_block_max.update_layout(height=400)
        st.plotly_chart(fig_block_max, use_container_width=True)

    with col2:
        # Tonnage by block
        fig_block_tonnage = px.bar(
            block_filtered,
            x='block_name',
            y='tonnage',
            color='exercise',
            color_discrete_map=COLORS,
            title='Total Tonnage by Training Block',
            labels={'block_name': 'Block', 'tonnage': 'Tonnage (kg)', 'exercise': 'Exercise'},
            barmode='group'
        )
        fig_block_tonnage.update_layout(height=400)
        st.plotly_chart(fig_block_tonnage, use_container_width=True)

    st.markdown("---")

    # =============================
    # ACCESSORY WORK
    # =============================
    st.header("🎯 Accessory Work Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Top 15 accessories by frequency
        top_accessories = accessory_df.head(15)

        fig_accessories = px.bar(
            top_accessories,
            y='canonical_name',
            x='frequency',
            color='category',
            color_discrete_map=COLORS,
            title='Top 15 Accessory Exercises by Frequency',
            labels={'canonical_name': 'Exercise', 'frequency': 'Sessions', 'category': 'Category'},
            orientation='h'
        )
        fig_accessories.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_accessories, use_container_width=True)

    with col2:
        # Category distribution pie chart
        category_dist = accessory_df.groupby('category')['frequency'].sum().reset_index()

        fig_pie = px.pie(
            category_dist,
            values='frequency',
            names='category',
            title='Accessory Work by Category',
            color='category',
            color_discrete_map=COLORS
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

        # Volume distribution
        st.subheader("Volume Distribution")
        total_sets_by_cat = accessory_df.groupby('category')['total_sets'].sum()
        st.dataframe(total_sets_by_cat.to_frame('Total Sets'), use_container_width=True)

    st.markdown("---")

    # =============================
    # TRAINING FREQUENCY
    # =============================
    st.header("📅 Training Frequency")

    freq_filtered = frequency_df[
        (frequency_df['sequence_order'] >= week_range[0]) &
        (frequency_df['sequence_order'] <= week_range[1])
    ]

    fig_freq = px.line(
        freq_filtered,
        x='sequence_order',
        y='sessions_per_week',
        title='Training Sessions per Week',
        labels={'sequence_order': 'Week', 'sessions_per_week': 'Sessions'},
        markers=True
    )
    fig_freq.add_hline(
        y=freq_filtered['sessions_per_week'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: {freq_filtered['sessions_per_week'].mean():.1f}"
    )
    fig_freq.update_layout(height=300)
    st.plotly_chart(fig_freq, use_container_width=True)

    # Frequency stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Sessions/Week", f"{freq_filtered['sessions_per_week'].mean():.1f}")
    with col2:
        st.metric("Total Weeks Trained", len(freq_filtered))
    with col3:
        st.metric("Total Sessions", freq_filtered['sessions_per_week'].sum())

    st.markdown("---")

    # =============================
    # INSIGHTS & RECOMMENDATIONS
    # =============================
    st.header("💡 Training Insights & Recommendations")

    # Calculate trends
    squat_data = main_lift_filtered[main_lift_filtered['exercise'] == 'Squat']
    bench_data = main_lift_filtered[main_lift_filtered['exercise'] == 'Bench Press']
    deadlift_data = main_lift_filtered[main_lift_filtered['exercise'] == 'Sumo Deadlift']

    insights = []

    # Progression analysis
    for lift, data, pr in [('Squat', squat_data, 220), ('Bench', bench_data, 135), ('Deadlift', deadlift_data, 260)]:
        if not data.empty:
            last_10_avg = data.tail(10)['top_weight'].mean()
            first_10_avg = data.head(10)['top_weight'].mean()
            progress_pct = ((last_10_avg - first_10_avg) / first_10_avg * 100) if first_10_avg > 0 else 0

            if progress_pct > 15:
                insights.append(f"✅ **{lift}** showing excellent progress ({progress_pct:.1f}% improvement)")
            elif progress_pct > 5:
                insights.append(f"📈 **{lift}** showing steady progress ({progress_pct:.1f}% improvement)")
            elif progress_pct < 0:
                insights.append(f"⚠️ **{lift}** may need attention (recent weights down from initial average)")

    # RPE analysis
    avg_rpe = rpe_df[rpe_df['is_main_lift'] == True]['actual_rpe'].mean()
    if avg_rpe > 8.5:
        insights.append(f"⚠️ **High average RPE ({avg_rpe:.1f})** - Consider incorporating more submaximal work")
    elif avg_rpe < 7:
        insights.append(f"💪 **Conservative RPE ({avg_rpe:.1f})** - Room to push harder if recovery allows")
    else:
        insights.append(f"✅ **Balanced intensity ({avg_rpe:.1f} avg RPE)** - Good training zone")

    # Volume analysis
    total_weekly_volume = weekly_volume_df[
        weekly_volume_df['category'].isin(['squat', 'bench', 'deadlift'])
    ].groupby('sequence_order')['tonnage'].sum()

    recent_volume = total_weekly_volume.tail(10).mean()
    early_volume = total_weekly_volume.head(10).mean()

    if recent_volume > early_volume * 1.2:
        insights.append(f"📊 **Volume trending up** - Recent weeks averaging {recent_volume:.0f} kg vs {early_volume:.0f} kg early")
    elif recent_volume < early_volume * 0.8:
        insights.append(f"📉 **Volume decreased** - May be tapering or deload phase")

    # Frequency analysis
    avg_sessions = freq_filtered['sessions_per_week'].mean()
    if avg_sessions >= 4:
        insights.append(f"🔥 **High training frequency** ({avg_sessions:.1f} sessions/week) - Ensure adequate recovery")
    elif avg_sessions < 3:
        insights.append(f"📅 **Lower frequency** ({avg_sessions:.1f} sessions/week) - Consider adding sessions if schedule allows")

    # Display insights
    for insight in insights:
        st.write(insight)

    st.markdown("---")

    # Recommendations
    st.subheader("🎯 Recommendations Based on Your Data")

    recommendations = []

    # Check bench vs other lifts ratio
    if CURRENT_PRS['Bench Press'] / CURRENT_PRS['Squat'] < 0.6:
        recommendations.append("**Bench Press Focus:** Your bench (135kg) is about 61% of your squat (220kg). "
                              "This is slightly below typical powerlifter ratios (65-75%). Consider prioritizing bench volume.")

    # Check deadlift vs squat ratio
    dl_sq_ratio = CURRENT_PRS['Sumo Deadlift'] / CURRENT_PRS['Squat']
    if dl_sq_ratio > 1.2:
        recommendations.append(f"**Deadlift Dominant:** Your deadlift is {dl_sq_ratio:.0%} of squat. "
                              "Strong pulling! Squat may have more room for improvement.")

    # Competition total projection
    total = sum(CURRENT_PRS.values())
    recommendations.append(f"**Current Total:** {total}kg. With continued progression, a 650kg total "
                          "(~230/140/280) appears achievable in the next training cycle.")

    for rec in recommendations:
        st.info(rec)

    st.markdown("---")

    # =============================
    # DATA QUALITY
    # =============================
    with st.expander("📋 Data Quality Summary"):
        quality_df = load_data_quality_summary()
        if not quality_df.empty:
            st.write("The following data quality issues were flagged during ingestion:")
            st.dataframe(quality_df, use_container_width=True)
        else:
            st.write("No data quality issues logged.")

        st.write(f"\n**Total weeks in database:** 77")
        st.write(f"**Total training sessions:** {frequency_df['sessions_per_week'].sum()}")


if __name__ == '__main__':
    main()
