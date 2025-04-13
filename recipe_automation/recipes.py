from slugify import slugify
import os
from utils import get_category_path, extract_file_id, download_image_from_drive

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
        lines = f.readlines()

    # Check if the link already exists
    if any(recipe_link.strip() == line.strip() for line in lines):
        return  # Link already present

    # Insert the link just below the title
    new_lines = []
    inserted = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and line.strip().startswith("# "):
            new_lines.append(recipe_link)
            inserted = True

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
