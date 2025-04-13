import os
import json
from sheets import get_new_recipes
from recipes import create_markdown
from github_ops import commit_and_push_changes, create_pull_request

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/17DM2qFogUHGtHELX1qeQeRxQThXEqOZL6qnq9iT13bI/edit?gid=0"
    github_token = os.environ["GITHUB_TOKEN"]
    repo_url = "https://github.com/rooftopcellist/recipes"

    new_recipes = get_new_recipes(sheet_url)
    if not new_recipes:
        print("No new recipes found.")
        return

    for recipe in new_recipes:
        recipe_path, slug, extra_files = create_markdown(recipe)
        branch = f"add-{slug}"
        commit_and_push_changes(recipe_path, branch, repo_url, github_token, extra_files)
        create_pull_request(branch, github_token)

    latest_time = max([r["__timestamp"] for r in new_recipes])
    with open("processed_recipes.json", "w") as f:
        json.dump({"last_processed": latest_time.isoformat()}, f)

if __name__ == "__main__":
    main()
