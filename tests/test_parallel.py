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
        # Create Task A for Alice and Task B for Bob in same project
        self.runner.task("add", "Task A", "project:ProjA", "assignee:Alice")
        self.runner.task("add", "Task B", "project:ProjA", "assignee:Bob")

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

    def test_same_assignee_different_projects_parallel(self):
        # Create Task 1 for Alice in ProjA and Task 2 for Alice in ProjB
        self.runner.task("add", "Alice Task ProjA", "project:ProjA", "assignee:Alice")
        self.runner.task("add", "Alice Task ProjB", "project:ProjB", "assignee:Alice")

        # Start Alice Task ProjA
        self.runner.task("1", "start")
        time.sleep(0.2)

        # Start Alice Task ProjB -> Should NOT stop Alice Task ProjA because projects differ!
        self.runner.task("2", "start")
        time.sleep(0.2)

        res = self.runner.task("+ACTIVE", "export")
        active_tasks = json.loads(res.stdout)
        self.assertEqual(len(active_tasks), 2, f"Expected 2 active tasks across projects for Alice, got {len(active_tasks)}")

        projects = {t.get("project") for t in active_tasks}
        self.assertEqual(projects, {"ProjA", "ProjB"})

    def test_same_assignee_same_project_autostop(self):
        # Create Task 1 and Task 3 for Alice in ProjA, Task 2 for Bob in ProjA
        self.runner.task("add", "Alice Task 1", "project:ProjA", "assignee:Alice")
        self.runner.task("add", "Bob Task", "project:ProjA", "assignee:Bob")
        self.runner.task("add", "Alice Task 2", "project:ProjA", "assignee:Alice")

        # Start Alice Task 1
        self.runner.task("1", "start")
        time.sleep(0.2)

        # Start Bob Task
        self.runner.task("2", "start")
        time.sleep(0.2)

        # Start Alice Task 2 in ProjA -> Should stop Alice Task 1 (same project & assignee), leave Bob Task active
        self.runner.task("3", "start")
        time.sleep(0.3)

        res = self.runner.task("+ACTIVE", "export")
        active_tasks = json.loads(res.stdout)
        self.assertEqual(len(active_tasks), 2)

        descriptions = {t.get("description") for t in active_tasks}
        self.assertEqual(descriptions, {"Bob Task", "Alice Task 2"})

if __name__ == "__main__":
    unittest.main()
