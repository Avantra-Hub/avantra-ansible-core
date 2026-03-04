# Red Hat Automation Hub — Certification Reference

> Internal team reference document. Excluded from the collection build artifact via `galaxy.yml` `build_ignore`.


## Certification Requirements

### Minimum Versions

- `requires_ansible` in `meta/runtime.yml` must be `>= 2.16.0` (forward-looking policy).
- Python: `>= 3.12` (align with supported ansible-core versions).

### README Sections (Required)

The following sections are **required** by the Red Hat certified collection template:

1. **Description** — what the collection does
2. **Requirements** — Ansible and Python version prerequisites
3. **Installation** — how to install the collection
4. **Usage** — example playbooks or task snippets
5. **Support** — where users can get help (must distinguish vendor vs Red Hat support)
6. **Release Notes** — link to changelog or release notes
7. **License** — license name and link

### Sanity Ignore Files

Only keep ignore files for Ansible versions in `requires_ansible` range:
- Keep: `ignore-2.16.txt` through `ignore-2.20.txt`
- Remove any older files (e.g., `ignore-2.12.txt` through `ignore-2.15.txt`)

## Submission Process

### Manual Submission

1. Build the collection: `ansible-galaxy collection build`
2. Go to [console.redhat.com](https://console.redhat.com) > **Automation Hub** > **Partners**
3. Upload the `.tar.gz` artifact
4. Wait for automated checks + manual review by Red Hat Partner Engineering

### Automated Publishing (CI/CD)

The `release.yml` workflow includes a `publish-automation-hub` job that:
1. Downloads the built collection artifact
2. Publishes using `ansible-galaxy collection publish` with `AH_TOKEN` secret
3. Server: `https://cloud.redhat.com/api/automation-hub/`

### API Token Setup

1. Go to [console.redhat.com](https://console.redhat.com) > **Automation Hub** > **Connect to Hub**
2. Click **Load token** — this gives you an offline token (a long `refresh_token` string)
3. Go to the [Offline API token management](https://access.redhat.com/management/api) page to view/revoke tokens
4. Store the offline token as `AH_TOKEN` in the GitHub repo: **Settings** > **Environments** > create `automation-hub-publish` > add secret `AH_TOKEN`

> **Token expiry:** The offline token expires after **30 days of inactivity**. To keep it alive, run periodically:
> ```
> curl https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token \
>   -d grant_type=refresh_token -d client_id="cloud-services" \
>   -d refresh_token="<your_offline_token>" --fail --silent --show-error --output /dev/null
> ```

### Server URLs

| Purpose | URL |
|---------|-----|
| Automation Hub API (publish) | `https://cloud.redhat.com/api/automation-hub/` |
| Certified content (sync) | `https://console.redhat.com/api/automation-hub/content/published/` |
| Validated content (sync) | `https://console.redhat.com/api/automation-hub/content/validated/` |
| SSO Token Auth | `https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token` |

## Release Checklist

- [ ] `galaxy.yml` version matches intended git tag
- [ ] `meta/runtime.yml` `requires_ansible` is `>= 2.16.0`
- [ ] README.md has all required sections (Description, Requirements, Installation, Usage, Support, Release Notes, License)
- [ ] All README links are absolute URLs
- [ ] `CHANGELOG.rst` has entry for the new version
- [ ] `changelogs/changelog.yaml` has entry for the new version
- [ ] Test matrix only includes Python 3.12+ and Ansible 2.16+
- [ ] No stale `tests/sanity/ignore-2.1[0-5].txt` files
- [ ] `AH_TOKEN` secret configured in `automation-hub-publish` environment
- [ ] Tag pushed, release workflow completed successfully
- [ ] Collection visible on [Automation Hub](https://console.redhat.com/ansible/automation-hub)
