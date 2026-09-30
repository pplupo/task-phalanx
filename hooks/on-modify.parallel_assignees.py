#!/usr/bin/env python3
import sys
import os
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone

def sanitize_slug(name):
    if not name:
        return "unassigned"
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip().lower())
    return slug or "unassigned"

def get_timew_dir(assignee, project):
    assignee_slug = sanitize_slug(assignee)
    project_slug = sanitize_slug(project)
    
    base_timew = os.environ.get("TIMEWDATA")
    if not base_timew:
        base_timew = os.path.expanduser("~/.timewarrior")
    
    if "projects" in base_timew and "assignees" in base_timew:
        assignee_dir = base_timew
    else:
        assignee_dir = os.path.join(base_timew, "projects", project_slug, "assignees", assignee_slug)
    
    os.makedirs(assignee_dir, exist_ok=True)
    cfg_file = os.path.join(assignee_dir, "timew.cfg")
    if not os.path.exists(cfg_file):
        try:
            with open(cfg_file, "w") as f:
                f.write("# Timewarrior configuration for project/assignee\n")
        except Exception:
            pass
    return assignee_dir

def main():
    if os.environ.get("PARALLEL_ASSIGNEES_HOOK_ACTIVE") == "1":
        raw = sys.stdin.read().strip()
        lines = [line.strip() for line in raw.split('\n') if line.strip()]
        if len(lines) >= 2:
            print(lines[1])
        elif lines:
            print(lines[0])
        sys.exit(0)

    raw_input = sys.stdin.read().strip()
    if not raw_input:
        sys.exit(0)

    lines = [line.strip() for line in raw_input.split('\n') if line.strip()]
    if len(lines) < 2:
        if lines:
            print(lines[0])
        sys.exit(0)

    try:
        old_task = json.loads(lines[0])
        new_task = json.loads(lines[1])
    except Exception as e:
        sys.stderr.write(f"Error parsing task JSON: {e}\n")
        sys.exit(1)

    old_assignee = old_task.get("assignee", "")
    new_assignee = new_task.get("assignee", "")
    old_project = old_task.get("project", "")
    new_project = new_task.get("project", "")

    # 1. Update assignee history if assignee changed
    if new_assignee and new_assignee != old_assignee:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = f"{timestamp}: {new_assignee}"
        existing_history = new_task.get("assigneehistory", "")
        if existing_history:
            if not existing_history.endswith(entry):
                new_task["assigneehistory"] = f"{existing_history}; {entry}"
        else:
            new_task["assigneehistory"] = entry

    # 2. Check task active status and project/assignee pair changes
    was_active = bool(old_task.get("start"))
    is_active = bool(new_task.get("start"))
    pair_changed = (old_assignee != new_assignee) or (old_project != new_project)

    has_timew = shutil.which("timew") is not None

    # Stop Timewarrior on old pair if task was active AND (stopping OR moving to a new pair)
    if was_active and (not is_active or pair_changed):
        if has_timew:
            timew_dir = get_timew_dir(old_assignee, old_project)
            timew_env = os.environ.copy()
            timew_env["TIMEWDATA"] = timew_dir
            try:
                subprocess.run(
                    ["timew", "stop"],
                    env=timew_env,
                    capture_output=True,
                    text=True
                )
            except Exception as ex:
                sys.stderr.write(f"Failed to stop Timewarrior for old pair: {ex}\n")

    # Start Timewarrior & auto-stop conflicting tasks on new pair if task is active AND (starting OR moving from an old pair)
    if is_active and (not was_active or pair_changed):
        target_assignee = new_assignee
        target_project = new_project
        uuid_to_start = new_task.get("uuid", "")
        description = new_task.get("description", "Task")

        bg_code = (
            "import sys, os, json, time, subprocess; "
            "time.sleep(0.05); "
            "env = os.environ.copy(); "
            "env['PARALLEL_ASSIGNEES_HOOK_ACTIVE'] = '1'; "
            "target_assignee = sys.argv[1]; target_project = sys.argv[2]; curr_uuid = sys.argv[3]; "
            "res = subprocess.run(['task', 'rc.confirmation=no', 'status:pending', '+ACTIVE', 'export'], env=env, capture_output=True, text=True); "
            "tasks = json.loads(res.stdout) if res.returncode == 0 and res.stdout.strip() else []; "
            "[subprocess.run(['task', 'rc.confirmation=no', t['uuid'], 'stop'], env=env, capture_output=True) for t in tasks if t.get('uuid') != curr_uuid and t.get('assignee', '') == target_assignee and t.get('project', '') == target_project]"
        )
        
        try:
            subprocess.Popen(
                [sys.executable, "-c", bg_code, target_assignee, target_project, uuid_to_start],
                env=os.environ.copy(),
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as ex:
            sys.stderr.write(f"Failed to spawn auto-stop helper: {ex}\n")

        if has_timew:
            timew_dir = get_timew_dir(target_assignee, target_project)
            timew_env = os.environ.copy()
            timew_env["TIMEWDATA"] = timew_dir
            try:
                subprocess.run(
                    ["timew", "start", description, f"uuid:{uuid_to_start}"],
                    env=timew_env,
                    capture_output=True,
                    text=True
                )
            except Exception as ex:
                sys.stderr.write(f"Failed to start Timewarrior for new pair: {ex}\n")

    print(json.dumps(new_task))
    sys.exit(0)

if __name__ == "__main__":
    main()
