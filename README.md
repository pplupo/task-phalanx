# 🛡️ task-phalanx

> **Taskwarrior & Timewarrior Parallel Assignee Engine**  
> *A tight-knit formation of warriors advancing in parallel unison.*

`task-phalanx` is an idempotent extension for Taskwarrior (compatible with Taskwarrior 2.x and 3.x / TaskChampion sync) that introduces an `assignee` field, accumulative `assigneehistory` audit field, per-project/per-assignee parallel task execution, and isolated per-project/assignee Timewarrior time tracking.

---

## 🤖 Built for Multi-Agent AI Systems

`task-phalanx` makes Taskwarrior and Timewarrior natively **multi-agent capable**.

When running autonomous AI agents or team members concurrently:
- Each AI agent is assigned its own distinct name (e.g., `assignee:Agent-Alpha`, `assignee:Agent-Beta`, `assignee:Coder`).
- Starting a task for `Agent-Alpha` **will not stop** tasks running under `Agent-Beta` or human assignees.
- Each AI agent gets its own isolated Timewarrior database (`~/.timewarrior/projects/<project_slug>/assignees/<agent_slug>/`), enabling independent, concurrent time tracking across all active AI agents.
- Complete handoff history between AI agents and human collaborators is preserved in `assigneehistory`.

---

## ⚔️ Key Features

1. **Multi-Agent & Multi-User Parallel Execution**:
   Starting a task for `Alice` (or `Agent-A`) automatically stops any active tasks assigned to `Alice` in that project, but leaves tasks assigned to `Bob`, `Agent-B`, or other assignees (or in other projects) running in parallel.

2. **Per-Agent Timewarrior Integration**:
   Bypasses Timewarrior's single-interval limitation by isolating time tracking databases per project and assignee under `~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/` via `TIMEWARRIORDB`. Multiple AI agents track time simultaneously without database locks or closed intervals.

3. **Accumulative Assignee History**:
   Appends semicolon-delimited ISO-8601 UTC timestamped records (`YYYY-MM-DDTHH:MM:SSZ: <Assignee>; `) to the `assigneehistory` UDA field whenever a task is assigned or reassigned.

4. **TaskChampion Sync Compatible**:
   All User Defined Attributes (`assignee` and `assigneehistory`) are defined as standard Taskwarrior strings, syncing seamlessly across remote devices or multi-agent nodes without schema drift or sync conflicts.

5. **Idempotent Installation**:
   `setup.sh` configures UDAs and installs hooks safely. Running it multiple times will not duplicate configuration or cause errors.

---

## 🚀 Installation

Run the setup script from repository root:

```bash
./setup.sh
```

---

## 💡 Quick Usage Examples

### 1. Assigning Tasks to Multiple AI Agents
```bash
task add "Refactor auth module" project:Backend assignee:Agent-Alpha
task add "Generate test suite" project:Backend assignee:Agent-Beta
```

### 2. Running AI Agent Tasks Concurrently
```bash
# Agent-Alpha starts working
task 1 start

# Agent-Beta starts working (Agent-Alpha's task remains active!)
task 2 start

# Check active tasks across all agents
task +ACTIVE
```

### 3. Automatic Per-Agent Task Stopping
```bash
task add "Fix linting errors" project:Backend assignee:Agent-Alpha

# Starting a new task for Agent-Alpha stops Task 1 (Agent-Alpha), while Agent-Beta's Task 2 remains active
task 3 start
```

### 4. Viewing Handoff & Assignee History
```bash
task 3 modify assignee:HumanReviewer
task 3 export
```

### 5. Inspecting Agent Time Logs
```bash
TIMEWARRIORDB=~/.timewarrior/projects/backend/assignees/agent_alpha timew
TIMEWARRIORDB=~/.timewarrior/projects/backend/assignees/agent_beta timew
```

---

## 🧪 Running Unit & Integration Tests

Run the test suite:

```bash
python3 -m unittest discover tests
```
