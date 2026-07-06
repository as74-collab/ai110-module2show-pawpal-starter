"""Core scheduling logic for the PawPal+ Streamlit project.

The Streamlit UI in app.py should stay focused on user interaction.
This module holds the data model and scheduling algorithm so it can be tested
independently with pytest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

PRIORITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

PREFERRED_TIME_ORDER = {
    "morning": 0,
    "afternoon": 1,
    "evening": 2,
    "any": 3,
}


class ScheduleError(ValueError):
    """Raised when invalid scheduling information is provided."""


@dataclass(frozen=True)
class Owner:
    """Represents the human using PawPal+."""

    name: str
    available_start: str = "08:00"
    available_end: str = "20:00"
    prefers_short_tasks_first: bool = False
    break_minutes: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ScheduleError("Owner name cannot be blank.")
        if self.break_minutes < 0:
            raise ScheduleError("Break minutes cannot be negative.")
        start = time_to_minutes(self.available_start)
        end = time_to_minutes(self.available_end)
        if end <= start:
            raise ScheduleError("Owner availability end time must be after start time.")


@dataclass(frozen=True)
class Pet:
    """Represents the pet receiving care."""

    name: str
    species: str
    age_years: float | None = None
    energy_level: str = "medium"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ScheduleError("Pet name cannot be blank.")
        if not self.species.strip():
            raise ScheduleError("Species cannot be blank.")
        if self.age_years is not None and self.age_years < 0:
            raise ScheduleError("Age cannot be negative.")
        if self.energy_level not in {"low", "medium", "high"}:
            raise ScheduleError("Energy level must be low, medium, or high.")


@dataclass(frozen=True)
class CareTask:
    """A pet care task that may be placed into a daily schedule."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "general"
    preferred_time: str = "any"
    required: bool = True
    recurring: bool = True
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ScheduleError("Task title cannot be blank.")
        if self.duration_minutes <= 0:
            raise ScheduleError("Task duration must be positive.")
        if self.priority not in PRIORITY_WEIGHTS:
            raise ScheduleError("Priority must be low, medium, or high.")
        if self.preferred_time not in PREFERRED_TIME_ORDER:
            raise ScheduleError("Preferred time must be morning, afternoon, evening, or any.")
        if not self.category.strip():
            raise ScheduleError("Category cannot be blank.")

    @property
    def priority_score(self) -> int:
        """Return the numeric priority value used by the scheduler."""

        return PRIORITY_WEIGHTS[self.priority]


@dataclass(frozen=True)
class ScheduleItem:
    """One task placed into the final daily plan."""

    task: CareTask
    start_time: str
    end_time: str
    explanation: str

    @property
    def title(self) -> str:
        return self.task.title


@dataclass(frozen=True)
class SkippedTask:
    """A task that could not be scheduled, with a reason."""

    task: CareTask
    reason: str


@dataclass
class DailyPlan:
    """The result produced by the scheduler."""

    owner: Owner
    pet: Pet
    items: list[ScheduleItem] = field(default_factory=list)
    skipped_tasks: list[SkippedTask] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_scheduled_minutes(self) -> int:
        return sum(item.task.duration_minutes for item in self.items)

    @property
    def total_skipped_minutes(self) -> int:
        return sum(skipped.task.duration_minutes for skipped in self.skipped_tasks)

    def as_rows(self) -> list[dict[str, str | int]]:
        """Return schedule rows that Streamlit can display as a table."""

        return [
            {
                "Start": item.start_time,
                "End": item.end_time,
                "Task": item.task.title,
                "Category": item.task.category,
                "Priority": item.task.priority,
                "Duration": item.task.duration_minutes,
                "Reason": item.explanation,
            }
            for item in self.items
        ]

    def skipped_rows(self) -> list[dict[str, str | int]]:
        """Return skipped task rows that Streamlit can display as a table."""

        return [
            {
                "Task": skipped.task.title,
                "Priority": skipped.task.priority,
                "Duration": skipped.task.duration_minutes,
                "Reason": skipped.reason,
            }
            for skipped in self.skipped_tasks
        ]


class PawPalScheduler:
    """Builds an ordered, non-overlapping care plan for one pet and one owner."""

    def build_plan(self, owner: Owner, pet: Pet, tasks: Iterable[CareTask]) -> DailyPlan:
        """Generate a daily plan that respects availability, priority, and duration.

        Algorithm summary:
        1. Validate owner/pet/tasks through their dataclasses.
        2. Remove non-recurring tasks from today's schedule.
        3. Sort tasks by required status, priority, preferred time, and duration.
        4. Place tasks sequentially from the owner's available start time.
        5. Skip tasks that do not fit, while explaining why.
        """

        task_list = list(tasks)
        plan = DailyPlan(owner=owner, pet=pet)

        start_minutes = time_to_minutes(owner.available_start)
        end_minutes = time_to_minutes(owner.available_end)
        current = start_minutes

        if not task_list:
            plan.warnings.append("No tasks were entered, so PawPal+ created an empty plan.")
            return plan

        recurring_tasks: list[CareTask] = []
        for task in task_list:
            if task.recurring:
                recurring_tasks.append(task)
            else:
                plan.skipped_tasks.append(
                    SkippedTask(
                        task=task,
                        reason="Skipped because it was marked as not recurring for today's plan.",
                    )
                )

        for task in self._sort_tasks(recurring_tasks, owner):
            task_end = current + task.duration_minutes
            if task_end > end_minutes:
                available_left = max(0, end_minutes - current)
                plan.skipped_tasks.append(
                    SkippedTask(
                        task=task,
                        reason=(
                            f"Not enough time left. The task needs {task.duration_minutes} minutes, "
                            f"but only {available_left} minutes remain in the owner's available window."
                        ),
                    )
                )
                continue

            plan.items.append(
                ScheduleItem(
                    task=task,
                    start_time=minutes_to_time(current),
                    end_time=minutes_to_time(task_end),
                    explanation=self._explain_choice(task, pet),
                )
            )
            current = task_end + owner.break_minutes

        if plan.items and current > end_minutes:
            plan.warnings.append(
                "The final break would extend past the available window, but all scheduled tasks still fit."
            )

        if not plan.items:
            plan.warnings.append("No recurring tasks fit inside the selected availability window.")

        return plan

    def _sort_tasks(self, tasks: Iterable[CareTask], owner: Owner) -> list[CareTask]:
        """Sort tasks using scheduling priorities."""

        if owner.prefers_short_tasks_first:
            duration_key = lambda task: task.duration_minutes
        else:
            duration_key = lambda task: -task.duration_minutes

        return sorted(
            tasks,
            key=lambda task: (
                not task.required,
                -task.priority_score,
                PREFERRED_TIME_ORDER[task.preferred_time],
                duration_key(task),
                task.title.lower(),
            ),
        )

    def _explain_choice(self, task: CareTask, pet: Pet) -> str:
        """Create a human-readable explanation for why a task was scheduled."""

        reasons = []

        if task.required:
            reasons.append("required care task")
        else:
            reasons.append("optional enrichment task")

        reasons.append(f"{task.priority} priority")

        if task.preferred_time != "any":
            reasons.append(f"preferred for the {task.preferred_time}")

        if pet.energy_level == "high" and task.category in {"exercise", "walk", "play"}:
            reasons.append("matches a high-energy pet's need for movement")
        elif pet.energy_level == "low" and task.category in {"rest", "grooming", "health"}:
            reasons.append("fits a lower-energy pet's care needs")

        if task.notes.strip():
            reasons.append(task.notes.strip())

        return "; ".join(reasons).capitalize() + "."


def time_to_minutes(time_text: str) -> int:
    """Convert HH:MM text into minutes after midnight."""

    try:
        hours_text, minutes_text = time_text.split(":")
        hours = int(hours_text)
        minutes = int(minutes_text)
    except ValueError as exc:
        raise ScheduleError("Time must use HH:MM format.") from exc

    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        raise ScheduleError("Time must be a valid 24-hour clock time.")

    return hours * 60 + minutes


def minutes_to_time(total_minutes: int) -> str:
    """Convert minutes after midnight into HH:MM text."""

    if total_minutes < 0 or total_minutes >= 24 * 60:
        raise ScheduleError("Minutes must stay within one day.")

    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"