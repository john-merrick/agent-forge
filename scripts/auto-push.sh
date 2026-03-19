#!/bin/bash
# Auto-commit and push changes to GitHub when files change
# Runs via launchd — monitors the agent-forge directory

REPO_DIR="/Users/isaacboorer/codebase/agent-forge"
DEBOUNCE=10  # seconds to wait after last change before committing

cd "$REPO_DIR" || exit 1

# Debounce: wait for changes to settle
last_push=0

push_changes() {
    now=$(date +%s)
    # Skip if we pushed less than DEBOUNCE seconds ago
    if (( now - last_push < DEBOUNCE )); then
        return
    fi

    # Check for actual changes (staged or unstaged, excluding untracked noise)
    if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then
        return
    fi

    # Stage all tracked + new files (respects .gitignore)
    git add -A

    # Double-check there's something to commit
    if git diff --cached --quiet 2>/dev/null; then
        return
    fi

    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "auto: sync changes ($timestamp)"
    git push origin main 2>&1

    last_push=$(date +%s)
    echo "[$timestamp] Pushed changes to origin/main"
}

echo "Watching $REPO_DIR for changes..."

fswatch -o \
    --exclude '\.git' \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '\.pyc$' \
    --exclude 'data/agent_forge\.db' \
    --exclude 'agents/.*\.py$' \
    --exclude 'agents/.*\.md$' \
    --exclude '\.venv' \
    --exclude 'dist' \
    --latency 5 \
    "$REPO_DIR" | while read -r _; do
    # Drain any queued events (debounce)
    sleep "$DEBOUNCE"
    push_changes
done
