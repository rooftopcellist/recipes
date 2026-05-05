#!/usr/bin/env python3
"""
Test script for the README.md update functionality.
This script tests the new parse_readme_structure and update_category_readme functions.
"""

import os
import tempfile
import shutil
# Use our test utilities instead of the actual ones to avoid dependency issues
from test_utils import parse_readme_structure, update_category_readme

def test_parse_readme_structure():
    """Test the parse_readme_structure function with different README formats."""

    # Test with a simple README
    simple_readme = """# Simple Title

* [Recipe 1](recipe1.md)
* [Recipe 2](recipe2.md)
"""
    structure = parse_readme_structure(simple_readme)
    print("Simple README structure:", structure)
    assert structure['main_title']['title'] == "Simple Title"
    assert structure['default_section'] is None

    # Test with a README with sections
    sectioned_readme = """# Dinner

## Main Dishes

* [Recipe 1](recipe1.md)
* [Recipe 2](recipe2.md)

## Side Dishes

* [Side 1](side1.md)
"""
    structure = parse_readme_structure(sectioned_readme)
    print("Sectioned README structure:", structure)
    assert structure['main_title']['title'] == "Dinner"
    assert "Main Dishes" in structure['sections']
    assert "Side Dishes" in structure['sections']
    assert structure['default_section'] == "Main Dishes"

    # Test with a README like thanksgiving/README.md
    thanksgiving_readme = """# Collection of the Best Thanksgiving Recipes

### Sides

* [Cranberry Sauce with Red Wine](./cranberry-sauce-red-wine.md)

### Turkeys
* 2019 - Dry-brine w/ rosemary butter - Docschick's family recipe
* 2020 - Buttermilk-Brined Roast Turkey - Samin Nosrat (NY Times)
"""
    structure = parse_readme_structure(thanksgiving_readme)
    print("Thanksgiving README structure:", structure)
    assert structure['main_title']['title'] == "Collection of the Best Thanksgiving Recipes"
    assert "Sides" in structure['sections']
    assert "Turkeys" in structure['sections']
    assert structure['default_section'] == "Sides"

def test_update_category_readme():
    """Test the update_category_readme function with different README formats."""

    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="test_recipes_")
    try:
        # Test with a simple README
        category_path = os.path.join(temp_dir, "simple")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Simple Title

* [Recipe 1](recipe1.md)
* [Recipe 2](recipe2.md)
""")

        update_category_readme(category_path, "New Recipe", "new-recipe")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("Updated simple README:", content)
        assert "* [New Recipe](new-recipe.md)" in content

        # Test with a README with sections
        category_path = os.path.join(temp_dir, "sectioned")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Dinner

## Main Dishes

* [Recipe 1](recipe1.md)
* [Recipe 2](recipe2.md)

## Side Dishes

* [Side 1](side1.md)
""")

        update_category_readme(category_path, "New Main Dish", "new-main-dish")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("Updated sectioned README:", content)
        assert "* [New Main Dish](new-main-dish.md)" in content

        # Test with a README like thanksgiving/README.md
        category_path = os.path.join(temp_dir, "thanksgiving")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Collection of the Best Thanksgiving Recipes

### Sides

* [Cranberry Sauce with Red Wine](./cranberry-sauce-red-wine.md)

### Turkeys
* 2019 - Dry-brine w/ rosemary butter - Docschick's family recipe
* 2020 - Buttermilk-Brined Roast Turkey - Samin Nosrat (NY Times)
""")

        update_category_readme(category_path, "New Side Dish", "new-side-dish")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("Updated thanksgiving README:", content)
        assert "* [New Side Dish](new-side-dish.md)" in content

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing parse_readme_structure...")
    test_parse_readme_structure()
    print("\nTesting update_category_readme...")
    test_update_category_readme()
    print("\nAll tests passed!")
