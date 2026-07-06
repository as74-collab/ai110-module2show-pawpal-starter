# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the AI assistant to help me build the PawPal+ project in a detailed, checkpoint-based workflow while frequently updating GitHub. The goal was to turn the starter Streamlit app into a complete pet care planning assistant with backend scheduling logic, tests, documentation, UML design, reflection, and extra-credit documentation.

The main task was not just to write one file. I asked the AI to help me plan and implement the whole project step by step so that each GitHub commit showed clear progress.

**What did the agent do?**

The AI helped with the following steps:

1. Reviewed the starter project structure and identified that the original `app.py` was only a thin Streamlit starter app.
2. Planned a GitHub checkpoint workflow so the project could be committed frequently.
3. Created the backend file `pawpal.py`.
4. Designed the main classes:
   - `Owner`
   - `Pet`
   - `CareTask`
   - `ScheduleItem`
   - `SkippedTask`
   - `DailyPlan`
   - `PawPalScheduler`
5. Implemented scheduling behavior:
   - required tasks before optional tasks,
   - high priority before medium and low priority,
   - preferred time ordering,
   - owner preference for shorter tasks first,
   - break time between tasks,
   - skipped tasks when time runs out,
   - explanations for scheduled and skipped tasks.
6. Created pytest tests for the scheduler.
7. Helped connect the scheduler to the Streamlit UI.
8. Improved the app with task editing, task deletion, demo tasks, skipped-task display, and CSV export.
9. Helped update `requirements.txt` to include `pytest-cov`.
10. Helped troubleshoot PowerShell virtual environment activation.
11. Helped troubleshoot the coverage command when `pytest-cov` was not installed.
12. Helped write a full README with setup, UML, scheduling logic, sample output, tests, smarter scheduling, demo walkthrough, tradeoffs, and future improvements.
13. Helped complete the reflection and AI interaction documentation.

**What did you have to verify or fix manually?**

I had to manually verify several things:

1. I ran `python -m pytest -q` to confirm that the tests passed.
2. I ran `python -m pytest --cov=pawpal -q` to confirm that coverage worked.
3. I opened the Streamlit app and manually checked that the UI worked.
4. I checked whether skipped tasks appeared by shortening the available time window.
5. I verified that task editing and deletion worked in the app.
6. I checked Git status before committing.
7. I pushed each checkpoint to GitHub.
8. I confirmed that the Mermaid UML diagram should render correctly on GitHub.
9. I had to create a virtual environment because `.venv` did not exist at first.
10. I had to bypass PowerShell’s script execution restriction for the current terminal session.
11. I had to install `pytest-cov` after the coverage command failed.

One issue I noticed was that skipped tasks did not appear at first because the schedule had enough time to include all tasks. The fix was to test the app with a shorter time window, such as 8:00 AM to 8:45 AM, and use the strong demo tasks.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | ChatGPT | ChatGPT |
| **Prompt** | “Write the whole PawPal+ app.” | “Help me solve the whole PawPal+ project in great detail, with frequent GitHub commits. Give me one big checkpoint at a time and tell me what to do on my end.” |
| **Response summary** | This type of prompt would likely produce a large amount of code all at once, but it would be harder to verify and harder to commit cleanly. | This approach produced a staged workflow: starter checkpoint, backend model, tests, Streamlit UI, stronger features, README, reflection, and AI documentation. |
| **What was useful** | It could be fast for getting a rough first draft. | It was easier to follow, easier to test, easier to debug, and better for GitHub history because each commit had a clear purpose. |
| **Problems noticed** | A single large response can hide mistakes. It is harder to know which part caused an error if the code fails. | It took more steps, but the result was more reliable because each checkpoint was tested before moving on. |
| **Decision** | I did not use this as the main strategy. | I used this strategy for the final implementation. |

**Which approach did you use in your final implementation and why?**

I used Option B because the checkpoint-based workflow was more reliable. It let me build the project in small stages and verify each part before moving on.

This was especially useful because the project had several different requirements: backend classes, scheduling logic, Streamlit UI, tests, README documentation, UML design, reflection, and AI interaction documentation. Doing everything in one step would have made the project harder to debug.

The staged approach also made the GitHub history stronger because each commit showed a meaningful improvement.