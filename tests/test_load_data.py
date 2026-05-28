import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from load_data import init_db


def test_tables_exist(test_db):
    conn = sqlite3.connect(test_db)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert "subjects" in tables
    assert "samples" in tables


def test_row_counts(test_db):
    conn = sqlite3.connect(test_db)
    subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    conn.close()
    assert subject_count == 3
    assert sample_count == 6


def test_idempotency(test_db):
    subjects = [
        ("sbj_t1", "prj1", "melanoma", 50, "M", "miraclib", "yes"),
        ("sbj_t2", "prj1", "melanoma", 60, "F", "miraclib", "no"),
        ("sbj_t3", "prj1", "healthy",  45, "M", "none",     None),
    ]
    samples = [
        ("smp_t1_0", "sbj_t1", "PBMC", 0, 1200, 3400, 2800, 900, 600),
        ("smp_t1_7", "sbj_t1", "PBMC", 7, 1100, 4200, 3100, 850, 550),
        ("smp_t2_0", "sbj_t2", "PBMC", 0, 1000, 2900, 2500, 700, 800),
        ("smp_t2_7", "sbj_t2", "PBMC", 7,  950, 2700, 2300, 680, 750),
        ("smp_t3_0", "sbj_t3", "PBMC", 0, 1500, 2000, 2200, 1100, 500),
        ("smp_t3_7", "sbj_t3", "PBMC", 7, 1450, 1950, 2150, 1050, 480),
    ]

    # Re-run init_db on the same path — it should wipe and recreate the schema.
    conn = init_db(test_db)
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO subjects (subject_id, project, condition, age, sex, treatment, response) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        subjects,
    )
    cur.executemany(
        "INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start, "
        "b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        samples,
    )
    conn.commit()
    subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    conn.close()

    assert subject_count == 3
    assert sample_count == 6
