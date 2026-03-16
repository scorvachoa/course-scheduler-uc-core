
from course_scheduler.utils.data_utils import flatten_courses


def test_flatten_courses_merges_sections():
    data = [
        {
            "curso": "Matematica",
            "secciones": [
                {"nrc": "100", "seccion": "A1"},
                {"nrc": "101", "seccion": "A2"},
            ],
        }
    ]
    flat = flatten_courses(data)
    assert len(flat) == 2
    assert {item["nrc"] for item in flat} == {"100", "101"}
    assert all("secciones" not in item for item in flat)
