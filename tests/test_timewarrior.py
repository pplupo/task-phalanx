import os
import json
import subprocess
import time
import unittest
from tests.conftest import IsolatedEnvironmentTestCase

class TestTimewarriorParallel(IsolatedEnvironmentTestCase):
    def setUp(self):
        super().setUp()
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        setup_script = os.path.join(repo_root, "setup.sh")
        subprocess.run([setup_script], env=self.runner.env, capture_output=True, text=True, check=True)

    def test_per_project_assignee_timewarrior_tracking(self):
        # Create Task 1 for Alice in ProjA and Task 2 for Bob in ProjA
        self.runner.task("add", "Alice Task", "project:ProjA", "assignee:Alice")
        self.runner.task("add", "Bob Task", "project:ProjA", "assignee:Bob")

        # Start Task 1 (Alice)
        self.runner.task("1", "start")
        time.sleep(0.2)

        # Start Task 2 (Bob)
        self.runner.task("2", "start")
        time.sleep(0.2)

        # Check Alice's Timewarrior database under projects/proja/assignees/alice
        alice_timew_dir = os.path.join(self.runner.timewdata, "projects", "proja", "assignees", "alice")
        self.assertTrue(os.path.exists(alice_timew_dir), f"Alice Timewarrior directory {alice_timew_dir} should exist")
        
        alice_res = self.runner.timew("export", timewdata=alice_timew_dir)
        alice_intervals = json.loads(alice_res.stdout) if alice_res.stdout.strip() else []
        self.assertTrue(len(alice_intervals) > 0, "Alice Timewarrior database should have recorded interval")
        
        tags = [tag for i in alice_intervals for tag in i.get("tags", [])]
        self.assertTrue(any("Alice" in t for t in tags), f"Expected 'Alice' in tags, got tags={tags}")

        # Check Bob's Timewarrior database under projects/proja/assignees/bob
        bob_timew_dir = os.path.join(self.runner.timewdata, "projects", "proja", "assignees", "bob")
        self.assertTrue(os.path.exists(bob_timew_dir), f"Bob Timewarrior directory {bob_timew_dir} should exist")
        
        bob_res = self.runner.timew("export", timewdata=bob_timew_dir)
        bob_intervals = json.loads(bob_res.stdout) if bob_res.stdout.strip() else []
        self.assertTrue(len(bob_intervals) > 0, "Bob Timewarrior database should have recorded interval")

if __name__ == "__main__":
    unittest.main()
