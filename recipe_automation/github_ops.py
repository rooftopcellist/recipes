from git import Repo, GitCommandError
import os
import requests

def commit_and_push_changes(filepath, branch, repo_url, github_token, extra_files=None):
    # Embed token into HTTPS URL
    authed_repo_url = repo_url.replace("https://", f"https://{github_token}@")

    repo_dir = "/tmp/recipes_repo"
    if os.path.exists(repo_dir):
        os.system(f"rm -rf {repo_dir}")

    try:
        # Clone with authentication
        repo = Repo.clone_from(authed_repo_url, repo_dir)

        # Create and checkout new branch
        new_branch = repo.create_head(branch)
        new_branch.checkout()

        dest_path = os.path.join(repo_dir, filepath)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        os.system(f"cp {filepath} {dest_path}")

        # Copy extra files like images
        if extra_files:
            for file in extra_files:
                local_dest = os.path.join(repo_dir, file)
                os.makedirs(os.path.dirname(local_dest), exist_ok=True)
                os.system(f"cp {file} {local_dest}")

        # Stage diff
        repo.index.add([os.path.relpath(dest_path, repo_dir)])

        # Add both recipe and image(s)
        files_to_add = [os.path.relpath(dest_path, repo_dir)]
        if extra_files:
            files_to_add += [os.path.relpath(os.path.join(repo_dir, f), repo_dir) for f in extra_files]
        repo.index.add(files_to_add)

        # Commit changes
        repo.index.commit(f"Add recipe: {os.path.basename(filepath)}")

        # Set remote URL to include token and push
        origin = repo.remote()
        origin.set_url(authed_repo_url)
        origin.push(refspec=f"{branch}:{branch}")

        print(f"✅ Successfully pushed branch '{branch}'.")

    except GitCommandError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

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
