import os
import time
import json
import subprocess
import unittest
from tests.conftest import IsolatedEnvironmentTestCase

class TestParallelAssignees(IsolatedEnvironmentTestCase):
    def setUp(self):
        super().setUp()
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        setup_script = os.path.join(repo_root, "setup.sh")
        subprocess.run([setup_script], env=self.runner.env, capture_output=True, text=True, check=True)

    def test_parallel_task_execution_different_assignees(self):
        # Create Task A for Alice and Task B for Bob
        self.runner.task("add", "Task A", "assignee:Alice")
        self.runner.task("add", "Task B", "assignee:Bob")

        # Start Task A (Alice)
        self.runner.task("1", "start")
        time.sleep(0.2)
        
        # Start Task B (Bob)
        self.runner.task("2", "start")
        time.sleep(0.2)

        # Verify BOTH tasks are active (+ACTIVE)
        res = self.runner.task("+ACTIVE", "export")
        active_tasks = json.loads(res.stdout)
        self.assertEqual(len(active_tasks), 2, f"Expected 2 active tasks, got {len(active_tasks)}")

        assignees = {t.get("assignee") for t in active_tasks}
        self.assertEqual(assignees, {"Alice", "Bob"})

    def test_same_assignee_task_autostop(self):
        # Create Task 1 and Task 2 for Alice, Task 3 for Bob
        self.runner.task("add", "Alice Task 1", "assignee:Alice")
        self.runner.task("add", "Bob Task", "assignee:Bob")
        self.runner.task("add", "Alice Task 2", "assignee:Alice")

        # Start Alice Task 1
        self.runner.task("1", "start")
        time.sleep(0.2)

        # Start Bob Task
        self.runner.task("2", "start")
        time.sleep(0.2)

        # Start Alice Task 2 -> Should stop Alice Task 1, leave Bob Task active
        self.runner.task("3", "start")
        time.sleep(0.3)

        res = self.runner.task("+ACTIVE", "export")
        active_tasks = json.loads(res.stdout)
        self.assertEqual(len(active_tasks), 2)

        descriptions = {t.get("description") for t in active_tasks}
        self.assertEqual(descriptions, {"Bob Task", "Alice Task 2"})

if __name__ == "__main__":
    unittest.main()
