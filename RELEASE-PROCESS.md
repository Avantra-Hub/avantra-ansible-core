# Release Process

This document describes how to create and publish a new release of the `avantra.core` Ansible collection.

## Prerequisites

- Write access to the repository
- `antsibull-changelog` installed locally (`pip install antsibull-changelog && uv pip install antsibull-core`)
- The `galaxy-publish` GitHub Environment must be configured with required reviewers
- The `GALAXY_API_KEY` secret must be set on the `galaxy-publish` environment (Ansible Galaxy API token)

## Versioning

This collection uses **year-based major versions** (e.g., `25.x.x` for 2025). Minor and patch versions are incremented for features and fixes within the year.

## Steps

### 1. Create a release branch

```shell
git checkout main && git pull
git checkout -b release/25.1.0
```

### 2. Bump the version

Edit `galaxy.yml` and update the `version` field:

```yaml
version: 25.1.0
```

### 3. Generate the changelog

Ensure all merged PRs have added their changelog fragments to `changelogs/fragments/`. Then compile them:

```shell
antsibull-changelog release
```

This updates `CHANGELOG.rst` and removes the processed fragment files.

### 4. Commit and open a PR

```shell
git add galaxy.yml CHANGELOG.rst changelogs/
git commit -m "Release 25.1.0"
git push -u origin release/25.1.0
```

Open a pull request targeting `main`. CI will run the full test matrix on the PR.

### 5. Merge the PR

Once the PR is reviewed and CI passes, merge it into `main`.

### 6. Tag the release

```shell
git checkout main && git pull
git tag 25.1.0
git push origin 25.1.0
```

The tag **must** match the version in `galaxy.yml` exactly, otherwise the release pipeline will fail.

### 7. Approve the Galaxy publish

The release pipeline runs automatically on tag push:

1. **Tests** — full sanity and unit test matrix
2. **Validate tag** — confirms the git tag matches `galaxy.yml`
3. **Build** — builds the collection artifact
4. **Docs** — builds Sphinx documentation

The pipeline then **pauses** at the Galaxy publish step, waiting for approval.

Go to **Actions** in GitHub, find the running release workflow, and approve the `galaxy-publish` environment deployment.

### 8. Automatic completion

After approval, the pipeline automatically:

- Publishes the collection to **Ansible Galaxy**
- Creates a **GitHub Release** with changelog notes and the `.tar.gz` artifact attached
- Deploys **documentation** to GitHub Pages under the version subdirectory

## Changelog Fragments

Each PR should include a changelog fragment in `changelogs/fragments/`. Create a YAML file named descriptively (e.g., `fix-login-timeout.yml`):

```yaml
bugfixes:
  - Fix login module timeout when server is unreachable.
```

Available categories: `major_changes`, `minor_changes`, `breaking_changes`, `deprecated_features`, `removed_features`, `security_fixes`, `bugfixes`, `known_issues`.
