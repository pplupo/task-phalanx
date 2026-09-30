import os
import subprocess
import unittest
from tests.conftest import IsolatedEnvironmentTestCase

class TestSetupIdempotency(IsolatedEnvironmentTestCase):
    def test_setup_idempotency(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        setup_script = os.path.join(repo_root, "setup.sh")

        # Create a dummy stock on-modify.timewarrior hook to verify setup disables it
        stock_hook = os.path.join(self.runner.hooks_dir, "on-modify.timewarrior")
        with open(stock_hook, "w") as f:
            f.write("#!/bin/sh\nexit 0\n")
        os.chmod(stock_hook, 0o755)

        # First execution
        res1 = subprocess.run([setup_script], env=self.runner.env, capture_output=True, text=True)
        self.assertEqual(res1.returncode, 0, f"Setup failed: {res1.stderr}")
        self.assertIn("task-phalanx setup complete!", res1.stdout)
        self.assertIn("Disabling stock on-modify.timewarrior hook", res1.stdout)

        # Verify stock hook disabled
        self.assertFalse(os.access(stock_hook, os.X_OK))

        # Second execution (idempotency check)
        res2 = subprocess.run([setup_script], env=self.runner.env, capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0, f"Second setup run failed: {res2.stderr}")
        self.assertIn("task-phalanx setup complete!", res2.stdout)

        # Verify UDAs in config
        cfg_type = self.runner.task("_get", "rc.uda.assignee.type").stdout.strip()
        self.assertEqual(cfg_type, "string")

        cfg_hist_type = self.runner.task("_get", "rc.uda.assigneehistory.type").stdout.strip()
        self.assertEqual(cfg_hist_type, "string")

if __name__ == "__main__":
    unittest.main()
