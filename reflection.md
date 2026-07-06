# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design focused on the main objects needed for a pet care scheduling system: `Owner`, `Pet`, `CareTask`, and `PawPalScheduler`.

The `Owner` class was responsible for information about the person using the app, such as their name, available start time, available end time, break preference, and whether they prefer shorter tasks first when priority is tied.

The `Pet` class was responsible for storing information about the pet, including the pet’s name, species, age, and energy level.

The `CareTask` class represented one care activity, such as walking, feeding, medication, play, training, or grooming. Each task included a title, duration, priority, category, preferred time of day, required status, recurrence, and notes.

The `PawPalScheduler` class was responsible for taking the owner, pet, and list of tasks and producing a daily plan.

**b. Design changes**

My design changed during implementation. At first, I thought the scheduler could simply return a list of ordered tasks. However, that was not enough because the app also needed to explain why tasks were chosen, show skipped tasks, display warnings, and provide table-ready data for Streamlit.

To solve this, I added `ScheduleItem`, `SkippedTask`, and `DailyPlan`.

`ScheduleItem` represents a task that was successfully placed into the schedule, including its start time, end time, and explanation. `SkippedTask` represents a task that could not be scheduled and stores the reason why. `DailyPlan` stores the final result, including scheduled items, skipped tasks, warnings, total scheduled minutes, total skipped minutes, and helper methods for displaying results in Streamlit.

This made the design cleaner because the scheduler returns one complete plan object instead of several disconnected pieces of data.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers several constraints:

- the owner’s available start time,
- the owner’s available end time,
- task duration,
- task priority,
- whether a task is required,
- whether a task is recurring today,
- preferred time of day,
- break time between tasks,
- owner preference for shorter tasks first,
- pet energy level for explanations.

I decided that required tasks and high-priority tasks mattered most because pet care tasks like feeding, medication, and walks are more important than optional tasks like extra enrichment or long grooming sessions.

The scheduler sorts tasks so that required tasks come before optional tasks, high-priority tasks come before medium- and low-priority tasks, and preferred time of day is used as another ordering rule. It then schedules tasks only if they fit inside the owner’s available time window.

**b. Tradeoffs**

One tradeoff is that the scheduler uses a greedy algorithm instead of a full optimization algorithm.

This means the scheduler makes decisions in order instead of trying every possible combination of tasks. The benefit is that the algorithm is predictable, fast, and easy for a user to understand. The downside is that it may not always find the mathematically best combination of tasks.

For this scenario, I think the tradeoff is reasonable because PawPal+ is supposed to help a pet owner understand and follow a daily care plan. Clarity matters. A pet owner should be able to see why the app prioritized medication, feeding, or exercise before lower-priority optional tasks.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to help with design brainstorming, code structure, debugging, testing, and documentation.

The most helpful prompts were specific and step-by-step. Instead of only asking for a complete app at once, I worked in checkpoints. I asked for the backend classes first, then tests, then the Streamlit interface, then README documentation, then reflection and AI documentation.

This helped because each part could be tested before moving on. For example, after adding the scheduler, I ran pytest and confirmed that the tests passed before connecting everything to the UI.

**b. Judgment and verification**

One moment where I did not accept the AI suggestion as-is was when checking whether the app actually showed skipped tasks. At first, the available time window was too large, so no skipped tasks appeared. Instead of assuming the feature was broken, I tested it manually by shortening the available time window and loading stronger demo tasks.

I also verified AI-generated code by running tests, running the Streamlit app, checking Git status, and confirming that GitHub commits were pushed. When the coverage command failed because `pytest-cov` was missing, I installed the missing package and reran the command instead of ignoring the error.

---

## 4. Testing and Verification

**a. What you tested**

I tested the most important scheduling behaviors:

- high-priority tasks come before lower-priority tasks,
- required tasks come before optional tasks when priority is tied,
- tasks are skipped when there is not enough time,
- skipped tasks include an explanation,
- non-recurring tasks are skipped from today’s plan,
- scheduled tasks do not overlap,
- owner preference for shorter tasks first works,
- preferred morning tasks come before evening tasks when other rules tie,
- empty task lists return a warning,
- scheduled rows are formatted correctly for Streamlit,
- skipped rows are formatted correctly for Streamlit,
- break time can cause later tasks to be skipped,
- low-energy pet explanations work,
- invalid task duration raises an error,
- invalid owner time windows raise an error,
- time conversion helpers work correctly.

These tests were important because the scheduler is the core of the project. If the scheduler orders tasks incorrectly, overlaps tasks, or fails to skip tasks that do not fit, the app would not be reliable.

**b. Confidence**

I am confident that the scheduler works correctly for the main use cases in this project because I tested the core ordering rules, time-window behavior, skipped-task behavior, validation behavior, and display formatting.

If I had more time, I would test more edge cases, such as multiple pets, exact medication due times, weekly recurring schedules, tasks that must happen at a specific time, and larger task lists where an optimization algorithm might perform better than the current greedy approach.

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is the separation between the backend logic and the Streamlit interface. Keeping the scheduling logic in `pawpal.py` made the app easier to test and made the Streamlit file easier to understand.

I am also satisfied with the explanation system. The app does not only show what tasks were scheduled; it also explains why they were selected or skipped.

**b. What you would improve**

If I had another iteration, I would improve the scheduler by adding exact due times for medication and feeding. I would also add support for multiple pets, weekly schedules, calendar export, and saved owner/pet profiles.

I would also consider adding an optimization mode that compares different possible task combinations to maximize the value of the schedule while still protecting required tasks.

**c. Key takeaway**

One important thing I learned is that system design changes during implementation. My initial design was useful, but it became stronger once I added result classes like `DailyPlan`, `ScheduleItem`, and `SkippedTask`.

I also learned that AI is most useful when I treat it as a collaborator instead of blindly accepting everything. The best process was to ask for small steps, run the code, test the result, check errors, and revise based on what actually happened.