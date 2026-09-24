#!/usr/bin/env bash
set -euo pipefail

echo "==> Configuring task-phalanx (Taskwarrior & Timewarrior Parallel Assignees)..."

# 1. Verify Taskwarrior is installed
if ! command -v task &>/dev/null; then
    echo "Error: Taskwarrior (task) executable not found in PATH." >&2
    exit 1
fi

# 2. Configure UDAs idempotently with confirmation=no
echo "Setting up User Defined Attributes (UDAs)..."
task rc.confirmation=no config uda.assignee.type string >/dev/null 2>&1 || true
task rc.confirmation=no config uda.assignee.label Assignee >/dev/null 2>&1 || true

task rc.confirmation=no config uda.assigneehistory.type string >/dev/null 2>&1 || true
task rc.confirmation=no config uda.assigneehistory.label "Assignee History" >/dev/null 2>&1 || true

# 3. Determine hooks directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_HOOKS_DIR="${SCRIPT_DIR}/hooks"

if [ -n "${TASKDATA:-}" ]; then
    TARGET_HOOKS_DIR="${TASKDATA}/hooks"
else
    TARGET_HOOKS_DIR="${HOME}/.task/hooks"
fi

echo "Installing task-phalanx hooks into ${TARGET_HOOKS_DIR}..."
mkdir -p "${TARGET_HOOKS_DIR}"

if [ -d "${SOURCE_HOOKS_DIR}" ]; then
    for hook_file in "${SOURCE_HOOKS_DIR}"/*; do
        if [ -f "${hook_file}" ]; then
            filename="$(basename "${hook_file}")"
            cp "${hook_file}" "${TARGET_HOOKS_DIR}/${filename}"
            chmod +x "${TARGET_HOOKS_DIR}/${filename}"
            echo "  Installed: ${filename}"
        fi
    done
else
    echo "Warning: Source hooks directory (${SOURCE_HOOKS_DIR}) not found." >&2
fi

# 4. Timewarrior detection and setup
if command -v timew &>/dev/null; then
    echo "Timewarrior detected."
    if [ -n "${TIMEWDATA:-}" ]; then
        TIMEW_BASE="${TIMEWDATA}"
    else
        TIMEW_BASE="${HOME}/.timewarrior"
    fi
    ASSIGNEES_DIR="${TIMEW_BASE}/assignees"
    mkdir -p "${ASSIGNEES_DIR}"
    echo "  Initialized per-assignee Timewarrior directory: ${ASSIGNEES_DIR}"
else
    echo "Timewarrior not detected in PATH. Skipping Timewarrior directory creation."
fi

echo "==> task-phalanx setup complete!"
