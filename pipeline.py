import os
import plotly.express as px

from load_data import init_db, load_csv
from analysis import (
    get_frequency_table,
    get_melanoma_miraclib_frequencies,
    run_statistical_comparison,
    get_baseline_subset_analysis,
    CELL_COLS,
)

DB_PATH = "clinical_trial.db"
CSV_PATH = "cell-count.csv"
OUTPUT_DIR = "outputs"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Initializing database")
    init_db(DB_PATH)

    print("Loading CSV data")
    load_csv(DB_PATH, CSV_PATH)

    print("Computing frequency table")
    freq_table = get_frequency_table(DB_PATH)
    freq_table.to_csv(os.path.join(OUTPUT_DIR, "frequency_table.csv"), index=False)

    print("Running statistical comparison")
    melanoma_freq = get_melanoma_miraclib_frequencies(DB_PATH)
    stat_results = run_statistical_comparison(melanoma_freq)
    stat_results.to_csv(os.path.join(OUTPUT_DIR, "statistical_results.csv"), index=False)

    print("Generating boxplots")
    for population in CELL_COLS:
        pop_df = melanoma_freq[melanoma_freq["population"] == population]
        fig = px.box(pop_df, x="response", y="percentage", points="all", title=population)

        for response_val in sorted(pop_df["response"].unique()):
            grp = pop_df[pop_df["response"] == response_val]["percentage"]
            q1 = grp.quantile(0.25)
            q3 = grp.quantile(0.75)
            iqr = q3 - q1
            lower_whisker = grp[grp >= q1 - 1.5 * iqr].min()
            upper_whisker = grp[grp <= q3 + 1.5 * iqr].max()
            stats_text = (
                f"Max: {grp.max():.2f}<br>"
                f"Upper Fence: {upper_whisker:.2f}<br>"
                f"Q3: {q3:.2f}<br>"
                f"Median: {grp.median():.2f}<br>"
                f"Q1: {q1:.2f}<br>"
                f"Lower Fence: {lower_whisker:.2f}<br>"
                f"Min: {grp.min():.2f}"
            )
            fig.add_annotation(
                x=response_val,
                y=-.5,
                xref="x",
                yref="paper",
                text=stats_text,
                showarrow=False,
                align="center",
                font=dict(size=11),
                bordercolor="black",
                borderwidth=1,
                bgcolor="white",
            )

        fig.update_layout(margin=dict(b=200))
        fig.write_image(os.path.join(OUTPUT_DIR, f"boxplot_{population}.png"))

    print("Running subset analysis")
    subset = get_baseline_subset_analysis(DB_PATH)
    subset["samples_by_project"].to_csv(os.path.join(OUTPUT_DIR, "subset_by_project.csv"), index=False)
    subset["subjects_by_response"].to_csv(os.path.join(OUTPUT_DIR, "subset_by_response.csv"), index=False)
    subset["subjects_by_sex"].to_csv(os.path.join(OUTPUT_DIR, "subset_by_sex.csv"), index=False)

    print("Pipeline complete. All outputs saved to outputs dir")


if __name__ == "__main__":
    main()
