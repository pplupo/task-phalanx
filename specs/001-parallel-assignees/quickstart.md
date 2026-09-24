# Quickstart & Validation Guide: Taskwarrior Parallel Assignees

## Prerequisites
- Taskwarrior 2.x / 3.x installed (`task --version`)
- Python 3 installed (`python3 --version`)
- (Optional) Timewarrior installed (`timew --version`)
- (Optional) TaskChampion sync configured (`task sync`)

## Installation
Run the setup script from repository root:
```bash
./setup.sh
```

To verify idempotency, execute the setup script a second time:
```bash
./setup.sh
```

## End-to-End Validation Scenarios

### Scenario 1: Parallel Task Execution for Different Assignees
1. Create two tasks for different assignees:
   ```bash
   task add "Frontend Task" assignee:Alice
   task add "Backend Task" assignee:Bob
   ```
2. Start the Frontend task for Alice:
   ```bash
   task 1 start
   ```
   Verify Task 1 is active (`task +ACTIVE` shows 1 task).

3. Start the Backend task for Bob:
   ```bash
   task 2 start
   ```
   Verify BOTH Task 1 and Task 2 are active (`task +ACTIVE` shows 2 active tasks).

### Scenario 2: Per-Assignee Timewarrior Interval Tracking
1. Inspect Alice's Timewarrior active tracking:
   ```bash
   TIMEWDATA=~/.timewarrior/assignees/alice timew
   ```
   **Expected Outcome**: Active interval for "Frontend Task".

2. Inspect Bob's Timewarrior active tracking:
   ```bash
   TIMEWDATA=~/.timewarrior/assignees/bob timew
   ```
   **Expected Outcome**: Active interval for "Backend Task" running concurrently.

### Scenario 3: Same Assignee Task Auto-Stopping
1. Create a second task for Alice:
   ```bash
   task add "Design Review" assignee:Alice
   ```
2. Start the Design Review task for Alice:
   ```bash
   task 3 start
   ```
3. Check active tasks:
   ```bash
   task +ACTIVE
   ```
   **Expected Outcome**: 
   - Task 1 (Alice's old task) is **stopped**.
   - Task 3 (Alice's new task) is **active**.
   - Task 2 (Bob's task) remains **active** simultaneously.

### Scenario 4: TaskChampion Synchronization
1. Sync tasks with TaskChampion backend:
   ```bash
   task sync
   ```
   **Expected Outcome**: Exit code 0, all UDAs (`assignee`, `assigneehistory`) synced cleanly across remote replica.
