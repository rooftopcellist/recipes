import os
import json
from sheets import get_new_recipes
from recipes import create_markdown
from github_ops import commit_and_push_changes, create_pull_request

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/17DM2qFogUHGtHELX1qeQeRxQThXEqOZL6qnq9iT13bI/edit?gid=0"
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_url = "https://github.com/rooftopcellist/recipes"

    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
        return

    try:
        print("📊 Fetching new recipes from Google Sheets...")
        new_recipes = get_new_recipes(sheet_url)
        if not new_recipes:
            print("ℹ️ No new recipes found.")
            return

        print(f"✅ Found {len(new_recipes)} new recipe(s) to process.")

        for i, recipe in enumerate(new_recipes, 1):
            print(f"\n🍽️ Processing recipe {i}/{len(new_recipes)}: {recipe.get('Recipe Name', 'Unknown')}")
            recipe_path, slug, extra_files = create_markdown(recipe)
            branch = f"add-{slug}"

            print(f"🔄 Committing and pushing changes for {slug}...")
            commit_and_push_changes(recipe_path, branch, repo_url, github_token, extra_files)

            print(f"📝 Creating pull request for {slug}...")
            pr_url = create_pull_request(branch, github_token)

            if pr_url:
                print(f"🎉 Recipe {slug} successfully processed and PR created/updated.")
            else:
                print(f"⚠️ Recipe {slug} processed but PR creation may have issues.")

    except Exception as e:
        print(f"❌ Error processing recipes: {e}")
        import traceback
        traceback.print_exc()
        return

    # Update the processed_recipes.json file with the latest timestamp
    try:
        latest_time = max([r["__timestamp"] for r in new_recipes])
        with open("processed_recipes.json", "w") as f:
            json.dump({"last_processed": latest_time.isoformat()}, f)
        print(f"✅ Updated processed_recipes.json with latest timestamp: {latest_time.isoformat()}")
    except Exception as e:
        print(f"⚠️ Warning: Could not update processed_recipes.json: {e}")

if __name__ == "__main__":
    main()
