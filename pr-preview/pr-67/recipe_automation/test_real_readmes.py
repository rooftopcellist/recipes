#!/usr/bin/env python3
"""
Test script for the README.md update functionality with real README.md files.
"""

import os
import tempfile
import shutil
import re

def parse_readme_structure(content):
    """Parse the structure of a README.md file to identify sections."""
    lines = content.splitlines()
    structure = {
        'main_title': None,
        'sections': {},
        'default_section': None
    }
    
    # Find the main title (# Title)
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            structure['main_title'] = {
                'title': line.strip()[2:].strip(),
                'line_index': i
            }
            break
    
    # Find all sections (## or ### Section)
    section_pattern = re.compile(r'^#{2,3}\s+(.+)$')
    section_indices = []
    section_names = []
    section_levels = []
    
    for i, line in enumerate(lines):
        match = section_pattern.match(line.strip())
        if match:
            section_indices.append(i)
            section_names.append(match.group(1).strip())
            section_levels.append(line.count('#'))
    
    # Process each section
    for i, (idx, name, level) in enumerate(zip(section_indices, section_names, section_levels)):
        # Determine content start (line after section header)
        content_start = idx + 1
        
        # Determine content end (line before next section or end of file)
        content_end = len(lines) - 1
        if i < len(section_indices) - 1:
            content_end = section_indices[i + 1] - 1
        
        structure['sections'][name] = {
            'line_index': idx,
            'level': level,
            'content_start': content_start,
            'content_end': content_end
        }
    
    # Determine default section for adding new links
    if structure['sections']:
        # Try to find a section that looks like a list of recipes
        for name, section in structure['sections'].items():
            section_content = '\n'.join(lines[section['content_start']:section['content_end']+1])
            if re.search(r'\*\s+\[.+\]\(.+\.md\)', section_content):
                structure['default_section'] = name
                break
        
        # If no recipe list section found, use the first section
        if not structure['default_section']:
            structure['default_section'] = list(structure['sections'].keys())[0]
    
    return structure

def update_category_readme(category_path, recipe_name, slug):
    """Update the README.md file in the given category path with a link to the new recipe."""
    readme_path = os.path.join(category_path, "README.md")
    recipe_link = f"* [{recipe_name}]({slug}.md)\n"

    # Create the README with title and link if it doesn't exist
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# {os.path.basename(category_path).capitalize()}\n\n")
            f.write(recipe_link)
        return

    # Read existing content
    with open(readme_path, "r") as f:
        content = f.read()
        lines = content.splitlines(True)  # Keep line endings

    # Check if the link already exists
    if any(recipe_link.strip() == line.strip() for line in lines):
        return  # Link already present

    # Parse the README structure
    structure = parse_readme_structure(content)
    
    # Determine where to insert the new link
    new_lines = lines.copy()
    inserted = False
    
    # If we have sections, try to insert in the appropriate section
    if structure['sections'] and structure['default_section']:
        section = structure['sections'][structure['default_section']]
        section_start = section['content_start']
        section_end = section['content_end']
        
        # Look for the last recipe link in the section
        last_link_index = -1
        for i in range(section_start, section_end + 1):
            if i < len(lines) and re.search(r'\*\s+\[.+\]\(.+\.md\)', lines[i].strip()):
                last_link_index = i
        
        if last_link_index >= 0:
            # Insert after the last link
            new_lines.insert(last_link_index + 1, recipe_link)
        else:
            # Insert at the beginning of the section content, after any blank lines
            insert_index = section_start
            while insert_index < section_end and insert_index < len(lines) and not lines[insert_index].strip():
                insert_index += 1
            new_lines.insert(insert_index, recipe_link)
        
        inserted = True
    # If no appropriate section found, insert after the title
    elif structure['main_title']:
        insert_index = structure['main_title']['line_index'] + 1
        # If there's a blank line after the title, insert after that
        if insert_index < len(lines) and lines[insert_index].strip() == "":
            insert_index += 1
        new_lines.insert(insert_index, recipe_link)
        inserted = True
    # Fallback: just append to the end of the file
    if not inserted:
        # Ensure there's a blank line before adding the link if the file doesn't end with one
        if new_lines and not new_lines[-1].strip() == "":
            new_lines.append("\n")
        new_lines.append(recipe_link)

    with open(readme_path, "w") as f:
        f.writelines(new_lines)

def test_real_readmes():
    """Test the update_category_readme function with real README.md files."""
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="test_recipes_")
    try:
        # Test with dinner/README.md
        category_path = os.path.join(temp_dir, "dinner")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Dinner

## Babish Dinner

* [Moroccan Spagetti](./moroccan-spagetti.md) (3 Fancy stars out of 5)

## Did Cody Add To This?

* [Fried Tofu](./fried-tofu-over-rice.md)""")
        
        update_category_readme(category_path, "New Dinner Recipe", "new-dinner-recipe")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("Updated dinner README:", content)
        
        # Test with thanksgiving/README.md
        category_path = os.path.join(temp_dir, "thanksgiving")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Collection of the Best Thanksgiving Recipes

### Sides

* [Cranberry Sauce with Red Wine](./cranberry-sauce-red-wine.md)

### Turkeys
* 2019 - Dry-brine w/ rosemary butter - Docschick's family recipe
* 2020 - Buttermilk-Brined Roast Turkey - Samin Nosrat (NY Times)""")
        
        update_category_readme(category_path, "New Thanksgiving Recipe", "new-thanksgiving-recipe")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("\nUpdated thanksgiving README:", content)
        
        # Test with baking/README.md
        category_path = os.path.join(temp_dir, "baking")
        os.makedirs(category_path, exist_ok=True)
        with open(os.path.join(category_path, "README.md"), "w") as f:
            f.write("""# Baking Recipes

* [Banana Bread](./banana_bread.md)
* [Peanut Butter Cookies](./peanutbutter-cookies)""")
        
        update_category_readme(category_path, "New Baking Recipe", "new-baking-recipe")
        with open(os.path.join(category_path, "README.md"), "r") as f:
            content = f.read()
        print("\nUpdated baking README:", content)
        
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_real_readmes()
