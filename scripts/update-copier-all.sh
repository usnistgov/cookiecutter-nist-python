# Run update-copier on all of my repos

repos="
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
"

for repo in $repos; do
    echo "repo: $repo"
    gh workflow run update-copier.yml --repo $repo
done
