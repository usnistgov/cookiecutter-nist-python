# Github actions setup

The following should be setup on the github page of the repo.

## Copier/cruft update

By default, the cruft/copier update workflows use `GITHUB_TOKEN` to create pull
requests. Enable [pull requests from workflows] under
`Settings -> Actions -> General` tab of the github repo.

To allow pull requests to trigger `on: push` and `on: pul_request` workflows,
and to update workflow files, you'll need to instead use a (fine-grained or
classic) personal access token.

- [Create token] with `contents: write`, `pull_requests: write` and
  `workflows: write` permissions.
- Under `Settings -> Secrets and variables -> Actions -> Secrets` add `PAT` with
  generated token. You can also use [gh] using

```bash
 gh secret set PAT
```

- Edit token in `.github/workflows/cruft[copier]-update.yml` to use
  `${{ secrets.PAT }}`

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

[pull requests from workflows]:
  https://github.blog/changelog/2022-05-03-github-actions-prevent-github-actions-from-creating-and-approving-pull-requests/
[Create token]:
  https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
[gh]: https://cli.github.com/
[pypi]: https://pypi.org/
[test.pypi]: https://test.pypi.org/
