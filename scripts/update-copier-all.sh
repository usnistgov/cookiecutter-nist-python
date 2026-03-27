#!/usr/bin/env bash
# Run update-copier on all of my repos
# extra options passed to gh workflow run

set -exu

repos=(
    usnistgov/cmomy
    usnistgov/tmmc-lnpy
    usnistgov/thermoextrap
    usnistgov/module-utilities
    usnistgov/pyproject2conda
    usnistgov/analphipy
    usnistgov/open-notebook
    usnistgov/uv-workon
    wpk-nist-gov/sync-pre-commit-hooks
    wpk-nist-gov/typecheck-runner
)

failed_repos=""
for repo in "${repos[@]}"; do
    echo "repo: $repo"
    if gh workflow run update-copier.yml --repo "$repo" "$@"; then
        echo "Successfully triggered workflow for $repo"
    else
        echo "ERROR: Failed to trigger workflow for $repo" >&2
        failed_repos="$failed_repos $repo"
    fi
done

if [ -n "$failed_repos" ]; then
    echo "The following repositories failed to trigger the workflow:" >&2
    for repo in $failed_repos; do
        echo "  - $repo" >&2
    done
    exit 1
else
    echo "All repositories processed successfully."
fi
