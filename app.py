import csv
from datetime import time
from io import StringIO

import streamlit as st

from pawpal import CareTask, Owner, PawPalScheduler, Pet, ScheduleError


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


# ---------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------

def initialize_state() -> None:
    """Create default task storage for the Streamlit session."""

    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {
                "title": "Morning walk",
                "duration_minutes": 30,
                "priority": "high",
                "category": "exercise",
                "preferred_time": "morning",
                "required": True,
                "recurring": True,
                "notes": "Important for exercise and bathroom needs.",
            },
            {
                "title": "Breakfast feeding",
                "duration_minutes": 10,
                "priority": "high",
                "category": "feeding",
                "preferred_time": "morning",
                "required": True,
                "recurring": True,
                "notes": "Keeps the pet on a consistent meal routine.",
            },
            {
                "title": "Puzzle toy enrichment",
                "duration_minutes": 20,
                "priority": "medium",
                "category": "play",
                "preferred_time": "afternoon",
                "required": False,
                "recurring": True,
                "notes": "Good mental stimulation if there is enough time.",
            },
            {
                "title": "Brush fur",
                "duration_minutes": 15,
                "priority": "low",
                "category": "grooming",
                "preferred_time": "evening",
                "required": False,
                "recurring": True,
                "notes": "Helpful, but less urgent than food, medicine, or exercise.",
            },
        ]

    if "last_plan_rows" not in st.session_state:
        st.session_state.last_plan_rows = []

    if "last_skipped_rows" not in st.session_state:
        st.session_state.last_skipped_rows = []


def reset_demo_tasks() -> None:
    """Reset the app to a strong demo task list."""

    st.session_state.tasks = [
        {
            "title": "Morning walk",
            "duration_minutes": 30,
            "priority": "high",
            "category": "exercise",
            "preferred_time": "morning",
            "required": True,
            "recurring": True,
            "notes": "Important for exercise, bathroom needs, and high-energy pets.",
        },
        {
            "title": "Give medication",
            "duration_minutes": 5,
            "priority": "high",
            "category": "health",
            "preferred_time": "morning",
            "required": True,
            "recurring": True,
            "notes": "Required health task that should not be skipped.",
        },
        {
            "title": "Dinner feeding",
            "duration_minutes": 10,
            "priority": "high",
            "category": "feeding",
            "preferred_time": "evening",
            "required": True,
            "recurring": True,
            "notes": "Keeps meal timing consistent.",
        },
        {
            "title": "Training practice",
            "duration_minutes": 25,
            "priority": "medium",
            "category": "training",
            "preferred_time": "afternoon",
            "required": False,
            "recurring": True,
            "notes": "Useful if time remains after required care.",
        },
        {
            "title": "Long grooming session",
            "duration_minutes": 45,
            "priority": "low",
            "category": "grooming",
            "preferred_time": "evening",
            "required": False,
            "recurring": True,
            "notes": "Can be skipped when the day is too busy.",
        },
    ]
    st.session_state.last_plan_rows = []
    st.session_state.last_skipped_rows = []


def task_from_dict(task_data: dict) -> CareTask:
    """Convert a Streamlit task dictionary into a CareTask object."""

    return CareTask(
        title=task_data["title"],
        duration_minutes=int(task_data["duration_minutes"]),
        priority=task_data["priority"],
        category=task_data["category"],
        preferred_time=task_data["preferred_time"],
        required=bool(task_data["required"]),
        recurring=bool(task_data["recurring"]),
        notes=task_data["notes"],
    )


def rows_to_csv(rows: list[dict]) -> str:
    """Convert schedule rows into downloadable CSV text."""

    if not rows:
        return ""

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def display_task_editor() -> None:
    """Show current tasks and allow editing/deleting."""

    if not st.session_state.tasks:
        st.info("No tasks yet. Add at least one task before generating a plan.")
        return

    for index, task in enumerate(st.session_state.tasks):
        required_text = "Required" if task["required"] else "Optional"
        recurring_text = "Recurring today" if task["recurring"] else "Not recurring today"
        label = (
            f"{index + 1}. {task['title']} — {task['duration_minutes']} min, "
            f"{task['priority']} priority, {required_text}, {recurring_text}"
        )

        with st.expander(label, expanded=False):
            st.caption("Edit this task, save changes, or delete it.")

            with st.form(f"edit_task_form_{index}"):
                edited_title = st.text_input(
                    "Task title",
                    value=task["title"],
                    key=f"edit_title_{index}",
                )

                edit_col1, edit_col2, edit_col3 = st.columns(3)

                with edit_col1:
                    edited_duration = st.number_input(
                        "Duration in minutes",
                        min_value=1,
                        max_value=240,
                        value=int(task["duration_minutes"]),
                        key=f"edit_duration_{index}",
                    )
                    edited_priority = st.selectbox(
                        "Priority",
                        ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(task["priority"]),
                        key=f"edit_priority_{index}",
                    )

                with edit_col2:
                    category_options = [
                        "feeding",
                        "health",
                        "exercise",
                        "walk",
                        "play",
                        "training",
                        "grooming",
                        "rest",
                        "general",
                    ]
                    edited_category = st.selectbox(
                        "Category",
                        category_options,
                        index=category_options.index(task["category"])
                        if task["category"] in category_options
                        else category_options.index("general"),
                        key=f"edit_category_{index}",
                    )
                    preferred_options = ["morning", "afternoon", "evening", "any"]
                    edited_preferred_time = st.selectbox(
                        "Preferred time",
                        preferred_options,
                        index=preferred_options.index(task["preferred_time"]),
                        key=f"edit_preferred_{index}",
                    )

                with edit_col3:
                    edited_required = st.checkbox(
                        "Required task",
                        value=bool(task["required"]),
                        key=f"edit_required_{index}",
                    )
                    edited_recurring = st.checkbox(
                        "Recurring today",
                        value=bool(task["recurring"]),
                        key=f"edit_recurring_{index}",
                    )

                edited_notes = st.text_area(
                    "Notes / reason",
                    value=task["notes"],
                    key=f"edit_notes_{index}",
                )

                save_clicked = st.form_submit_button("Save task changes")

                if save_clicked:
                    if not edited_title.strip():
                        st.error("Task title cannot be blank.")
                    else:
                        st.session_state.tasks[index] = {
                            "title": edited_title.strip(),
                            "duration_minutes": int(edited_duration),
                            "priority": edited_priority,
                            "category": edited_category,
                            "preferred_time": edited_preferred_time,
                            "required": edited_required,
                            "recurring": edited_recurring,
                            "notes": edited_notes.strip(),
                        }
                        st.session_state.last_plan_rows = []
                        st.session_state.last_skipped_rows = []
                        st.success(f"Updated task: {edited_title.strip()}")

            if st.button("Delete this task", key=f"delete_task_{index}"):
                st.session_state.tasks.pop(index)
                st.session_state.last_plan_rows = []
                st.session_state.last_skipped_rows = []
                st.rerun()


def build_owner(owner_name: str, start_time, end_time, short_first: bool, break_minutes: int) -> Owner:
    """Create an Owner object from UI values."""

    return Owner(
        name=owner_name,
        available_start=start_time.strftime("%H:%M"),
        available_end=end_time.strftime("%H:%M"),
        prefers_short_tasks_first=short_first,
        break_minutes=break_minutes,
    )


def build_pet(pet_name: str, species: str, age_years: float, energy_level: str) -> Pet:
    """Create a Pet object from UI values."""

    return Pet(
        name=pet_name,
        species=species,
        age_years=age_years,
        energy_level=energy_level,
    )


# ---------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------

initialize_state()

st.title("🐾 PawPal+")
st.caption(
    "A pet care planning assistant that builds a daily schedule from time, priority, "
    "recurrence, required status, and owner preferences."
)

with st.expander("Project scenario", expanded=False):
    st.markdown(
        """
        PawPal+ helps a busy pet owner organize daily care tasks such as feeding,
        walks, medicine, enrichment, grooming, rest, and training.

        This version uses a real backend scheduler instead of placeholder UI logic.
        It ranks tasks by required status, priority, preferred time, and owner preferences.
        Then it builds a non-overlapping schedule inside the owner's available time window
        and explains every scheduled or skipped task.
        """
    )

left_col, right_col = st.columns([1, 1])

# ---------------------------------------------------------------------
# Owner and pet inputs
# ---------------------------------------------------------------------

with left_col:
    st.header("1. Owner + pet info")

    owner_name = st.text_input("Owner name", value="Jordan")
    pet_name = st.text_input("Pet name", value="Mochi")

    species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    age_years = st.number_input("Pet age in years", min_value=0.0, max_value=40.0, value=3.0, step=0.5)
    energy_level = st.selectbox("Pet energy level", ["low", "medium", "high"], index=2)

    st.subheader("Daily constraints")
    available_start = st.time_input("Owner available start", value=time(8, 0))
    available_end = st.time_input("Owner available end", value=time(12, 0))
    break_minutes = st.number_input("Break between tasks, in minutes", min_value=0, max_value=60, value=5)
    prefers_short_tasks_first = st.checkbox(
        "Prefer shorter tasks first when priority is tied",
        value=False,
    )

    st.info(
        "To demonstrate skipped tasks, load the strong demo tasks and set the available window "
        "to 8:00 AM–8:45 AM."
    )

# ---------------------------------------------------------------------
# Task input form
# ---------------------------------------------------------------------

with right_col:
    st.header("2. Add care tasks")

    with st.form("task_form", clear_on_submit=True):
        task_title = st.text_input("Task title", placeholder="Example: Evening walk")
        duration = st.number_input("Duration in minutes", min_value=1, max_value=240, value=20)

        form_col1, form_col2 = st.columns(2)
        with form_col1:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            category = st.selectbox(
                "Category",
                ["feeding", "health", "exercise", "walk", "play", "training", "grooming", "rest", "general"],
            )
        with form_col2:
            preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "any"])
            required = st.checkbox("Required task", value=True)
            recurring = st.checkbox("Recurring today", value=True)

        notes = st.text_area("Notes / reason", placeholder="Example: Vet said medicine must happen daily.")

        submitted = st.form_submit_button("Add task")

        if submitted:
            if not task_title.strip():
                st.error("Task title cannot be blank.")
            else:
                st.session_state.tasks.append(
                    {
                        "title": task_title.strip(),
                        "duration_minutes": int(duration),
                        "priority": priority,
                        "category": category,
                        "preferred_time": preferred_time,
                        "required": required,
                        "recurring": recurring,
                        "notes": notes.strip(),
                    }
                )
                st.session_state.last_plan_rows = []
                st.session_state.last_skipped_rows = []
                st.success(f"Added task: {task_title.strip()}")

    task_button_col1, task_button_col2 = st.columns(2)
    with task_button_col1:
        if st.button("Load strong demo tasks"):
            reset_demo_tasks()
            st.rerun()

    with task_button_col2:
        if st.button("Clear all tasks"):
            st.session_state.tasks = []
            st.session_state.last_plan_rows = []
            st.session_state.last_skipped_rows = []
            st.rerun()


st.divider()

# ---------------------------------------------------------------------
# Task editor and schedule generation
# ---------------------------------------------------------------------

st.header("3. Current task list")
display_task_editor()

st.divider()

st.header("4. Generate daily plan")

generate_col, summary_col = st.columns([1, 2])

with generate_col:
    generate_clicked = st.button("Generate schedule", type="primary", use_container_width=True)

with summary_col:
    st.write(
        "The scheduler places tasks in order, avoids overlap, skips tasks that do not fit, "
        "and explains why each task was selected or skipped."
    )

if generate_clicked:
    try:
        owner = build_owner(
            owner_name=owner_name,
            start_time=available_start,
            end_time=available_end,
            short_first=prefers_short_tasks_first,
            break_minutes=int(break_minutes),
        )
        pet = build_pet(
            pet_name=pet_name,
            species=species,
            age_years=float(age_years),
            energy_level=energy_level,
        )
        tasks = [task_from_dict(task_data) for task_data in st.session_state.tasks]

        scheduler = PawPalScheduler()
        plan = scheduler.build_plan(owner=owner, pet=pet, tasks=tasks)

        st.session_state.last_plan_rows = plan.as_rows()
        st.session_state.last_skipped_rows = plan.skipped_rows()

        st.success(
            f"Generated a plan for {pet.name}. "
            f"Scheduled {len(plan.items)} task(s), skipped {len(plan.skipped_tasks)} task(s)."
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Scheduled tasks", len(plan.items))
        with metric_col2:
            st.metric("Scheduled minutes", plan.total_scheduled_minutes)
        with metric_col3:
            st.metric("Skipped minutes", plan.total_skipped_minutes)

        if plan.warnings:
            for warning in plan.warnings:
                st.warning(warning)

    except ScheduleError as error:
        st.error(f"Could not build the schedule: {error}")

    except Exception as error:
        st.error(f"Unexpected error: {error}")


# ---------------------------------------------------------------------
# Display latest generated results
# ---------------------------------------------------------------------

if st.session_state.last_plan_rows:
    st.subheader("Scheduled plan")
    st.dataframe(st.session_state.last_plan_rows, use_container_width=True, hide_index=True)

    schedule_csv = rows_to_csv(st.session_state.last_plan_rows)
    st.download_button(
        "Download scheduled plan as CSV",
        data=schedule_csv,
        file_name="pawpal_daily_schedule.csv",
        mime="text/csv",
    )

    with st.expander("Plain-English explanation", expanded=True):
        for row in st.session_state.last_plan_rows:
            st.markdown(
                f"- **{row['Start']}–{row['End']} — {row['Task']}** "
                f"({row['Duration']} min, {row['Priority']} priority): {row['Reason']}"
            )

else:
    st.info("No generated plan yet. Click **Generate schedule** after adding tasks.")

if st.session_state.last_skipped_rows:
    st.subheader("Skipped tasks")
    st.dataframe(st.session_state.last_skipped_rows, use_container_width=True, hide_index=True)

    skipped_csv = rows_to_csv(st.session_state.last_skipped_rows)
    st.download_button(
        "Download skipped tasks as CSV",
        data=skipped_csv,
        file_name="pawpal_skipped_tasks.csv",
        mime="text/csv",
    )

    with st.expander("Why tasks were skipped", expanded=True):
        for row in st.session_state.last_skipped_rows:
            st.markdown(
                f"- **{row['Task']}** ({row['Duration']} min, {row['Priority']} priority): {row['Reason']}"
            )


st.divider()

# ---------------------------------------------------------------------
# Design explanation inside the app
# ---------------------------------------------------------------------

with st.expander("How the scheduler works"):
    st.markdown(
        """
        PawPal+ uses a greedy scheduling algorithm:

        1. Validate owner, pet, and task inputs.
        2. Skip tasks that are not recurring today.
        3. Sort recurring tasks using these rules:
           - required tasks before optional tasks
           - high priority before medium and low priority
           - preferred time order: morning, afternoon, evening, then any
           - owner preference for shorter tasks first when priority is tied
        4. Add tasks one by one into the available time window.
        5. Skip any task that does not fit and explain why.

        This design is reasonable for a daily pet care assistant because required and
        high-priority tasks, such as feeding and medicine, should come before optional
        enrichment tasks. The tradeoff is that the scheduler is predictable and easy to
        explain, but it may not always find the mathematically perfect combination of
        tasks for every possible schedule.
        """
    )