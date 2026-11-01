import os
import json
from slugify import slugify
from sheets import get_new_recipes
from recipes import create_markdown
from github_ops import clone_repository, commit_and_push_changes, create_pull_request

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
            recipe_name = recipe.get('Recipe Name', 'Unknown')
            print(f"\n🍽️ Processing recipe {i}/{len(new_recipes)}: {recipe_name}")

            # Create a branch name based on the recipe slug
            slug = slugify(recipe["Recipe Name"])
            branch = f"add-{slug}"

            # Clone the repository to a temporary directory
            try:
                temp_dir, repo = clone_repository(repo_url, github_token)

                # Create and checkout a new branch
                new_branch = repo.create_head(branch)
                new_branch.checkout()

                # Create the markdown file and update index.md in the temporary directory
                recipe_path, slug, extra_files = create_markdown(recipe, temp_dir)

                # Log the files that will be committed
                print(f"📝 Files to be committed:")
                print(f"  - Recipe: {recipe_path}")
                for file in extra_files:
                    file_type = "Index" if os.path.basename(file) == "index.md" else "Image" if file.startswith("images/") else "Other"
                    print(f"  - {file_type}: {file}")

                # Commit and push the changes
                print(f"🔄 Committing and pushing changes for {slug}...")
                if not commit_and_push_changes(temp_dir, repo, recipe_path, branch, repo_url, github_token, extra_files):
                    raise RuntimeError("Recipe push failed; stopping to preserve the retry timestamp")

                print(f"📝 Creating pull request for {slug}...")
                pr_url = create_pull_request(branch, github_token)

                if pr_url:
                    print(f"🎉 Recipe {slug} successfully processed and PR created/updated.")
                else:
                    raise RuntimeError("PR creation failed; stopping to preserve the retry timestamp")

            except Exception as e:
                print(f"❌ Error processing recipe {recipe_name}: {e}")
                import traceback
                traceback.print_exc()
                return

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
