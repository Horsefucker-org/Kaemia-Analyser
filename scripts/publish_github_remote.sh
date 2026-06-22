#!/usr/bin/env bash
set -euo pipefail

# Helper to add a GitHub remote and push the current branch, create initial release tag
# Usage: ./publish_github_remote.sh git@github.com:USERNAME/REPO.git

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <git-remote-url>"
  exit 1
fi
REMOTE=$1
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Adding remote origin=$REMOTE"
git remote add origin "$REMOTE" || git remote set-url origin "$REMOTE"

echo "Pushing branch $BRANCH to origin"
git push -u origin "$BRANCH"

echo "Create annotated tag v0.1.0"
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0

echo "Done. Visit https://github.com/$(echo $REMOTE | sed -E 's/.*github.com[:/]([^/]+\/[^/]+)(\.git)?/\1/')/releases" 
