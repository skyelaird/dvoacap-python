#!/bin/bash
# Manual wiki sync script
# Syncs markdown files from wiki/ directory to GitHub Wiki repository

set -e

REPO_NAME="skyelaird/dvoacap-python"
WIKI_URL="https://github.com/${REPO_NAME}.wiki.git"
WIKI_DIR="wiki-repo-temp"

echo "🔄 Starting wiki sync..."

# Check if wiki directory exists
if [ ! -d "wiki" ]; then
    echo "❌ Error: wiki/ directory not found"
    exit 1
fi

# Clone wiki repository
echo "📥 Cloning wiki repository..."
if [ -d "$WIKI_DIR" ]; then
    rm -rf "$WIKI_DIR"
fi

git clone "$WIKI_URL" "$WIKI_DIR" || {
    echo "❌ Error: Could not clone wiki repository"
    echo "Make sure the Wiki is enabled in repository settings and at least one page exists"
    exit 1
}

# Copy markdown files
echo "📋 Copying markdown files..."
cp wiki/*.md "$WIKI_DIR/"

# Commit and push
cd "$WIKI_DIR"
git config user.name "$(git config --global user.name)"
git config user.email "$(git config --global user.email)"

if git diff --quiet && git diff --cached --quiet; then
    echo "✅ No changes to sync"
    cd ..
    rm -rf "$WIKI_DIR"
    exit 0
fi

echo "💾 Committing changes..."
git add *.md
COMMIT_HASH=$(cd .. && git rev-parse --short HEAD)
git commit -m "Manual wiki sync from repository (commit: $COMMIT_HASH)"

echo "⬆️  Pushing to GitHub Wiki..."
git push origin master

cd ..
rm -rf "$WIKI_DIR"

echo "✅ Wiki synced successfully!"
