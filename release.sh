#!/bin/bash
set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: You have uncommitted changes. Please commit or stash them first."
  exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -m1 'version =' pyproject.toml | cut -d '"' -f 2)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Determine new version
BUMP_TYPE=$1
case $BUMP_TYPE in
  patch)
    PATCH=$((PATCH + 1))
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  *)
    echo "Usage: ./release.sh {patch|minor|major}"
    exit 1
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "Bumping version: $CURRENT_VERSION -> $NEW_VERSION"

# Update version in pyproject.toml
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Commit and Tag
git add pyproject.toml
git commit -m "chore: release v$NEW_VERSION"
git tag "v$NEW_VERSION"

# Push
echo "🚀 Pushing changes and tag to GitHub..."
git push origin main
git push origin "v$NEW_VERSION"

echo "✅ Success! Version v$NEW_VERSION pushed. GitHub Actions will handle the rest."
