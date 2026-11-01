from git import Repo, GitCommandError
import os
import requests
import tempfile
import shutil
import base64
from urllib.parse import urlsplit


def _auth_env(repo_url, github_token):
    """Supply credentials only to Git subprocesses, never remote URLs."""
    url = urlsplit(repo_url)
    if url.scheme != "https" or url.hostname != "github.com" or url.username or url.password:
        raise ValueError("Repository URL must be an unauthenticated GitHub HTTPS URL")
    credential = base64.b64encode(f"x-access-token:{github_token}".encode()).decode()
    return {
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
        "GIT_CONFIG_VALUE_0": f"Authorization: Basic {credential}",
        "GIT_TERMINAL_PROMPT": "0",
    }


def clone_repository(repo_url, github_token):
    """Clone the repository to a temporary directory and return the path.

    Args:
        repo_url: The URL of the repository to clone
        github_token: The GitHub token for authentication

    Returns:
        tuple: (temp_dir, repo) - The path to the temporary directory and the repository object
    """
    auth_env = _auth_env(repo_url, github_token)

    # Create a temporary directory for the repo
    temp_dir = tempfile.mkdtemp(prefix="recipes_repo_")

    try:
        print(f"🔄 Cloning repository to temporary directory...")
        # Clone with authentication
        repo = Repo.clone_from(repo_url, temp_dir, env=auth_env)
        return temp_dir, repo
    except Exception as e:
        # Clean up the temporary directory if cloning fails
        print(f"❌ Failed to clone repository: {e}")
        shutil.rmtree(temp_dir)
        raise

def commit_and_push_changes(temp_dir, repo, filepath, branch, repo_url, github_token, extra_files=None, cleanup=True):
    """Commit and push changes to the repository.

    Args:
        temp_dir: The path to the temporary directory containing the cloned repository
        repo: The repository object
        filepath: The path to the recipe file
        branch: The branch name
        repo_url: The URL of the repository
        github_token: The GitHub token for authentication
        extra_files: A list of extra files to commit
        cleanup: Whether to clean up the temporary directory after pushing

    Returns:
        bool: True if successful, False otherwise
    """
    auth_env = _auth_env(repo_url, github_token)

    try:

        # Create and checkout new branch
        new_branch = repo.heads[branch] if branch in repo.heads else repo.create_head(branch)
        new_branch.checkout()

        print(f"📝 Verifying recipe files in temporary directory...")
        # Since we're now creating the recipe files directly in the temporary directory,
        # we don't need to copy them again. We just need to make sure they exist.
        dest_path = os.path.join(temp_dir, filepath)
        if not os.path.exists(dest_path):
            print(f"⚠️ Warning: Recipe file not found in temporary directory: {dest_path}")
            # If the file doesn't exist in the temporary directory, it might be a local file
            # that needs to be copied (for backward compatibility)
            if os.path.exists(filepath):
                print(f"📝 Copying recipe file from local directory: {filepath}")
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(filepath, dest_path)
            else:
                raise FileNotFoundError(f"Recipe file not found: {filepath}")

        # Copy recipe file and prepare list of files to add
        files_to_add = [os.path.relpath(dest_path, temp_dir)]

        # Handle extra files like images and index.md
        if extra_files:
            for file in extra_files:
                local_dest = os.path.join(temp_dir, file)
                os.makedirs(os.path.dirname(local_dest), exist_ok=True)

                # Special handling for index.md files (category index pages)
                if os.path.basename(file) == "index.md":
                    print(f"📗 Special handling for index.md: {file}")
                    try:
                        # Since we're now updating the index.md files directly in the temporary directory
                        # during the recipe creation process, we don't need to copy them again here.
                        # We just need to make sure they're added to the list of files to stage.
                        rel_path = os.path.relpath(file)
                        repo_index_path = os.path.join(temp_dir, rel_path)

                        # Verify that the index.md file exists in the temporary directory
                        if os.path.exists(repo_index_path):
                            print(f"✅ index.md already updated in temporary directory: {repo_index_path}")
                            # Add the index.md file to the list of files to stage
                            files_to_add.append(rel_path)
                        else:
                            print(f"⚠️ Warning: index.md not found in temporary directory: {repo_index_path}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not handle index.md {file}: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    # Regular file handling (images, etc.)
                    try:
                        # Check if the file already exists in the temporary directory
                        if os.path.exists(local_dest):
                            print(f"✅ File already exists in temporary directory: {local_dest}")
                        else:
                            # If the file doesn't exist in the temporary directory, it might be a local file
                            # that needs to be copied (for backward compatibility)
                            if os.path.exists(file):
                                print(f"📝 Copying file from local directory: {file}")
                                shutil.copy2(file, local_dest)
                            else:
                                print(f"⚠️ Warning: File not found: {file}")

                        # Add the file to the list of files to stage
                        files_to_add.append(os.path.relpath(local_dest, temp_dir))
                    except Exception as e:
                        print(f"⚠️ Warning: Could not handle file {file}: {e}")

        # Stage all files
        print(f"📋 Staging changes...")
        repo.index.add(files_to_add)

        # Commit changes
        print(f"💾 Committing changes...")
        repo.index.commit(f"Add recipe: {os.path.basename(filepath)}")

        print(f"🚀 Pushing branch '{branch}'...")
        origin = repo.remote()
        origin.set_url(repo_url)
        with repo.git.custom_environment(**auth_env):
            push_info = origin.push(refspec=f"{branch}:{branch}")
            push_info.raise_if_error()
        print(f"✅ Successfully pushed branch '{branch}'.")
        return True

    except GitCommandError as e:
        print(f"❌ Git command failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up the temporary directory if requested
        if cleanup:
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
    check_response = requests.get(check_url, headers=headers, timeout=30)

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
        headers=headers,
        timeout=30
    )

    if response.status_code == 201:
        pr_url = response.json()["html_url"]
        print(f"✅ PR created: {pr_url}")
        return pr_url
    elif response.status_code == 422 and "A pull request already exists" in response.text:
        # PR exists but we couldn't find it in our first check
        print(f"✅ PR already exists for branch '{branch}'")
        # Try to get the PR URL
        check_response = requests.get(check_url, headers=headers, timeout=30)
        if check_response.status_code == 200 and check_response.json():
            pr_url = check_response.json()[0]["html_url"]
            print(f"✅ Found existing PR: {pr_url}")
            return pr_url
        return None
    else:
        print(f"❌ PR creation failed: {response.text}")
        return None
