from slugify import slugify
import os
import re
from utils import get_category_path, extract_file_id, download_image_from_drive, parse_readme_structure

def strip_list_prefix(line):
    """Remove any existing bullet or number prefix from a line.

    Handles:
    - Bullets: *, -, •
    - Numbers: 1., 1), 1:, etc.
    - Combinations like "* -" or "1. 1."
    """
    stripped = line.strip()
    # Keep stripping prefixes until no more are found
    changed = True
    while changed:
        changed = False
        # Strip bullet prefixes: *, -, •
        if stripped and stripped[0] in '*-•':
            stripped = stripped[1:].lstrip()
            changed = True
        # Strip number prefixes: digits followed by . or ) or :
        match = re.match(r'^(\d+)\s*[.):]\s*', stripped)
        if match:
            stripped = stripped[match.end():].lstrip()
            changed = True
    return stripped

def format_bulleted_list(raw):
    """Format raw text as a bulleted list.

    Strips any existing bullets/numbers and adds consistent bullet formatting.
    Each non-empty line becomes a bullet point.
    """
    lines = [strip_list_prefix(line) for line in raw.strip().splitlines()]
    lines = [line for line in lines if line]  # Remove empty lines
    return "\n".join(f"* {line}" for line in lines)

def format_numbered_list(raw):
    """Format raw text as a numbered list.

    Strips any existing bullets/numbers and adds consistent numbered formatting.
    Each non-empty line becomes a numbered step.
    """
    lines = [strip_list_prefix(line) for line in raw.strip().splitlines()]
    lines = [line for line in lines if line]  # Remove empty lines
    return "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))

def update_category_readme(category_path, recipe_name, slug, temp_dir=None):
    """Update the index.md file in the given category path with a link to the new recipe.

    Args:
        category_path: The path to the category directory
        recipe_name: The name of the recipe
        slug: The slug of the recipe
        temp_dir: The path to the temporary directory containing the cloned repository

    Returns:
        str: The path to the updated index.md file
    """
    # Determine the actual path to use (either in the temp_dir or local)
    if temp_dir:
        # Use the path in the temporary directory
        rel_category_path = os.path.relpath(category_path)
        actual_category_path = os.path.join(temp_dir, rel_category_path)
        print(f"📗 Updating index.md in temporary directory: {actual_category_path}")
    else:
        # Use the local path
        actual_category_path = category_path
        print(f"📗 Updating local index.md: {actual_category_path}")

    readme_path = os.path.join(actual_category_path, "index.md")
    recipe_link = f"* [{recipe_name}]({slug}.md)\n"

    # Create the index with navigation, title, and link if it doesn't exist
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("{% include nav.md %}\n\n")
            f.write(f"## {os.path.basename(category_path).capitalize()}\n\n")
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

    return readme_path

def create_markdown(recipe, temp_dir=None):
    """Create a markdown file for the recipe and update the index.md file.

    Args:
        recipe: The recipe data
        temp_dir: The path to the temporary directory containing the cloned repository

    Returns:
        tuple: (recipe_path, slug, extra_paths_to_add) - The path to the recipe file, the slug, and a list of extra files to commit
    """
    slug = slugify(recipe["Recipe Name"])
    category = recipe["What category does this best fall under?"]
    category_path = get_category_path(category)

    # Determine the actual path to use (either in the temp_dir or local)
    if temp_dir:
        # Use the path in the temporary directory
        rel_category_path = os.path.relpath(category_path)
        actual_category_path = os.path.join(temp_dir, rel_category_path)
        print(f"📝 Creating recipe in temporary directory: {actual_category_path}")
    else:
        # Use the local path
        actual_category_path = category_path
        print(f"📝 Creating recipe locally: {actual_category_path}")

    recipe_path = os.path.join(actual_category_path, f"{slug}.md")

    image_url = recipe.get("Upload a picture of your dish", "").strip()
    image_ref = ""
    extra_paths_to_add = []

    if image_url:
        file_id = extract_file_id(image_url)
        if file_id:
            # Create image directory in the appropriate location
            if temp_dir:
                # Use the path in the temporary directory
                rel_image_dir = os.path.relpath(os.path.join(category_path, "images"))
                image_dir = os.path.join(temp_dir, rel_image_dir)
            else:
                # Use the local path
                image_dir = os.path.join(category_path, "images")

            os.makedirs(image_dir, exist_ok=True)
            image_ext = "jpeg"
            image_path = os.path.join(image_dir, f"{slug}.{image_ext}")

            try:
                # Always download to the local path first
                local_image_dir = os.path.join(category_path, "images")
                os.makedirs(local_image_dir, exist_ok=True)
                local_image_path = os.path.join(local_image_dir, f"{slug}.{image_ext}")

                download_image_from_drive(file_id, local_image_path)

                # If using temp_dir, copy the image to the temp directory
                if temp_dir:
                    # Make sure the directory exists
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    # Copy the image to the temp directory
                    import shutil
                    shutil.copy2(local_image_path, image_path)
                    print(f"✅ Copied image to temporary directory: {image_path}")

                # Use the relative path for the markdown
                image_rel_path = os.path.join("images", f"{slug}.{image_ext}")
                image_ref = f"![{recipe['Recipe Name']}]({image_rel_path})\n"

                # Add the image path to the list of files to commit
                if temp_dir:
                    # Use the relative path for git staging
                    rel_image_path = os.path.relpath(os.path.join(category_path, "images", f"{slug}.{image_ext}"))
                    extra_paths_to_add.append(rel_image_path)
                else:
                    extra_paths_to_add.append(local_image_path)
            except Exception as e:
                print(f"❌ Failed to download image for {slug}: {e}")

    # Pull values and clean up whitespace
    author = str(recipe.get("Author (Your name)", "") or "").strip()
    serves = str(recipe.get("How many People does this serve?", "") or "").strip()
    notes = str(recipe.get("Tips/Pairings/Note to Chef", "") or "").strip()
    summary = str(recipe.get("Summary or flavor text", "") or "").strip()

    # Format fields
    ingredients = format_bulleted_list(recipe["Ingredients"])
    instructions = format_numbered_list(recipe["Instructions for Preparation"])

    # Start assembling markdown with navigation include
    content = "{% include nav.md %}\n\n"
    content += f"# {recipe['Recipe Name'].strip()}\n\n"

    if image_ref:
        content += image_ref + "\n"

    if summary:
        content += summary + "\n\n"

    if author:
        content += f"**Author:** {author}\n\n"
    if serves:
        content += f"**Serves:** {serves}\n\n"
    if notes:
        content += f"**Best Paired With:** {notes}\n\n"

    content += f"""## Ingredients

{ingredients}

## Directions

{instructions}

_Enjoy!_
"""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(recipe_path), exist_ok=True)

    # Write the recipe file
    with open(recipe_path, "w") as f:
        f.write(content)

    # ✅ Update the category index.md in the appropriate location
    readme_path = update_category_readme(category_path, recipe["Recipe Name"], slug, temp_dir)

    # Return all files for git staging
    if temp_dir:
        # Use relative paths for git staging
        rel_recipe_path = os.path.relpath(os.path.join(category_path, f"{slug}.md"))
        rel_readme_path = os.path.relpath(os.path.join(category_path, "index.md"))
        return rel_recipe_path, slug, extra_paths_to_add + [rel_readme_path]
    else:
        return recipe_path, slug, extra_paths_to_add + [os.path.join(category_path, "index.md")]
