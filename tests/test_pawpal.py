import pytest

from pawpal import (
    CareTask,
    Owner,
    PawPalScheduler,
    Pet,
    ScheduleError,
    minutes_to_time,
    time_to_minutes,
)


def build_default_owner():
    return Owner(name="Jordan", available_start="08:00", available_end="09:00")


def build_default_pet():
    return Pet(name="Mochi", species="dog", energy_level="high")


def test_high_priority_required_task_is_scheduled_before_low_priority_task():
    owner = build_default_owner()
    pet = build_default_pet()
    tasks = [
        CareTask("Brush fur", 10, priority="low", category="grooming"),
        CareTask("Give medicine", 5, priority="high", category="health"),
    ]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    assert [item.task.title for item in plan.items] == ["Give medicine", "Brush fur"]


def test_scheduler_skips_task_when_not_enough_time_remains():
    owner = Owner(name="Jordan", available_start="08:00", available_end="08:30")
    pet = build_default_pet()
    tasks = [
        CareTask("Morning walk", 25, priority="high", category="exercise"),
        CareTask("Training game", 20, priority="medium", category="play"),
    ]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    assert [item.task.title for item in plan.items] == ["Morning walk"]
    assert [skipped.task.title for skipped in plan.skipped_tasks] == ["Training game"]
    assert "Not enough time left" in plan.skipped_tasks[0].reason


def test_optional_task_waits_behind_required_task_even_if_same_priority():
    owner = build_default_owner()
    pet = build_default_pet()
    tasks = [
        CareTask("Puzzle toy", 10, priority="high", category="play", required=False),
        CareTask("Feeding", 10, priority="high", category="feeding", required=True),
    ]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    assert [item.task.title for item in plan.items] == ["Feeding", "Puzzle toy"]


def test_non_recurring_task_is_skipped_with_explanation():
    owner = build_default_owner()
    pet = build_default_pet()
    tasks = [CareTask("Monthly nail trim", 15, priority="medium", recurring=False)]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    assert plan.items == []
    assert plan.skipped_tasks[0].task.title == "Monthly nail trim"
    assert "not recurring" in plan.skipped_tasks[0].reason


def test_schedule_items_do_not_overlap():
    owner = Owner(name="Jordan", available_start="08:00", available_end="10:00", break_minutes=5)
    pet = build_default_pet()
    tasks = [
        CareTask("Walk", 30, priority="high", category="exercise"),
        CareTask("Feed", 10, priority="high", category="feeding"),
        CareTask("Brush", 15, priority="medium", category="grooming"),
    ]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    for first, second in zip(plan.items, plan.items[1:]):
        assert time_to_minutes(first.end_time) <= time_to_minutes(second.start_time)


def test_owner_can_prefer_short_tasks_first_after_priority_rules():
    owner = Owner(
        name="Jordan",
        available_start="08:00",
        available_end="09:00",
        prefers_short_tasks_first=True,
    )
    pet = build_default_pet()
    tasks = [
        CareTask("Long grooming", 30, priority="medium", category="grooming"),
        CareTask("Quick water check", 5, priority="medium", category="feeding"),
    ]

    plan = PawPalScheduler().build_plan(owner, pet, tasks)

    assert [item.task.title for item in plan.items] == ["Quick water check", "Long grooming"]


def test_invalid_task_duration_raises_error():
    with pytest.raises(ScheduleError):
        CareTask("Broken task", 0)


def test_invalid_owner_time_window_raises_error():
    with pytest.raises(ScheduleError):
        Owner(name="Jordan", available_start="18:00", available_end="08:00")


def test_time_helpers_round_trip():
    assert time_to_minutes("08:45") == 525
    assert minutes_to_time(525) == "08:45"