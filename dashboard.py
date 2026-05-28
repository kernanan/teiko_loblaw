import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

from analysis import (
    get_frequency_table,
    get_melanoma_miraclib_frequencies,
    get_baseline_subset_analysis,
    run_statistical_comparison,
    CELL_COLS,
)

st.set_page_config(page_title="Loblaw Bio — Immune Cell Trial Dashboard")
st.title("Loblaw Bio — Immune Cell Trial Dashboard")

with st.sidebar:
    db_path = st.text_input("Database path", value="clinical_trial.db")
    st.caption("Run `python load_data.py` first if the database doesn't exist.")

st.session_state["db_path"] = db_path

if not os.path.exists(db_path):
    st.warning(f"Database file '{db_path}' not found. Run `python load_data.py` to create it.")
    st.stop()


@st.cache_data
def cached_get_frequency_table(db_path):
    return get_frequency_table(db_path)


@st.cache_data
def cached_get_melanoma_miraclib_frequencies(db_path):
    return get_melanoma_miraclib_frequencies(db_path)


@st.cache_data
def cached_run_statistical_comparison(db_path):
    freq_df = cached_get_melanoma_miraclib_frequencies(db_path)
    return run_statistical_comparison(freq_df)


@st.cache_data
def cached_get_baseline_subset_analysis(db_path):
    return get_baseline_subset_analysis(db_path)


@st.cache_data
def get_subject_count(db_path):
    conn = sqlite3.connect(db_path)
    n = conn.execute("SELECT COUNT(DISTINCT subject_id) FROM subjects").fetchone()[0]
    conn.close()
    return n


tabs = st.tabs(["📊 Data Overview", "🔬 Statistical Analysis", "🔍 Subset Analysis", "🗄️ DB Schema"])

with tabs[0]:
    freq_df = cached_get_frequency_table(db_path)

    total_samples = freq_df["sample"].nunique()
    total_subjects = get_subject_count(db_path)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Samples", total_samples)
    col2.metric("Total Subjects", total_subjects)
    col3.markdown("**Cell Populations:**")
    col3.markdown("\n".join(f"- {c}" for c in CELL_COLS))

    st.dataframe(freq_df, use_container_width=True)

    st.download_button(
        label="Download CSV",
        data=freq_df.to_csv(index=False),
        file_name="frequency_table.csv",
        mime="text/csv",
    )

with tabs[1]:
    st.info(
        "This analysis compares melanoma patients treated with miraclib (PBMC samples only). "
        "Responders vs. non-responders are compared using the Mann-Whitney U test. "
        "Results with p < 0.05 are considered statistically significant."
    )

    melanoma_freq_df = cached_get_melanoma_miraclib_frequencies(db_path)
    stats_df = cached_run_statistical_comparison(db_path)

    display_df = stats_df[["population", "responder_median", "non_responder_median", "u_statistic", "p_value", "significant"]].copy()
    display_df["significant"] = display_df["significant"].map({True: "✅", False: "❌"})
    display_df = display_df.rename(columns={"significant": "Significant"})
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    populations = melanoma_freq_df["population"].unique().tolist()
    for i in range(0, len(populations), 2):
        cols = st.columns([1, 1])
        for j, col in enumerate(cols):
            if i + j >= len(populations):
                break
            pop = populations[i + j]
            pop_df = melanoma_freq_df[melanoma_freq_df["population"] == pop]
            fig = px.box(pop_df, x="response", y="percentage", color="response", points="all", title=pop)
            col.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("Melanoma patients receiving miraclib at baseline (day 0), PBMC samples only")

    subset = cached_get_baseline_subset_analysis(db_path)
    baseline_samples = subset["baseline_samples"]
    samples_by_project = subset["samples_by_project"]
    subjects_by_response = subset["subjects_by_response"]
    subjects_by_sex = subset["subjects_by_sex"]

    responders = subjects_by_response.loc[subjects_by_response["response"] == "yes", "subject_count"].sum()
    non_responders = subjects_by_response.loc[subjects_by_response["response"] == "no", "subject_count"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Baseline Samples", len(baseline_samples))
    m2.metric("Responders", int(responders))
    m3.metric("Non-Responders", int(non_responders))

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Samples by Project**")
        st.dataframe(samples_by_project, use_container_width=True, hide_index=True)
        fig = px.bar(samples_by_project, x="project", y="sample_count", title="Samples by Project")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Subjects by Response**")
        st.dataframe(subjects_by_response, use_container_width=True, hide_index=True)
        fig = px.bar(subjects_by_response, x="response", y="subject_count", title="Subjects by Response")
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        st.markdown("**Subjects by Sex**")
        st.dataframe(subjects_by_sex, use_container_width=True, hide_index=True)
        fig = px.bar(subjects_by_sex, x="sex", y="subject_count", title="Subjects by Sex")
        st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    try:
        conn = sqlite3.connect(db_path)

        subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]

        mc1, mc2 = st.columns(2)
        mc1.metric("Subjects", subject_count)
        mc2.metric("Samples", sample_count)

        st.markdown("**subjects**")
        subjects_info = pd.read_sql_query("PRAGMA table_info(subjects)", conn)
        st.dataframe(subjects_info, use_container_width=True, hide_index=True)

        st.markdown("**samples**")
        samples_info = pd.read_sql_query("PRAGMA table_info(samples)", conn)
        st.dataframe(samples_info, use_container_width=True, hide_index=True)

        conn.close()
        st.success("Database loaded successfully.")
    except Exception as e:
        st.error(f"Failed to load database: {e}")
