#!/bin/bash
#
# This script releases a new version of the Python Agent.
#
# Usage:
# ./release.sh <version_number>

# Note: this is script is adapted from https://github.com/hypertrace/goagent/blob/main/release.sh

set -e

MAIN_BRANCH="main"
VERSION_FILE="./src/hypertrace/version.py"

function write_version_file {
cat > $2 <<EOL
# Code generated by ./release.sh. DO NOT EDIT.

"""Package version"""
__version__ = "$1"
EOL
}

function rollback_changes {
    git reset HEAD~2 --soft # reverts the last two commits
    git checkout . # drop all the changes
    git tag -d $1 # removes local tag
}

function commit_docs {
  git status -s
  git add ./docs
  git commit -m "docs: update docs" || true
}

if [[ -z $1 || "$1" == "--help" ]]; then
    echo "Usage: $0 <version_number>"
    exit 0
fi

VERSION=$1
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    echo "Invalid version \"$VERSION\". It should follow semver."
    exit 1
fi

MAJOR="$(cut -d'.' -f1 <<<"$VERSION")"
MINOR="$(cut -d'.' -f2 <<<"$VERSION")"
PATCH="$(cut -d'.' -f3 <<<"$VERSION")"

if [[ "$MAJOR" == "0" && "$MINOR" == "0" && "$PATCH" == "0" ]]; then
    echo "Version cannot be \"0.0.0\"."
    exit 1
fi

# TODO: add a check for making sure incremental version.

if [ ! -z "$(git status --porcelain)" ]; then
    echo "You have uncommitted files. Commit or stash them first."
    exit 1
fi

echo "Fetching remote tags..."
git fetch --all

if [ ! -z "$(git tag -l "$VERSION")" ]; then 
    echo "Version \"$VERSION\" already exists."
    exit 1
fi

git checkout $MAIN_BRANCH

echo "Fetching latest $MAIN_BRANCH..."
git pull origin $MAIN_BRANCH

echo "Verifying docs"
# Makes sure docs are up to date
tox -e pdoc
git diff-index --quiet HEAD ./docs || commit_docs

echo "Writing version file"
write_version_file $VERSION $VERSION_FILE
git add $VERSION_FILE

git commit -m "chore(version): changes version to $VERSION"

echo "Creating tag"
git tag -a "$VERSION" -m "Version $VERSION"

NEW_VERSION="$MAJOR.$MINOR.$(($PATCH+1))-dev"

echo "Writing version file for next iteration"
write_version_file $NEW_VERSION $VERSION_FILE
git add $VERSION_FILE

git commit -m "chore(version): prepares for next version $NEW_VERSION."

set +e
git push origin $MAIN_BRANCH
PUSH_RESULT_CODE=$?
set -e

if [ "$PUSH_RESULT_CODE" != "0" ]; then
    rollback_changes $VERSION
    echo "Failed to push to $MAIN_BRANCH"
    exit 1
fi

git push --tags
