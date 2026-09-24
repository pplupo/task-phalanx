# Research: Taskwarrior Parallel Assignees and Timewarrior Integration

## Decisions and Rationale

### 1. Hook Language & Architecture
- **Decision**: Implement Taskwarrior hooks as Python 3 scripts (`on-modify.parallel_assignees.py`, `on-add.parallel_assignees.py`) and setup installer as an idempotent Bash script (`setup.sh`).
- **Rationale**: Python 3 natively parses and outputs JSON (which Taskwarrior hook protocol uses on standard input/output) reliably across Linux environments. Python standard library `json` and `sys` require zero external dependencies.

### 2. Taskwarrior Hook Execution Flow for Parallel Assignees
- **Decision**: Implement an `on-modify` hook that inspects incoming JSON task changes.
- **Mechanism**:
  - Taskwarrior hooks receive original task JSON and modified task JSON on stdin.
  - When a task transition indicates it is being started (i.e. `start` attribute is set or modified):
    - Retrieve the task's `assignee` UDA (default to `"unassigned"` if empty).
    - Query Taskwarrior for all active tasks (`status:pending +ACTIVE`).
    - Filter active tasks to those where `assignee` matches the started task's `assignee`, excluding the current task itself.
    - Invoke `task <uuid> stop` for each matching active task.
  - When `assignee` changes (on `on-add` or `on-modify`):
    - Append `<ISO-8601-UTC-timestamp>: <new_assignee>` to `assigneehistory` separated by `; `.

### 3. TaskChampion Sync Compatibility
- **Decision**: Configure UDAs (`uda.assignee`, `uda.assigneehistory`) using standard Taskwarrior UDA configuration commands.
- **Mechanism**:
  - Taskwarrior 3.x uses TaskChampion sync. Standard strings in UDAs are automatically serialized into task operations and synced cleanly.
  - Hooks do not modify TaskChampion sync tokens or conflict with task UUID identifiers.

### 4. Per-Assignee Timewarrior Database Architecture
- **Decision**: Use separate Timewarrior data folders per assignee using `TIMEWDATA=~/.timewarrior/assignees/<assignee_slug>/`.
- **Mechanism**:
  - Timewarrior's native engine only allows one active interval per data directory.
  - To track parallel active intervals for multiple assignees simultaneously, the hook derives a filesystem-safe slug for the assignee (e.g., `alice`, `bob`, `unassigned`).
  - The hook executes `TIMEWDATA=~/.timewarrior/assignees/<assignee_slug>/ timew start "<tags>"` when starting a task, and `TIMEWDATA=~/.timewarrior/assignees/<assignee_slug>/ timew stop` when stopping a task.
  - This enables true parallel, independent time tracking for Alice, Bob, and unassigned tasks without interval conflict.

### 5. Idempotency of Setup Script
- **Decision**: `setup.sh` checks current Taskwarrior config (`task _get rc.uda.assignee.type`) and hook installation paths before applying changes.
- **Mechanism**:
  - Executes `task config uda.assignee.type string` and `task config uda.assignee.label Assignee` idempotently.
  - Executes `task config uda.assigneehistory.type string` and `task config uda.assigneehistory.label "Assignee History"` idempotently.
  - Ensures directory structure `~/.timewarrior/assignees/` exists if Timewarrior is present.
  - Copies/symlinks hook scripts into `$TASKDATA/hooks/` (or `~/.task/hooks/`), making scripts executable (`chmod +x`).
  - Re-running `setup.sh` overwrites hook script binaries with latest version and verifies task configs without creating duplicates or throwing errors.
