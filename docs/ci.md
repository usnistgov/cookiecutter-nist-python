# Github actions setup

The following should be setup on the github page of the repo.

## Copier/cruft update

To use the cruft/copier-update workflow, you should setup the a github token.
Otherwise, updates to workflow files will fail, and pull requests will not
trigger `on: push` or `on: pull_request` workflows.

- Enable
  [pull requests from workflows](https://github.blog/changelog/2022-05-03-github-actions-prevent-github-actions-from-creating-and-approving-pull-requests/)
  under `Settings -> Actions -> General` tab of the github repo.
- Add (fine-grained or classic) personal access token.
  - [Create token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    with `contents: write`, `pull_requests: write` and `workflows: write`
    permissions.
  - Under `Settings -> Secrets and variables -> Actions -> Secrets` add `PAT`
    with generated token. You can also use [gh](https://cli.github.com/) using

   ```bash
    gh secret set PAT
    ```

## Trusted publishing

Generated repos use [trusted publishing] to release the code to
[pypi](https://pypi.org/) and [test.pypi](https://test.pypi.org/). This requires
defining the environments `pypi` and `test-pypi`, which can be created under
`Settings -> Environments` of the github repo.

## Rules

It is a good idea to setup a merge rule. This can be done under
`Settings -> Rules -> Rulesets`, using something like the following:

- Add `main` to `Target branches` using `Include by pattern`
- Select `Require status checks to pass`. Add `pre-commit.ci - pr` and
  `required-checks-pass` to the `Status checks that are required` list.
