import sqlite3
import os
import pandas as pd


def init_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE subjects (
            subject_id TEXT PRIMARY KEY,
            project    TEXT NOT NULL,
            condition  TEXT NOT NULL,
            age        INTEGER NOT NULL,
            sex        TEXT NOT NULL,
            treatment  TEXT NOT NULL,
            response   TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE samples (
            sample_id               TEXT PRIMARY KEY,
            subject_id              TEXT NOT NULL,
            sample_type             TEXT NOT NULL,
            time_from_treatment_start INTEGER NOT NULL,
            b_cell                  INTEGER NOT NULL,
            cd8_t_cell              INTEGER NOT NULL,
            cd4_t_cell              INTEGER NOT NULL,
            nk_cell                 INTEGER NOT NULL,
            monocyte                INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
    """)

    conn.commit()
    return conn


def load_csv(db_path, csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    subject_cols = ["project", "condition", "age", "sex", "treatment", "response"]
    subjects = df.groupby("subject", sort=False).first().reset_index()

    for _, row in subjects.iterrows():
        response = row["response"] if pd.notna(row["response"]) and row["response"] != "" else None
        cur.execute(
            "INSERT INTO subjects (subject_id, project, condition, age, sex, treatment, response) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row["subject"], row["project"], row["condition"], int(row["age"]),
             row["sex"], row["treatment"], response),
        )

    sample_cols = ["sample", "subject", "sample_type", "time_from_treatment_start",
                   "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start, "
            "b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (row["sample"], row["subject"], row["sample_type"], int(row["time_from_treatment_start"]),
             int(row["b_cell"]), int(row["cd8_t_cell"]), int(row["cd4_t_cell"]),
             int(row["nk_cell"]), int(row["monocyte"])),
        )

    conn.commit()
    conn.close()
    print(f"Loaded {len(subjects)} subjects, {len(df)} samples.")


if __name__ == "__main__":
    init_db("clinical_trial.db")
    print("Database initialized.")
    load_csv("clinical_trial.db", "cell-count.csv")
