# Implementation Plan: Taskwarrior Parallel Assignees and Timewarrior Integration

**Branch**: `001-parallel-assignees` | **Date**: 2026-09-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-parallel-assignees/spec.md`

## Summary

Implement an idempotent setup script and Taskwarrior hook system (`on-modify`, `on-add`) in Python 3 / Bash compatible with Taskwarrior 3.x TaskChampion sync. The solution introduces `assignee` and accumulative `assigneehistory` UDAs. Starting a task automatically stops active tasks belonging *only* to the same assignee (or unassigned scope), allowing tasks assigned to different assignees to run concurrently. If Timewarrior is installed, setup initializes per-assignee data directories (`~/.timewarrior/assignees/<assignee_slug>/`), invoking `TIMEWDATA` scoped commands so Timewarrior independently tracks parallel time intervals per assignee.

## Technical Context

**Language/Version**: Python 3 (hooks), Bash (setup script)

**Primary Dependencies**: Taskwarrior (`task` CLI v2/v3), TaskChampion sync, optional Timewarrior (`timew` CLI)

**Storage**: Taskwarrior UDA fields (`uda.assignee`, `uda.assigneehistory`) on task JSON objects; per-assignee Timewarrior data folders under `~/.timewarrior/assignees/`

**Testing**: Pytest / Bash unit and integration test scripts using isolated temporary `TASKRC`, `TASKDATA`, and `TIMEWDATA`

**Target Platform**: Linux / POSIX environment

**Project Type**: CLI tool & Taskwarrior extension hooks

**Performance Goals**: Hook processing completes in < 50ms per task invocation

**Constraints**: Idempotent installation; TaskChampion sync compatibility; zero external dependencies beyond Python 3 standard library and Taskwarrior/Timewarrior

**Scale/Scope**: Single setup script (`setup.sh`), hook script(s) in `hooks/`, test suite in `tests/`

## Constitution Check

*GATE: Passed prior to Phase 0 research and post Phase 1 design.*

- **Library-First / Modular**: Hooks and setup scripts are self-contained and modular.
- **CLI Interface**: Standard stdin/stdout JSON interface for Taskwarrior hooks; command line interface for `setup.sh`.
- **Test-First**: Full automated integration tests with isolated Taskwarrior instances prior to implementation.
- **Simplicity**: Procedural Python 3 hooks using standard library `json`, `sys`, and `os`. No bloated framework or dependencies.

## Project Structure

### Documentation (this feature)

```text
specs/001-parallel-assignees/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research decisions
├── data-model.md        # Data model and state transition rules
├── quickstart.md        # Quickstart & validation scenarios
└── contracts/
    └── cli-contract.md  # CLI and hook contract specification
```

### Source Code Structure

```text
setup.sh                 # Idempotent installation script
hooks/
├── on-add.parallel_assignees.py    # Assignee history tracking on task creation
└── on-modify.parallel_assignees.py # Parallel task start/stop, history, & TIMEWDATA invocation

tests/
├── conftest.py          # Isolated Taskwarrior & Timewarrior test environment fixtures
├── test_idempotency.py  # Tests for setup.sh repeatability
├── test_parallel.py     # Tests for parallel assignee task start/stop behavior
├── test_timewarrior.py # Tests for per-assignee TIMEWDATA interval tracking
└── test_history.py      # Tests for accumulative assigneehistory field
```

**Structure Decision**: Clean modular repository root with `setup.sh`, `hooks/` source directory, and `tests/` integration test suite.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | Fully aligned with KISS and single-writer principles |
