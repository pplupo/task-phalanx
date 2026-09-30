# Feature Specification: Taskwarrior Parallel Assignees and Timewarrior Integration

**Feature Branch**: `001-parallel-assignees`  
**Created**: 2026-09-23  
**Status**: Draft  
**Input**: User description: "I want to create an idempotent script that create an 'assignee' field in taskwarrior and change its behavior so that if an assignee is passed: 1- start will start a task and set the assignee. 2- starting a task wll stop tasks of that assignee only: the other tasks are left alone. They will keep running if they were running. It would allow for multiple tasks to be in progress at the same time. You must use uda for the new field: task config uda.assignee.type string, task config uda.assignee.label Assignee. The script must detect if timewarrior is present, and if it is, change its hooks: 1- start will start a task and set the assignee. 2- starting a task wll stop tasks of that assignee only: the other tasks are left alone. They will keep running if they were running. It would allow for multiple tasks to be in progress at the same time. Whenever an assignee is assigned, I want you to store it's name with a timestamp in anoher uda field. This field is accumulative, you don't remove the assignees from it, you only add new ones as they change. Task auto-stopping and Timewarrior databases are scoped per project and per assignee."

## Clarifications

### Session 2026-09-23
- Q: How should the accumulative assignee history entries be formatted and delimited in the assigneehistory UDA field? → A: ISO-8601 timestamp with semicolon delimiter (e.g., `2026-09-23T10:00:00Z: Alice; 2026-09-23T12:00:00Z: Bob`).
- Q: How should Timewarrior support tracking multiple parallel task intervals simultaneously across assignees? → A: Use separate Timewarrior database directories per project and assignee via `TIMEWARRIORDB` (e.g., `~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/`), enabling independent concurrent active time intervals per project and assignee.
- Q: How should TaskChampion sync compatibility be ensured? → A: Assignee UDAs (`assignee` and `assigneehistory`) must use standard Taskwarrior UDA string configurations registered in Taskwarrior config, ensuring seamless JSON synchronization via TaskChampion sync hooks/commands without schema drift.
- Q: How should stock `on-modify.timewarrior` hook conflict be handled? → A: `setup.sh` detects and disables the stock `on-modify.timewarrior` hook by removing executable permissions and renaming to `on-modify.timewarrior.disabled`, preventing global single-interval timeline conflicts.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Idempotent Environment Configuration & Hook Protection (Priority: P1)

As a system administrator or task manager, I want to run a setup script that safely and idempotently configures Taskwarrior UDAs, disables conflicting stock Timewarrior hooks, and establishes per-project/per-assignee Timewarrior directories so that parallel assignee support is enabled without corrupting existing configuration or timeline state.

**Why this priority**: Core prerequisite for enabling all downstream assignee tracking, TaskChampion sync compatibility, and hook behaviors safely across single or repeated script executions.

**Independent Test**: Can be tested by executing the setup script multiple times in succession against a Taskwarrior environment with stock hooks present, verifying that UDAs and hooks are correctly set up and stock hooks disabled.

**Acceptance Scenarios**:

1. **Given** Taskwarrior is installed, **When** the configuration script is executed for the first time, **Then** `uda.assignee.type` is set to `string`, `uda.assignee.label` is set to `Assignee`, `uda.assigneehistory.type` is set to `string`, `uda.assigneehistory.label` is set to `Assignee History`, and required Taskwarrior hooks are installed.
2. **Given** stock `on-modify.timewarrior` is present in the hooks directory, **When** `setup.sh` executes, **Then** it disables the stock hook (`chmod -x`) to prevent global timeline interference.
3. **Given** Timewarrior is installed on the system, **When** the configuration script runs, **Then** it detects Timewarrior presence, ensures project/assignee directory structure (`~/.timewarrior/projects/`) exists, and configures the necessary Timewarrior hooks for per-project/per-assignee time tracking.

---

### User Story 2 - Parallel Task Execution Scoped by Project and Assignee (Priority: P2)

As a team member or multi-context worker, I want starting a task with a specified assignee to only stop active tasks belonging to that same assignee within the same project, so that an assignee can have active tasks running concurrently across different projects or assignees.

**Why this priority**: Enables the core functional objective of allowing concurrent in-progress tasks assigned to different individuals or across different projects.

**Independent Test**: Can be tested by starting Task A for `Alice` in `ProjA`, Task B for `Alice` in `ProjB`, and Task C for `Bob` in `ProjA`, confirming all three tasks remain in active `start` state simultaneously.

**Acceptance Scenarios**:

1. **Given** Task A is currently active under `Alice` in `ProjA`, **When** Task B is started with `Alice` in `ProjB`, **Then** Task A continues running while Task B starts, resulting in both Task A and Task B being in progress.
2. **Given** Task A is active under `Alice` in `ProjA`, **When** Task C is started with `Alice` in `ProjA`, **Then** Task A is stopped and Task C is started.
3. **Given** Taskwarrior is configured with TaskChampion sync, **When** tasks are started or assigned, **Then** task state and UDA values sync cleanly without syntax errors or attribute conflicts.

---

### User Story 3 - Per-Project Per-Assignee Timewarrior Independent Interval Tracking (Priority: P3)

As a user tracking time across multiple assignees and projects, I want Timewarrior to maintain independent active tracking intervals for each `(project, assignee)` pair using distinct `TIMEWARRIORDB` databases.

**Why this priority**: Overcomes Timewarrior's single-active-interval limitation by isolating database contexts per project and assignee.

**Independent Test**: Can be tested by starting a task for Alice in ProjA and a task for Alice in ProjB, then verifying that `TIMEWARRIORDB=.../projects/proja/assignees/alice timew` and `TIMEWARRIORDB=.../projects/projb/assignees/alice timew` each show an active running interval.

**Acceptance Scenarios**:

1. **Given** Timewarrior is installed, **When** Task 1 is started for `Alice` in `ProjA`, **Then** an active interval is recorded in `TIMEWARRIORDB=~/.timewarrior/projects/proja/assignees/alice`.
2. **Given** Task 1 is active for `Alice` in `ProjA`, **When** Task 2 is started for `Alice` in `ProjB`, **Then** Task 1's interval in `proja/assignees/alice` remains active, and a new active interval is started in `TIMEWARRIORDB=~/.timewarrior/projects/projb/assignees/alice`.

---

### User Story 4 - Accumulative Assignee History Tracking (Priority: P4)

As an auditor or project manager, I want every assignment or re-assignment of a task to append the assignee name and assignment timestamp to an accumulative history UDA, so that complete ownership history is preserved over time.

**Why this priority**: Provides auditability and tracking of task handoffs over the lifecycle of a task.

**Independent Test**: Can be tested by setting an assignee on a task, then changing the assignee, and checking that the history field contains timestamped entries for both assignments.

**Acceptance Scenarios**:

1. **Given** a new or existing task, **When** an assignee is set (e.g., `assignee:Alice`), **Then** a record formatted as `<ISO-8601-timestamp>: Alice` is appended to the task's assignee history UDA (delimited by `; `).
2. **Given** a task currently assigned to `Alice`, **When** the task is reassigned (e.g., `assignee:Bob`), **Then** the existing history entry for `Alice` is preserved and a new record `<ISO-8601-timestamp>: Bob` is appended to the history UDA using a `; ` delimiter.

---

### Edge Cases

- What happens when a task is started without passing an `assignee` argument when prior tasks are running? (Unassigned tasks are managed under an `unassigned` assignee scope using `TIMEWARRIORDB=~/.timewarrior/projects/<proj>/assignees/unassigned/`).
- What happens if stock `on-modify.timewarrior` hook is present in Taskwarrior hooks directory? (`setup.sh` disables executable bit `chmod -x` and renames to `.disabled` so it does not interfere).
- What happens if special characters or spaces exist in an assignee's or project's name? (Assignee and project names are sanitized to safe filesystem slugs, e.g. `proj_a`, `john_doe`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The setup script MUST be fully idempotent, allowing repeated execution without causing duplicate configurations, errors, or hook degradation.
- **FR-002**: The setup script MUST configure Taskwarrior UDA for `assignee` using `uda.assignee.type=string` and `uda.assignee.label=Assignee`.
- **FR-003**: The setup script MUST configure Taskwarrior UDA for accumulative assignee history using `uda.assigneehistory.type=string` and `uda.assigneehistory.label="Assignee History"`.
- **FR-004**: All UDA definitions and hook payloads MUST be fully compatible with Taskwarrior 3.x TaskChampion sync engine.
- **FR-005**: The system MUST intercept task `start` commands and assign/update the task's `assignee` attribute when passed.
- **FR-006**: The system MUST scope auto-stopping of active tasks on `start` strictly to tasks sharing the exact same `assignee` AND `project` values.
- **FR-007**: Active tasks belonging to different assignees or different projects MUST be permitted to run concurrently in `start` state in Taskwarrior.
- **FR-008**: The system MUST append `<ISO-8601-timestamp>: <assignee>` to the accumulative assignee history UDA whenever `assignee` is set or modified, separated by `; `, preserving all historical entries.
- **FR-009**: The setup script MUST detect whether Timewarrior is present on the system.
- **FR-010**: If Timewarrior is present, the system MUST configure per-project/per-assignee Timewarrior database directories (`~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/`).
- **FR-011**: If Timewarrior is present, the system MUST invoke `TIMEWARRIORDB=~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/ timew start/stop` hooks matching task start/stop events per project/assignee, allowing concurrent active Timewarrior intervals across different assignees or projects.
- **FR-012**: Assignee and project names used for filesystem directory paths MUST be sanitized to safe slugs while preserving full original strings in Taskwarrior UDAs.
- **FR-013**: The setup script MUST detect and disable any pre-existing stock `on-modify.timewarrior` hook script in the target hooks directory to prevent global timeline conflicts.

### Key Entities

- **Task**: Represents a Taskwarrior task item with attributes including status (`pending`, `active`, `completed`), `start` timestamp, `project`, `assignee`, and `assigneehistory`.
- **Assignee**: Plain string representing the person, agent, or role assigned to execute a task.
- **Assignee History**: Append-only log of assignment events containing semicolon-delimited ISO-8601 timestamped records (`YYYY-MM-DDTHH:MM:SSZ: Assignee`) of all current and former assignees for a given task.
- **Timewarrior Project/Assignee Database**: An isolated Timewarrior data folder located under `~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/` dedicated to tracking active time intervals for a single project/assignee pair.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of setup script runs complete cleanly with exit code 0 when executed 1, 2, or 10 consecutive times on a clean or pre-configured system.
- **SC-002**: Multiple tasks assigned to different assignees OR to the same assignee across different projects can be started and remain active simultaneously in Taskwarrior.
- **SC-003**: Starting a task for Alice in ProjA starts an active interval in `TIMEWARRIORDB=.../proja/assignees/alice` while Alice's active interval in `TIMEWARRIORDB=.../projb/assignees/alice` remains active simultaneously.
- **SC-004**: Reassigning a task 3 times results in all 3 assignment events recorded in chronological order in the task's `assigneehistory` UDA field.
- **SC-005**: Starting a task for Assignee A in ProjA stops 100% of currently active tasks for Assignee A in ProjA while 0% of active tasks for Assignee A in ProjB or Assignee B in ProjA are stopped.
- **SC-006**: Taskwarrior tasks with `assignee` and `assigneehistory` attributes sync cleanly with TaskChampion without errors or data loss.

## Assumptions

- Taskwarrior 3.x (or 2.x) with TaskChampion sync is installed and available in system PATH.
- Python 3 standard library is used for hook implementations.
- Unassigned tasks (where `assignee` is blank/empty) use `unassigned` as their isolation scope and Timewarrior database slug.
- Timewarrior per-project/per-assignee data directories will be created under `~/.timewarrior/projects/<project_slug>/assignees/<assignee_slug>/`.
- Assignee history entries use ISO-8601 UTC timestamps formatted as `YYYY-MM-DDTHH:MM:SSZ: <Assignee>` separated by `; `.
