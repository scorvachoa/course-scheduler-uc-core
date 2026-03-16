
from course_scheduler.models.course import Course
from course_scheduler.models.schedule import Schedule
from course_scheduler.planner.conflict_detector import detect_conflicts


def make_course(name, nrc, block, day, start, end, modality="presencial"):
    return Course(
        name=name,
        subject="SUB",
        course="101",
        credits=3,
        nrc=nrc,
        teacher="Docente",
        block=block,
        schedules=[Schedule(day=day, start=start, end=end, modality=modality)],
    )


def test_detect_conflicts_same_block():
    a = make_course("Curso A", "100", "W1A", "Lunes", "08:00", "10:00")
    b = make_course("Curso B", "200", "W2A", "Lunes", "09:00", "11:00")
    conflicts = detect_conflicts([a, b])
    assert len(conflicts) == 1


def test_detect_conflicts_different_block_ignored():
    a = make_course("Curso A", "100", "W1A", "Lunes", "08:00", "10:00")
    b = make_course("Curso B", "200", "W2B", "Lunes", "09:00", "11:00")
    conflicts = detect_conflicts([a, b])
    assert len(conflicts) == 0
