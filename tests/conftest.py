import os
import pathlib
import sys
import tempfile

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from load_data import init_db


@pytest.fixture
def test_db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    conn = init_db(db_path)
    cur = conn.cursor()

    subjects = [
        ("sbj_t1", "prj1", "melanoma", 50, "M", "miraclib", "yes"),
        ("sbj_t2", "prj1", "melanoma", 60, "F", "miraclib", "no"),
        ("sbj_t3", "prj1", "healthy",  45, "M", "none",     None),
    ]
    cur.executemany(
        "INSERT INTO subjects (subject_id, project, condition, age, sex, treatment, response) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        subjects,
    )

    samples = [
        # sbj_t1 — time 0 and 7
        ("smp_t1_0", "sbj_t1", "PBMC", 0, 1200, 3400, 2800, 900, 600),
        ("smp_t1_7", "sbj_t1", "PBMC", 7, 1100, 4200, 3100, 850, 550),
        # sbj_t2 — time 0 and 7
        ("smp_t2_0", "sbj_t2", "PBMC", 0, 1000, 2900, 2500, 700, 800),
        ("smp_t2_7", "sbj_t2", "PBMC", 7,  950, 2700, 2300, 680, 750),
        # sbj_t3 — time 0 and 7
        ("smp_t3_0", "sbj_t3", "PBMC", 0, 1500, 2000, 2200, 1100, 500),
        ("smp_t3_7", "sbj_t3", "PBMC", 7, 1450, 1950, 2150, 1050, 480),
    ]
    cur.executemany(
        "INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start, "
        "b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        samples,
    )

    conn.commit()
    conn.close()

    yield db_path

    os.remove(db_path)
