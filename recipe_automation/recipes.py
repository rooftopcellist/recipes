from slugify import slugify
import os
import re
from utils import get_category_path, extract_file_id, download_image_from_drive, parse_readme_structure

def format_bulleted_list(raw):
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return "\n".join(f"* {line}" for line in lines)

def format_numbered_list(raw):
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))

def update_category_readme(category_path, recipe_name, slug):
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

def create_markdown(recipe):
    slug = slugify(recipe["Recipe Name"])
    category = recipe["What category does this best fall under?"]
    category_path = get_category_path(category)
    recipe_path = os.path.join(category_path, f"{slug}.md")

    image_url = recipe.get("Upload a picture of your dish", "").strip()
    image_ref = ""
    extra_paths_to_add = []

    if image_url:
        file_id = extract_file_id(image_url)
        if file_id:
            image_dir = os.path.join(category_path, "images")
            os.makedirs(image_dir, exist_ok=True)
            image_ext = "jpeg"
            image_path = os.path.join(image_dir, f"{slug}.{image_ext}")
            try:
                download_image_from_drive(file_id, image_path)
                image_rel_path = os.path.relpath(image_path, category_path)
                image_ref = f"![{recipe['Recipe Name']}]({image_rel_path})\n"
                extra_paths_to_add.append(image_path)
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

    # Start assembling markdown
    content = f"# {recipe['Recipe Name'].strip()}\n\n"

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

    os.makedirs(category_path, exist_ok=True)
    with open(recipe_path, "w") as f:
        f.write(content)

    # ✅ Update the category README.md
    update_category_readme(category_path, recipe["Recipe Name"], slug)

    # Return all files for git staging
    return recipe_path, slug, extra_paths_to_add + [os.path.join(category_path, "README.md")]
