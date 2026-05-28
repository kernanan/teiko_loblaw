import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from analysis import get_frequency_table, get_melanoma_miraclib_frequencies, run_statistical_comparison, get_baseline_subset_analysis, run_average_number_B_cells_for_time0_melanoma_male_responders


DB_PATH = pathlib.Path(__file__).parent.parent / "clinical_trial.db"


def test_get_frequency_table():
    df = get_frequency_table(str(DB_PATH))

    assert df.shape == (52500, 5), f"Unexpected shape: {df.shape}"
    assert df.columns.tolist() == ["sample", "total_count", "population", "count", "percentage"]

    sums = df.groupby("sample")["percentage"].sum()
    assert sums.min() >= 99.99, f"Min percentage sum too low: {sums.min()}"
    assert sums.max() <= 100.01, f"Max percentage sum too high: {sums.max()}"
    return df

def test_get_melanoma_miraclib_frequencies():
    freq_df = get_melanoma_miraclib_frequencies(str(DB_PATH))
    assert set(freq_df["condition"].unique()) == {'melanoma'}, f"Unexpected condition values"
    assert set(freq_df["treatment"].unique()) == {'miraclib'}, f"Unexpected treatment values"
    response_values = freq_df["response"].unique()
    assert set(response_values) == {'yes', 'no'}, f"Unexpected response values: {response_values}"
    stats_df = run_statistical_comparison(freq_df)
    assert stats_df.shape == (5, 6), f"Unexpected stats_df shape: {stats_df.shape}"
    return stats_df

def test_run_statistical_comparison():
    result = get_baseline_subset_analysis(str(DB_PATH))
    # print(result.keys())
    assert result.keys() == {"baseline_samples", "samples_by_project", "subjects_by_response", "subjects_by_sex"}, f"Expected 4 keys in result, got {result.keys()}"
    resp_total = result["subjects_by_response"]["subject_count"].sum()
    sex_total = result["subjects_by_sex"]["subject_count"].sum()
    # print(resp_total, sex_total) # Must be equal, same underlying group
    assert resp_total == sex_total, f"Expected equal subject counts, got resp={resp_total} sex={sex_total}"
    return result

if __name__ == "__main__":
    # part 2 test
    f = test_get_frequency_table()
    print("PART 2 FREQ TABLE PASS:\n", f)

    # part 3 test
    mf = test_get_melanoma_miraclib_frequencies()
    print("PART 3 MELANOMA MIRACLIB FREQUENCIES PASS:\n", mf)
    
    # part 4 test
    s = test_run_statistical_comparison()
    print("PART 4 STATISTICAL COMPARISON PASS:\n", s)

    # AVG_number_B_cells_for_time0_melanoma_male_responders("clinical_trial question
    b = run_average_number_B_cells_for_time0_melanoma_male_responders(str(DB_PATH))
    print("PART X AVERAGE NUMBER B CELLS FOR TIME0 MELANOMA MALE RESPONDERS:\n", b)


