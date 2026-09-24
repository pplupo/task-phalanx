# Tasks: Taskwarrior Parallel Assignees and Timewarrior Integration

**Feature**: Taskwarrior Parallel Assignees and Timewarrior Integration  
**Feature Directory**: `specs/001-parallel-assignees`  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test harness setup

- [x] T001 Create project source and test directories (`hooks/`, `tests/`)
- [x] T002 [P] Configure pytest and isolated Taskwarrior/Timewarrior environment fixtures in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure setup script required before hook execution

- [x] T003 Implement idempotent Taskwarrior UDA registration (`uda.assignee.type=string`, `uda.assignee.label=Assignee`, `uda.assigneehistory.type=string`, `uda.assigneehistory.label="Assignee History"`) and hook installation in `setup.sh`

---

## Phase 3: User Story 1 - Idempotent Environment Configuration (Priority: P1) 🎯 MVP

**Goal**: Ensure setup script configures Taskwarrior UDAs and hooks idempotently across multiple executions without error or duplicate config.

**Independent Test**: Execute `setup.sh` 3 times in succession against clean and pre-configured environments in `tests/test_idempotency.py` and assert exit code 0 and valid Taskwarrior config.

### Tests for User Story 1

- [x] T004 [P] [US1] Write test cases for idempotent configuration and repeated execution in `tests/test_idempotency.py`

### Implementation for User Story 1

- [x] T005 [US1] Add configuration verification and error handling in `setup.sh`

---

## Phase 4: User Story 2 - Parallel Task Execution Scoped by Assignee with TaskChampion Sync (Priority: P2)

**Goal**: Intercept `start` commands so starting a task stops only active tasks belonging to the same assignee (or unassigned scope), allowing different assignees to run tasks concurrently, syncing cleanly via TaskChampion.

**Independent Test**: Start Task 1 for Alice and Task 2 for Bob in `tests/test_parallel.py`, asserting both tasks remain active simultaneously and export valid JSON.

### Tests for User Story 2

- [x] T006 [P] [US2] Write integration tests for parallel task execution and assignee-scoped task stopping in `tests/test_parallel.py`

### Implementation for User Story 2

- [x] T007 [P] [US2] Implement initial assignee history logging on task creation in `hooks/on-add.parallel_assignees.py`
- [x] T008 [US2] Implement assignee-scoped active task query, selective stopping, and JSON returning in `hooks/on-modify.parallel_assignees.py`

---

## Phase 5: User Story 3 - Per-Assignee Timewarrior Independent Interval Tracking (Priority: P3)

**Goal**: Detect Timewarrior and manage per-assignee data directories (`~/.timewarrior/assignees/<assignee_slug>/`) using `TIMEWDATA` so parallel tasks track time intervals independently.

**Independent Test**: Start Task 1 (Alice) and Task 2 (Bob) in `tests/test_timewarrior.py`, asserting active intervals exist concurrently in `TIMEWDATA=.../alice` and `TIMEWDATA=.../bob`.

### Tests for User Story 3

- [x] T009 [P] [US3] Write integration tests for per-assignee `TIMEWDATA` interval tracking in `tests/test_timewarrior.py`

### Implementation for User Story 3

- [x] T010 [US3] Add Timewarrior detection and `~/.timewarrior/assignees/<assignee_slug>/` directory initialization in `setup.sh`
- [x] T011 [US3] Integrate `TIMEWDATA=~/.timewarrior/assignees/<assignee_slug>/ timew start/stop` execution in `hooks/on-modify.parallel_assignees.py`

---

## Phase 6: User Story 4 - Accumulative Assignee History Tracking (Priority: P4)

**Goal**: Preserve full assignment history in `assigneehistory` UDA as `; `-delimited `<ISO-8601-UTC-timestamp>: <Assignee>` records.

**Independent Test**: Reassign a task 3 times in `tests/test_history.py` and verify all 3 timestamped events exist in `assigneehistory`.

### Tests for User Story 4

- [x] T012 [P] [US4] Write unit tests for accumulative `assigneehistory` formatting in `tests/test_history.py`

### Implementation for User Story 4

- [x] T013 [US4] Implement semicolon-delimited ISO-8601 history appending in `hooks/on-modify.parallel_assignees.py` and `hooks/on-add.parallel_assignees.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end validation

- [x] T014 [P] Create usage and configuration documentation in `README.md`
- [x] T015 Execute end-to-end quickstart validation scenarios from `specs/001-parallel-assignees/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Completed
- **Foundational (Phase 2)**: Completed
- **User Stories (Phases 3-6)**: Completed
- **Polish (Phase 7)**: Completed
