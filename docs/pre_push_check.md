# Pre-Push Checklist

Run through these checks before pushing changes to the remote.

## 1. Lint — Unused Imports & Style

`ansible-test sanity` runs **pylint** and **pep8** against all files under `plugins/` and `tests/`.

Common failures:
- `unused-import` — remove any import you're not using (e.g. `import pytest` when no fixtures are used)
- `pep8` line length — max 160 characters
- `validate-modules` — every parameter in `argument_spec` must be documented in a doc fragment or the module's `DOCUMENTATION` string

Quick local check (no venv needed):

```bash
# If you have pylint installed
pylint --disable=all --enable=unused-import tests/ plugins/
```

## 2. Sanity Tests

Requires `ansible-test` (ships with `ansible-core`).

```bash
# Run from the collection root (must be at ansible_collections/avantra/core)
# Option A: use the symlink
cd ~/.ansible/collections/ansible_collections/avantra/core

# Option B: or set ANSIBLE_COLLECTIONS_PATH
export ANSIBLE_COLLECTIONS_PATH=/path/to/parent/of/ansible_collections

# Run sanity for a specific Python version
ansible-test sanity --python 3.12 --verbose

# Run only a specific sanity test
ansible-test sanity --test pylint --python 3.12
ansible-test sanity --test pep8 --python 3.12
ansible-test sanity --test validate-modules --python 3.12
ansible-test sanity --test import --python 3.12
```

### Sanity ignore files

Located in `tests/sanity/ignore-{version}.txt`. Currently all versions (2.16–2.21) ignore
`validate-modules:missing-gplv3-license` for all module files (collection uses Apache-2.0).

If a sanity test failure is a known false positive, add it to the appropriate ignore file(s).

## 3. Unit Tests

```bash
# From the collection root
ansible-test units --python 3.12 --requirements --verbose

# Run a specific test file
ansible-test units --python 3.12 tests/unit/plugins/module_utils/test_avantra_api.py

# With coverage
ansible-test units --coverage --python 3.12 --requirements --verbose
ansible-test coverage report --requirements
```

### Running with pytest directly

If you don't want to use `ansible-test`, you can run pytest directly, but you must set
`PYTHONPATH` so that `ansible_collections.avantra.core` resolves:

```bash
PYTHONPATH=~/.ansible/collections pytest tests/unit/ -v
```

## 4. CI Matrix

The CI workflow (`.github/workflows/ci.yml`) tests against:

| Ansible | Python |
|---------|--------|
| 2.16    | 3.12   |
| 2.17    | 3.12   |
| 2.18    | 3.12, 3.13 |
| 2.19    | 3.12, 3.13 |
| 2.20    | 3.12, 3.13, 3.14 |
| devel   | 3.12, 3.13, 3.14 |

## 5. Git Hygiene

- [ ] `git diff --cached` — review staged changes
- [ ] No secrets in committed files (check `integration_config.yml` is in `.gitignore`)
- [ ] No debug `print()` statements left in production code
- [ ] Commit messages follow conventional format: `type(scope): description`

## 6. Integration Tests (Manual)

Integration tests run against a live Avantra instance and are **not** triggered on push.
They require `tests/integration/integration_config.yml` (gitignored).

```bash
# From the collection root
ansible-test integration --python 3.12 --requirements --verbose avantra_server
ansible-test integration --python 3.12 --requirements --verbose avantra_sapsystem
```

See `docs/avantra_api.md` for API details and credential setup.
