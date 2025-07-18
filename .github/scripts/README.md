# GitHub Workflow Permission Checker

This directory contains tools to ensure GitHub workflows have appropriate permissions.

## check-workflow-permissions.py

This script verifies that workflows performing git push operations have the required `contents: write` permission.

### Usage

```bash
python .github/scripts/check-workflow-permissions.py
```

### What it checks

The script examines all YAML files in `.github/workflows/` and:

1. **Identifies git push operations** - Looks for patterns like:
   - `git push`
   - `git commit && git push`
   - Actions that auto-commit changes
   - Other git operations that modify the repository

2. **Validates permissions** - Ensures workflows with git push operations have:
   - `contents: write` permission (either at workflow or job level)
   - Or `write-all` permissions

### Required Permission Format

If your workflow performs git push operations, add this permission:

```yaml
permissions:
  contents: write # required for pushing changes
```

Or at the job level:

```yaml
jobs:
  my-job:
    permissions:
      contents: write # required for pushing changes
    steps:
      # ... job steps that include git push
```

### Exit Codes

- `0`: All workflows have appropriate permissions
- `1`: One or more workflows need attention

### Example Output

```
✅ checks.yaml: No git push operations found
❌ deploy.yaml: Has git push operations but missing 'contents: write' permission
✅ release.yaml: Has git push operations and appropriate permissions
```

## Best Practices

1. **Minimal Permissions**: Only grant `contents: write` to workflows that actually need to push changes
2. **Clear Comments**: Add `# required for pushing changes` comment when adding `contents: write`
3. **Regular Validation**: Run the permission checker as part of CI/CD to catch issues early
4. **Job-Level Permissions**: Consider using job-level permissions instead of workflow-level for better security isolation