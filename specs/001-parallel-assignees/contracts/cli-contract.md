# CLI Contract: Taskwarrior Parallel Assignees and Timewarrior Integration

## Installer CLI Interface

### `setup.sh`
- **Purpose**: Idempotent configuration script for setting up Taskwarrior UDAs, TaskChampion compatibility, and installing hooks.
- **Invocation**: `./setup.sh`
- **Exit Codes**:
  - `0`: Success (UDAs configured, directories created, hooks installed/updated cleanly)
  - `1`: Error (Taskwarrior not installed or hook directory unwritable)
- **Output**:
  - `stdout`: Informative progress messages (e.g. `[OK] Taskwarrior UDA configured`, `[OK] TaskChampion sync compatibility verified`, `[OK] Per-assignee Timewarrior directories initialized`).
  - `stderr`: Error details on failure.

## Taskwarrior CLI Command Interfaces

### Setting Assignee on Task Creation
```bash
task add "Fix login bug" assignee:Alice
```
- **Behavior**: Creates task with `assignee="Alice"` and `assigneehistory="2026-09-23T10:00:00Z: Alice"`.

### Starting Task with Assignee
```bash
task 1 start
# OR
task 1 start assignee:Bob
```
- **Behavior**: 
  - Sets `assignee="Bob"` (if passed) and records history update.
  - Stops any currently active tasks assigned to `Bob`.
  - Leaves active tasks assigned to `Alice` running.
  - Executes `TIMEWDATA=~/.timewarrior/assignees/bob/ timew start ...` (if Timewarrior installed).

### Syncing via TaskChampion
```bash
task sync
```
- **Behavior**: Syncs all task modifications and UDA fields (`assignee`, `assigneehistory`) without error or schema conflict.

## Taskwarrior Hook Contract

### `on-modify.parallel_assignees.py`
- **Protocol**: Taskwarrior Hook Protocol v2 (`on-modify`)
- **Input (stdin)**: Line 1: JSON representation of original task object. Line 2: JSON representation of modified task object.
- **Output (stdout)**: JSON representation of final task object to persist.
- **Exit Code**: `0` on success.
