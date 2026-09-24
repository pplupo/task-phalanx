import os
import json
import subprocess
import unittest
from tests.conftest import IsolatedEnvironmentTestCase

class TestAssigneeHistory(IsolatedEnvironmentTestCase):
    def setUp(self):
        super().setUp()
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        setup_script = os.path.join(repo_root, "setup.sh")
        subprocess.run([setup_script], env=self.runner.env, capture_output=True, text=True, check=True)

    def test_assignee_history_accumulation(self):
        # 1. Add task with initial assignee
        self.runner.task("add", "Feature Task", "assignee:Alice")
        
        t1 = json.loads(self.runner.task("1", "export").stdout)[0]
        self.assertEqual(t1.get("assignee"), "Alice")
        history1 = t1.get("assigneehistory", "")
        self.assertIn("Alice", history1)

        # 2. Modify assignee to Bob
        self.runner.task("1", "modify", "assignee:Bob")

        t2 = json.loads(self.runner.task("1", "export").stdout)[0]
        self.assertEqual(t2.get("assignee"), "Bob")
        history2 = t2.get("assigneehistory", "")
        self.assertIn("Alice", history2)
        self.assertIn("Bob", history2)
        self.assertIn("; ", history2)

        # 3. Modify assignee to Charlie
        self.runner.task("1", "modify", "assignee:Charlie")

        t3 = json.loads(self.runner.task("1", "export").stdout)[0]
        self.assertEqual(t3.get("assignee"), "Charlie")
        history3 = t3.get("assigneehistory", "")
        self.assertIn("Alice", history3)
        self.assertIn("Bob", history3)
        self.assertIn("Charlie", history3)

if __name__ == "__main__":
    unittest.main()
