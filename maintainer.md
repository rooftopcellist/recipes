# Maintainer Guide

This document covers maintenance tasks for the recipes site.

## Recipe Automation

The recipe automation script automatically creates pull requests from Google Form submissions.

### Setup

```bash
make setup-automation
```

This will:
- Create a Python virtual environment in `recipe_automation/venv`
- Install required dependencies from `requirements.txt`

### Running the Automation

Before running, ensure you have:
1. `GITHUB_TOKEN` environment variable set
2. `credentials.json` for Google API access in the `recipe_automation` directory

```bash
export GITHUB_TOKEN=your_github_token
make run-automation
```

### What the Script Does

1. Fetches new recipe submissions from Google Sheets
2. Creates properly formatted Markdown files
3. Downloads uploaded photos from Google Drive
4. Creates a Git branch and commits the new recipe
5. Opens a pull request to the main repository

See `recipe_automation/README.md` for more detailed setup instructions.

