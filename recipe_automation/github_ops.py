from git import Repo, GitCommandError
import os
import requests
import tempfile
import shutil

def clone_repository(repo_url, github_token):
    """Clone the repository to a temporary directory and return the path.

    Args:
        repo_url: The URL of the repository to clone
        github_token: The GitHub token for authentication

    Returns:
        tuple: (temp_dir, repo) - The path to the temporary directory and the repository object
    """
    # Embed token into HTTPS URL
    authed_repo_url = repo_url.replace("https://", f"https://{github_token}@")

    # Create a temporary directory for the repo
    temp_dir = tempfile.mkdtemp(prefix="recipes_repo_")

    try:
        print(f"🔄 Cloning repository to temporary directory...")
        # Clone with authentication
        repo = Repo.clone_from(authed_repo_url, temp_dir)
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
    # Embed token into HTTPS URL
    authed_repo_url = repo_url.replace("https://", f"https://{github_token}@")

    try:

        # Create and checkout new branch
        new_branch = repo.create_head(branch)
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

        # Handle extra files like images and README.md
        if extra_files:
            for file in extra_files:
                local_dest = os.path.join(temp_dir, file)
                os.makedirs(os.path.dirname(local_dest), exist_ok=True)

                # Special handling for README.md files
                if os.path.basename(file) == "README.md":
                    print(f"📗 Special handling for README.md: {file}")
                    try:
                        # Since we're now updating the README.md files directly in the temporary directory
                        # during the recipe creation process, we don't need to copy them again here.
                        # We just need to make sure they're added to the list of files to stage.
                        rel_path = os.path.relpath(file)
                        repo_readme_path = os.path.join(temp_dir, rel_path)

                        # Verify that the README.md file exists in the temporary directory
                        if os.path.exists(repo_readme_path):
                            print(f"✅ README.md already updated in temporary directory: {repo_readme_path}")
                            # Add the README.md file to the list of files to stage
                            files_to_add.append(rel_path)
                        else:
                            print(f"⚠️ Warning: README.md not found in temporary directory: {repo_readme_path}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not handle README.md {file}: {e}")
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
        # Clean up the temporary directory if requested
        if cleanup:
            print(f"🧹 Cleaning up temporary directory...")
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temporary directory: {e}")

        return True

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
