#!/usr/bin/env python3
"""
Test script to verify that the clone-first approach works correctly.
"""

import os
import tempfile
import shutil
from slugify import slugify
from git import Repo
from recipes import create_markdown, update_category_readme
from github_ops import clone_repository

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

def test_clone_first_approach():
    """Test the clone-first approach."""
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
        
        # Commit the changes
        print("\nCommitting changes...")
        repo.git.add(all=True)
        repo.git.commit("-m", f"Add recipe: {recipe['Recipe Name']}")
        
        # Get the diff of the commit
        diff = repo.git.show("HEAD")
        print("\nDiff of the commit:")
        print(diff)
        
        print("\nTest passed! README.md file was properly updated in the cloned repository.")
        
    finally:
        # Clean up the temporary directories
        shutil.rmtree(source_dir)
        shutil.rmtree(clone_dir)

if __name__ == "__main__":
    test_clone_first_approach()
