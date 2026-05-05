#!/usr/bin/env python3
"""
Test script to verify that README.md files are properly preserved when updating.
This version tests the new flow where README.md files are updated directly in the temporary directory.
"""

import os
import tempfile
import shutil
from git import Repo
from slugify import slugify
from recipes import create_markdown, update_category_readme
from github_ops import commit_and_push_changes

def setup_test_repo(repo_dir):
    """Set up a test Git repository with initial README.md files."""
    # Initialize a new Git repository
    repo = Repo.init(repo_dir)
    
    # Create a dinner directory with README.md
    dinner_dir = os.path.join(repo_dir, "dinner")
    os.makedirs(dinner_dir, exist_ok=True)
    
    # Create a README.md file in the dinner directory
    with open(os.path.join(dinner_dir, "README.md"), "w") as f:
        f.write("""# Dinner

## Babish Dinner

* [Moroccan Spagetti](./moroccan-spagetti.md) (3 Fancy stars out of 5)

## Did Cody Add To This?

* [Fried Tofu](./fried-tofu-over-rice.md)""")
    
    # Add and commit the files
    repo.git.add(all=True)
    repo.git.commit("-m", "Initial commit")
    
    return repo

def test_readme_preservation():
    """Test that README.md files are properly preserved when updating."""
    
    # Create temporary directories
    source_dir = tempfile.mkdtemp(prefix="source_repo_")
    clone_dir = tempfile.mkdtemp(prefix="clone_repo_")
    
    try:
        # Set up the source repository
        print("Setting up source repository...")
        source_repo = setup_test_repo(source_dir)
        
        # Create a mock recipe
        recipe = {
            "Recipe Name": "Test Recipe",
            "What category does this best fall under?": "dinner",
            "Ingredients": "Ingredient 1\nIngredient 2",
            "Instructions for Preparation": "Step 1\nStep 2",
            "Author (Your name)": "Test Author",
            "How many People does this serve?": "4",
            "Tips/Pairings/Note to Chef": "Test Notes",
            "Summary or flavor text": "Test Summary"
        }
        
        # Clone the repository
        print("\nCloning repository...")
        os.system(f"git clone {source_dir} {clone_dir}")
        repo = Repo(clone_dir)
        
        # Create a new branch
        branch = f"add-{slugify(recipe['Recipe Name'])}"
        new_branch = repo.create_head(branch)
        new_branch.checkout()
        
        # Create the markdown file and update README.md in the cloned repository
        print("\nCreating markdown file and updating README.md...")
        recipe_path, slug, extra_files = create_markdown(recipe, clone_dir)
        
        # Print the updated README.md content
        readme_path = os.path.join(clone_dir, "dinner", "README.md")
        print("\nUpdated README.md content:")
        with open(readme_path, "r") as f:
            updated_content = f.read()
            print(updated_content)
        
        # Verify that the README.md file has been properly updated
        assert "## Babish Dinner" in updated_content
        assert "[Moroccan Spagetti](./moroccan-spagetti.md)" in updated_content
        assert "## Did Cody Add To This?" in updated_content
        assert "[Fried Tofu](./fried-tofu-over-rice.md)" in updated_content
        assert "[Test Recipe](test-recipe.md)" in updated_content
        
        # Now simulate the commit_and_push_changes function
        print("\nSimulating commit_and_push_changes function...")
        
        # Create a temporary directory to simulate the source directory
        temp_source_dir = tempfile.mkdtemp(prefix="temp_source_")
        try:
            # Create the dinner directory
            os.makedirs(os.path.join(temp_source_dir, "dinner"), exist_ok=True)
            
            # Create a recipe file
            with open(os.path.join(temp_source_dir, "dinner", f"{slug}.md"), "w") as f:
                f.write("# Test Recipe\n\nThis is a test recipe.")
            
            # Create a README.md file
            with open(os.path.join(temp_source_dir, "dinner", "README.md"), "w") as f:
                f.write(updated_content)
            
            # Call commit_and_push_changes with cleanup=False to keep the temporary directory
            commit_and_push_changes(
                temp_dir=clone_dir,
                repo=repo,
                filepath=os.path.join("dinner", f"{slug}.md"),
                branch=branch,
                repo_url="file://" + source_dir,
                github_token="dummy_token",
                extra_files=["dinner/README.md"],
                cleanup=False
            )
            
            # Verify that the README.md file in the repository has been properly updated
            print("\nVerifying README.md content after commit_and_push_changes...")
            with open(readme_path, "r") as f:
                final_content = f.read()
                print(final_content)
            
            # Verify that the content is still correct
            assert "## Babish Dinner" in final_content
            assert "[Moroccan Spagetti](./moroccan-spagetti.md)" in final_content
            assert "## Did Cody Add To This?" in final_content
            assert "[Fried Tofu](./fried-tofu-over-rice.md)" in final_content
            assert "[Test Recipe](test-recipe.md)" in final_content
            
            print("\nTest passed! README.md file was properly preserved during the entire process.")
            
        finally:
            # Clean up the temporary source directory
            shutil.rmtree(temp_source_dir)
        
    finally:
        # Clean up the temporary directories
        shutil.rmtree(source_dir)
        shutil.rmtree(clone_dir)

if __name__ == "__main__":
    test_readme_preservation()
