Prepare and tag a new release of the avantra.core Ansible collection.

The user provides the version as: $ARGUMENTS

If no version argument is given, read the current version from `galaxy.yml`, show it, and ask what the new version should be.

## Steps

### 1. Validate version format
- The version MUST match the pattern `YY.MINOR.PATCH` (e.g., `25.3.2`)
- Abort if the format is invalid

### 2. Pre-flight checks
- Confirm you are on the `main` branch and it is clean (`git status`)
- Pull latest from origin (`git pull`)
- Confirm the version does not already exist as a git tag (`git tag -l`)

### 3. Create a release branch
```
git checkout -b release/<version>
```

### 4. Bump version in `galaxy.yml`
- Update the `version:` field to the new version

### 5. Generate the changelog
- Run `uv run antsibull-changelog release` to compile fragments into `CHANGELOG.rst` and `changelogs/changelog.yaml`
- If antsibull-changelog is not installed, install it first: `uv pip install antsibull-changelog antsibull-core`
- If there are no changelog fragments in `changelogs/fragments/`, warn the user and ask whether to continue with an empty release summary or abort

### 6. Verify results
- Show the diff of `CHANGELOG.rst` to confirm the changelog looks correct
- Verify `CHANGELOG.rst` contains a `v<version>` section header: `grep -q "^v<version>$" CHANGELOG.rst`
- Show the user a summary of what changed

### 7. Commit the release
```
git add galaxy.yml CHANGELOG.rst changelogs/
git commit -m "release: <version>"
```

### 8. Push and create PR
- Push the release branch: `git push -u origin release/<version>`
- Create a PR targeting `main` with title `release: <version>`
- Show the PR URL

### 9. Post-merge instructions
After the PR is created, remind the user:
> After merging the PR, run these commands to tag and trigger the release pipeline:
> ```
> git checkout main && git pull
> git tag <version>
> git push origin <version>
> ```
> Then approve the publish environments in GitHub Actions.
