# Github actions setup

The following should be setup on the github page of the repo.

## Copier/cruft update

By default, the generated repo will have `.github/workflows/copier-update.yml`
or `.github/workflows/cruft-update.yml`. These will periodically check for
updates to the template and create a pr with changes. These require a token to
trigger `on: push` and `on: pull_request` workflows, and to update workflow
files. Create the token using one of the following:

- [Classic personal access token][PAT-classic] with `repo` and `workflows` scope
- [Fine-grained personal access token][PAT-fine] with `contents: write`,
  `pull_requests: write` and `workflows: write` permissions.

Also, [allow workflows to create pull requests][pr-from-workflows]

Add the token to the github repo using either:

- Under `Settings -> Secrets and variables -> Actions -> Secrets` add `PAT` with
  generated token.
- Use [github cli][gh]:

  ```bash
  gh secret set PAT
  ```

## Trusted publishing

Generated repos use [trusted publishing] to release the code to [pypi] and
[test.pypi]. This requires defining the environments `pypi` and `test-pypi`,
which can be created under `Settings -> Environments` of the github repo.

## Rules

It is a good idea to setup a merge rule. This can be done under
`Settings -> Rules -> Rulesets`, using something like the following:

- Add `main` to `Target branches` using `Include by pattern`
- Select `Require status checks to pass`. Add `pre-commit.ci - pr` and
  `required-checks-pass` to the `Status checks that are required` list.

[pr-from-workflows]:
  https://github.blog/changelog/2022-05-03-github-actions-prevent-github-actions-from-creating-and-approving-pull-requests/
[gh]: https://cli.github.com/
[pypi]: https://pypi.org/
[test.pypi]: https://test.pypi.org/
[PAT-classic]:
  https://github.com/peter-evans/create-pull-request#:~:text=Classic-,Personal%20Access%20Token%20(PAT),-with%20repo%20scope
[PAT-fine]:
  https://github.com/peter-evans/create-pull-request#:~:text=Fine%2Dgrained-,Personal%20Access%20Token%20(PAT),-with%20contents%3A%20write
