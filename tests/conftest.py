import os
import shutil
import subprocess
import tempfile
import unittest

class TaskRunner:
    def __init__(self, env, tmp_path, hooks_dir, taskdata, timewdata):
        self.env = env
        self.tmp_path = tmp_path
        self.hooks_dir = hooks_dir
        self.taskdata = taskdata
        self.timewdata = timewdata

    def task(self, *args, check=True):
        cmd = ["task", "rc.confirmation=no"] + list(args)
        res = subprocess.run(cmd, env=self.env, capture_output=True, text=True)
        if check and res.returncode != 0:
            raise RuntimeError(f"Taskwarrior command failed ({res.returncode}): {res.stderr}\nOutput: {res.stdout}")
        return res

    def timew(self, *args, check=True, timewdata=None):
        cmd = ["timew"] + list(args)
        run_env = self.env.copy()
        if timewdata:
            run_env["TIMEWDATA"] = str(timewdata)
        res = subprocess.run(cmd, env=run_env, capture_output=True, text=True)
        if check and res.returncode != 0:
            raise RuntimeError(f"Timewarrior command failed ({res.returncode}): {res.stderr}\nOutput: {res.stdout}")
        return res

    def install_hooks(self, source_hooks_dir):
        for item in os.listdir(source_hooks_dir):
            s = os.path.join(source_hooks_dir, item)
            d = os.path.join(self.hooks_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                os.chmod(d, 0o755)

class IsolatedEnvironmentTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="tw_test_")
        taskdata = os.path.join(self.test_dir, "taskdata")
        hooks_dir = os.path.join(taskdata, "hooks")
        os.makedirs(taskdata, exist_ok=True)
        os.makedirs(hooks_dir, exist_ok=True)

        taskrc = os.path.join(self.test_dir, "taskrc")
        with open(taskrc, "w") as f:
            f.write(f"data.location={taskdata}\nconfirmation=no\n")

        timewdata = os.path.join(self.test_dir, "timewarrior")
        os.makedirs(timewdata, exist_ok=True)

        env = os.environ.copy()
        env["TASKRC"] = taskrc
        env["TASKDATA"] = taskdata
        env["TIMEWDATA"] = timewdata

        self.runner = TaskRunner(env, self.test_dir, hooks_dir, taskdata, timewdata)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
