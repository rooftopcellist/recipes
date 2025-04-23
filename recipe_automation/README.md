# 🥘 Recipe Submission Automation

This script automates the process of generating Pull Requests to your [recipes GitHub Pages site](https://github.com/rooftopcellist/recipes) from a Google Form submission.

When a new recipe is submitted through the form, the script:
- Reads the submission from the linked Google Sheet.
- Creates a properly formatted Markdown file in the appropriate recipe category.
- Downloads the uploaded photo from Google Drive.
- Creates a Git branch and commits the new recipe and image.
- Pushes the branch and opens a pull request to the main repository.

---

## 📦 Requirements

### ✅ Dependencies

Install required Python packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Required libraries include:
- `gspread`, `oauth2client` — for reading Google Sheets
- `google-api-python-client`, `google-auth` — for accessing uploaded photos via Google Drive
- `GitPython`, `requests` — for Git operations and creating GitHub pull requests
- `python-slugify` — for slug-safe filenames

---

## 🔑 Setup

### 1. **Clone This Repo**

```bash
git clone https://github.com/rooftopcellist/recipes.git
cd recipes/recipe-automation
```

### 2. **Create a Google Service Account**

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (if needed).
3. Enable **Google Sheets API** and **Google Drive API**.
4. Create a **service account** and download the `credentials.json` key file.
5. Place the `credentials.json` file in the root of this repo.
6. Share your Google Sheet with the **service account email** (`...@...gserviceaccount.com`) as an **Editor**.

### 3. **Update the Config**

Open `main.py` and set your Google Sheet URL:

```python
sheet_url = "https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0"
```

### 4. **Set Your GitHub Token**

Create a [GitHub personal access token](https://github.com/settings/tokens) with `repo` scope.

Set it as an environment variable before running the script:

```bash
export GITHUB_TOKEN=ghp_yourtokenvalue
```

### 5. **Track Processed Recipes**

Ensure `processed_recipes.json` exists and looks like:

```json
{
  "last_processed": "2024-01-01T00:00:00"
}
```

This helps the script skip previously submitted recipes.

---

## 🚀 Running the Script

To run the full automation:

```bash
python main.py
```

This will:
- Detect new submissions
- Generate a Markdown file and download the photo
- Push the recipe to a new branch
- Open a pull request on [rooftopcellist/recipes](https://github.com/rooftopcellist/recipes)

---

## 📂 Directory Mapping

Form submissions include a category field. Recipes are routed automatically to folders like:

| Category (Form)      | Folder in Repo     |
|----------------------|--------------------|
| Baking               | `baking/`          |
| Cocktails            | `cocktails/`       |
| Desserts             | `desserts/`        |
| Dinner               | `dinner/`          |
| Meal Prep            | `meal-prep/`       |
| Brews                | `brews/`           |
| Smoothies            | `smoothies/`       |
| Thanksgiving         | `thanksgiving/`    |
| Anything else        | `quick-meals/`     |

Photos are stored in a subdirectory `images/` within each category folder.

---

## 🥪 Example

If someone submits a *Banana Smoothie* to the "Smoothies" category:

```
smoothies/
├── images/
│   └── banana-smoothie.jpeg
├── banana-smoothie.md
└── README.md
```

And the Markdown includes an embedded image:

```markdown
![Banana Smoothie](images/banana-smoothie.jpeg)
```

---

## 🔄 Automating with GitHub Actions (Optional)

You can run this script daily using a GitHub Action or cron job. Ask for help if you’d like a `.github/workflows/recipe.yml` set up.

---

## 🧪 Testing

The recipe automation includes a comprehensive test suite to ensure everything works correctly. To run the tests:

```bash
./run_tests.py
```

This will run all the tests in the repository and provide a summary of the results.

The test suite includes:
- `test_clone_first.py` - Tests the clone-first approach
- `test_full_flow.py` - Tests the full flow of the recipe automation
- `test_github_ops.py` - Tests the GitHub operations
- `test_readme_preservation_v2.py` - Tests README.md preservation
- `test_readme_update.py` - Tests the README.md update function
- `test_real_readmes.py` - Tests with real README.md files
- `test_utils.py` - Tests utility functions

---

## 🖔 Troubleshooting

- **Images not downloading**: Ensure uploads are shared with the service account.
- **No PR created**: Confirm the GitHub token is exported and valid.
- **No recipes found**: Check the timestamp in `processed_recipes.json`.
- **Tests failing**: Run individual tests to debug (e.g., `python test_clone_first.py`).

---

## 📬 Questions?

Open an issue or reach out!

