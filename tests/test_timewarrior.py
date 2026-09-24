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

    def test_per_assignee_timewarrior_tracking(self):
        # Create Task 1 for Alice and Task 2 for Bob
        self.runner.task("add", "Alice Task", "assignee:Alice")
        self.runner.task("add", "Bob Task", "assignee:Bob")

        # Start Task 1 (Alice)
        self.runner.task("1", "start")
        time.sleep(0.2)

        # Start Task 2 (Bob)
        self.runner.task("2", "start")
        time.sleep(0.2)

        # Check Alice's Timewarrior database
        alice_timew_dir = os.path.join(self.runner.timewdata, "assignees", "alice")
        self.assertTrue(os.path.exists(alice_timew_dir), f"Alice Timewarrior directory {alice_timew_dir} should exist")
        
        alice_res = self.runner.timew("export", timewdata=alice_timew_dir)
        alice_intervals = json.loads(alice_res.stdout) if alice_res.stdout.strip() else []
        
        self.assertTrue(len(alice_intervals) > 0, f"Alice Timewarrior database empty: stdout='{alice_res.stdout}', stderr='{alice_res.stderr}'")
        
        tags = [tag for i in alice_intervals for tag in i.get("tags", [])]
        self.assertTrue(any("Alice" in t for t in tags), f"Expected 'Alice' in tags, got tags={tags}")

if __name__ == "__main__":
    unittest.main()
