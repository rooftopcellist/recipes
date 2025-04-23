from git import Repo, GitCommandError
import os
import requests
import tempfile
import shutil

def commit_and_push_changes(filepath, branch, repo_url, github_token, extra_files=None):
    # Embed token into HTTPS URL
    authed_repo_url = repo_url.replace("https://", f"https://{github_token}@")

    # Create a temporary directory for the repo
    temp_dir = tempfile.mkdtemp(prefix="recipes_repo_")

    try:
        print(f"🔄 Cloning repository to temporary directory...")
        # Clone with authentication
        repo = Repo.clone_from(authed_repo_url, temp_dir)

        # Create and checkout new branch
        new_branch = repo.create_head(branch)
        new_branch.checkout()

        print(f"📝 Copying recipe files to temporary directory...")
        # Copy the recipe file
        dest_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(filepath, dest_path)

        # Copy extra files like images and README.md
        files_to_add = [os.path.relpath(dest_path, temp_dir)]
        if extra_files:
            for file in extra_files:
                local_dest = os.path.join(temp_dir, file)
                os.makedirs(os.path.dirname(local_dest), exist_ok=True)
                try:
                    shutil.copy2(file, local_dest)
                    files_to_add.append(os.path.relpath(local_dest, temp_dir))
                except Exception as e:
                    print(f"⚠️ Warning: Could not copy {file}: {e}")

        # Stage all files
        print(f"📋 Staging changes...")
        repo.index.add(files_to_add)

        # Commit changes
        print(f"💾 Committing changes...")
        repo.index.commit(f"Add recipe: {os.path.basename(filepath)}")

        # Set remote URL to include token and push
        print(f"🚀 Pushing branch '{branch}'...")
        origin = repo.remote()
        origin.set_url(authed_repo_url)
        origin.push(refspec=f"{branch}:{branch}")

        print(f"✅ Successfully pushed branch '{branch}'.")

    except GitCommandError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up the temporary directory
        print(f"🧹 Cleaning up temporary directory...")
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temporary directory: {e}")

def create_pull_request(branch, github_token):
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }
    data = {
        "title": f"Add new recipe: {branch}",
        "head": branch,
        "base": "main",
        "body": "Automatically generated recipe submission.",
    }
    response = requests.post(
        "https://api.github.com/repos/rooftopcellist/recipes/pulls",
        json=data,
        headers=headers
    )
    if response.status_code == 201:
        print("✅ PR created:", response.json()["html_url"])
    else:
        print("❌ PR creation failed:", response.text)
