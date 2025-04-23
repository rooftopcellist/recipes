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

        try:
            # First try a normal push
            push_info = origin.push(refspec=f"{branch}:{branch}")

            # Check if push was successful
            for info in push_info:
                if info.flags & info.ERROR:
                    print(f"⚠️ Push failed, trying force push: {info.summary}")
                    # If normal push fails, try force push
                    origin.push(refspec=f"{branch}:{branch}", force=True)
                    print(f"✅ Force push of branch '{branch}' successful.")
                    break
            else:
                print(f"✅ Successfully pushed branch '{branch}'.")

        except GitCommandError as e:
            if "rejected" in str(e) or "failed to push" in str(e):
                print(f"⚠️ Push rejected, trying force push...")
                # If push fails due to rejection, try force push
                origin.push(refspec=f"{branch}:{branch}", force=True)
                print(f"✅ Force push of branch '{branch}' successful.")
            else:
                # Re-raise if it's a different error
                raise

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

    # First check if a PR already exists for this branch
    print(f"🔍 Checking if PR already exists for branch '{branch}'...")
    check_url = f"https://api.github.com/repos/rooftopcellist/recipes/pulls?head=rooftopcellist:{branch}&state=open"
    check_response = requests.get(check_url, headers=headers)

    if check_response.status_code == 200 and check_response.json():
        # PR already exists
        pr_url = check_response.json()[0]["html_url"]
        print(f"✅ PR already exists: {pr_url}")
        return pr_url

    # Create a new PR
    print(f"📝 Creating new PR for branch '{branch}'...")
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
        pr_url = response.json()["html_url"]
        print(f"✅ PR created: {pr_url}")
        return pr_url
    elif response.status_code == 422 and "A pull request already exists" in response.text:
        # PR exists but we couldn't find it in our first check
        print(f"✅ PR already exists for branch '{branch}'")
        # Try to get the PR URL
        check_response = requests.get(check_url, headers=headers)
        if check_response.status_code == 200 and check_response.json():
            pr_url = check_response.json()[0]["html_url"]
            print(f"✅ Found existing PR: {pr_url}")
            return pr_url
        return None
    else:
        print(f"❌ PR creation failed: {response.text}")
        return None
