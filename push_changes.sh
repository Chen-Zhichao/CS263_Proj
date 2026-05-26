#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

usage() {
  cat <<'EOF'
Usage:
  ./push_changes.sh "commit message"

Example:
  ./push_changes.sh "Add dataset evaluation script"

What this does:
  1. Checks that .env is ignored and not tracked
  2. Stages your project changes
  3. Commits them with your message
  4. Pushes the current branch to GitHub

Before the first push, create an empty GitHub repo and connect it:
  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

commit_message="${1:-}"
if [[ -z "$commit_message" ]]; then
  echo "Missing commit message."
  usage
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This folder is not a Git repository yet. Run: git init"
  exit 1
fi

if [[ -f .env ]] && ! git check-ignore -q .env; then
  echo "Safety stop: .env exists but is not ignored by Git."
  echo "Add '.env' to .gitignore before pushing."
  exit 1
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "Safety stop: .env is already tracked by Git."
  echo "Run: git rm --cached .env"
  echo "Then commit that removal before pushing."
  exit 1
fi

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git symbolic-ref HEAD refs/heads/main
fi

echo "Current Git status:"
git status --short

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git add -A

if git diff --cached --name-only | grep -qx ".env"; then
  git restore --staged .env
  echo "Safety stop: .env was staged unexpectedly."
  exit 1
fi

if git diff --cached --quiet; then
  echo "No safe changes to commit after staging."
  exit 0
fi

git commit -m "$commit_message"

if ! git remote get-url origin >/dev/null 2>&1; then
  echo
  echo "Committed locally, but no GitHub remote named 'origin' is set."
  echo "Create an empty GitHub repo, then run:"
  echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
  echo "  git push -u origin main"
  exit 0
fi

current_branch="$(git branch --show-current)"

if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
  git push
else
  git push -u origin "$current_branch"
fi

echo "Done. Your code is pushed to GitHub."

