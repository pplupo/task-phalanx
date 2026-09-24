#!/usr/bin/env python3
import sys
import json
from datetime import datetime, timezone

def main():
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        sys.exit(0)

    try:
        task = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"Error parsing task JSON: {e}\n")
        sys.exit(1)

    assignee = task.get("assignee")
    if assignee:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = f"{timestamp}: {assignee}"
        existing_history = task.get("assigneehistory", "")
        if existing_history:
            task["assigneehistory"] = f"{existing_history}; {entry}"
        else:
            task["assigneehistory"] = entry

    print(json.dumps(task))
    sys.exit(0)

if __name__ == "__main__":
    main()
