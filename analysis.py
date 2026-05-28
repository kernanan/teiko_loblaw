import sqlite3
import pandas as pd
from scipy import stats


CELL_COLS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def get_frequency_table(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT
            sa.sample_id  AS sample,
            su.project,
            su.condition,
            su.treatment,
            su.response,
            sa.sample_type,
            sa.time_from_treatment_start,
            sa.b_cell,
            sa.cd8_t_cell,
            sa.cd4_t_cell,
            sa.nk_cell,
            sa.monocyte
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
    """, conn)
    conn.close()

    df["total_count"] = df[CELL_COLS].sum(axis=1)

    df = df.melt(
        id_vars=[c for c in df.columns if c not in CELL_COLS],
        value_vars=CELL_COLS,
        var_name="population",
        value_name="count",
    )

    df["percentage"] = (df["count"] / df["total_count"] * 100)

    return df[["sample", "total_count", "population", "count", "percentage"]]

# for Bob's colleague, basically does get_frequency_table() with extra wheres, just need this for part 3
def get_melanoma_miraclib_frequencies(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT
            sa.sample_id AS sample,
            su.condition,
            su.treatment,
            su.response,
            sa.sample_type,
            sa.b_cell,
            sa.cd8_t_cell,
            sa.cd4_t_cell,
            sa.nk_cell,
            sa.monocyte
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.treatment = 'miraclib'
          AND sa.sample_type = 'PBMC'
          AND su.response IN ('yes', 'no')
    """, conn)
    conn.close()

    df["total_count"] = df[CELL_COLS].sum(axis=1)

    df = df.melt(
        id_vars=[c for c in df.columns if c not in CELL_COLS],
        value_vars=CELL_COLS,
        var_name="population",
        value_name="count",
    )

    df["percentage"] = (df["count"] / df["total_count"] * 100)

    return df[["sample", "condition", "treatment", "response", "sample_type", "total_count", "population", "count", "percentage"]].reset_index(drop=True)


def get_baseline_subset_analysis(db_path):
    conn = sqlite3.connect(db_path)

    baseline_samples = pd.read_sql_query("""
        SELECT
            sa.sample_id,
            sa.subject_id,
            su.project,
            su.condition,
            su.treatment,
            su.response,
            su.sex,
            sa.sample_type,
            sa.time_from_treatment_start
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
          AND su.treatment = 'miraclib'
    """, conn)

    samples_by_project = pd.read_sql_query("""
        SELECT su.project, COUNT(*) AS sample_count
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
          AND su.treatment = 'miraclib'
        GROUP BY su.project
    """, conn)

    subjects_by_response = pd.read_sql_query("""
        SELECT su.response, COUNT(DISTINCT sa.subject_id) AS subject_count
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
          AND su.treatment = 'miraclib'
        GROUP BY su.response
    """, conn)

    subjects_by_sex = pd.read_sql_query("""
        SELECT su.sex, COUNT(DISTINCT sa.subject_id) AS subject_count
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
          AND su.treatment = 'miraclib'
        GROUP BY su.sex
    """, conn)

    conn.close()

    return {
        "baseline_samples": baseline_samples,
        "samples_by_project": samples_by_project,
        "subjects_by_response": subjects_by_response,
        "subjects_by_sex": subjects_by_sex,
    }


def run_statistical_comparison(freq_df):
    rows = []
    for population, group in freq_df.groupby("population"):
        responders = group[group["response"] == "yes"]["percentage"]
        non_responders = group[group["response"] == "no"]["percentage"]

        u_stat, p_value = stats.mannwhitneyu(responders, non_responders, alternative="two-sided")

        rows.append({
            "population": population,
            "u_statistic": u_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "responder_median": responders.median(),
            "non_responder_median": non_responders.median(),
        })

    return pd.DataFrame(rows)


def run_average_number_B_cells_for_time0_melanoma_male_responders(db_path):
    conn = sqlite3.connect(db_path)
    result = conn.execute("""
        SELECT ROUND(AVG(sa.b_cell), 2)
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.sex = 'M'
          AND su.response = 'yes'
          AND sa.time_from_treatment_start = 0
    """).fetchone()[0]
    conn.close()
    return result
