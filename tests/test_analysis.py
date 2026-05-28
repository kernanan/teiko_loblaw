import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from analysis import (
    get_frequency_table,
    get_melanoma_miraclib_frequencies,
    get_baseline_subset_analysis,
    run_statistical_comparison,
)


@pytest.fixture
def freq_table(test_db):
    return get_frequency_table(test_db)


@pytest.fixture
def melanoma_freq(test_db):
    return get_melanoma_miraclib_frequencies(test_db)


# --- get_frequency_table ---

def test_frequency_table_shape(freq_table, test_db):
    import sqlite3
    conn = sqlite3.connect(test_db)
    sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    conn.close()
    assert len(freq_table) == sample_count * 5


def test_frequency_table_columns(freq_table):
    assert freq_table.columns.tolist() == [
        "sample", "total_count", "population", "count", "percentage"
    ]


def test_percentages_sum_to_100(freq_table):
    sums = freq_table.groupby("sample")["percentage"].sum()
    assert (sums >= 99.99).all(), f"Some samples sum below 100: {sums[sums < 99.99]}"
    assert (sums <= 100.01).all(), f"Some samples sum above 100: {sums[sums > 100.01]}"


# --- run_statistical_comparison ---

def test_stat_comparison_shape(melanoma_freq):
    stats_df = run_statistical_comparison(melanoma_freq)
    assert len(stats_df) == 5


def test_p_values_in_range(melanoma_freq):
    stats_df = run_statistical_comparison(melanoma_freq)
    assert (stats_df["p_value"] >= 0).all()
    assert (stats_df["p_value"] <= 1).all()


# --- get_baseline_subset_analysis ---

def test_baseline_subset_keys(test_db):
    result = get_baseline_subset_analysis(test_db)
    assert result.keys() == {
        "baseline_samples",
        "samples_by_project",
        "subjects_by_response",
        "subjects_by_sex",
    }


def test_baseline_filters_correctly(test_db):
    result = get_baseline_subset_analysis(test_db)
    baseline = result["baseline_samples"]
    assert (baseline["time_from_treatment_start"] == 0).all()
