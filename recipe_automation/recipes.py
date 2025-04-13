from slugify import slugify
import os
from utils import get_category_path, extract_file_id, download_image_from_drive

def format_bulleted_list(raw):
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return "\n".join(f"* {line}" for line in lines)

def format_numbered_list(raw):
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))

def create_markdown(recipe):
    slug = slugify(recipe["Recipe Name"])
    category = recipe["What category does this best fall under?"]
    category_path = get_category_path(category)
    recipe_path = os.path.join(category_path, f"{slug}.md")

    image_url = recipe.get("Upload a picture of your dish", "").strip()
    image_ref = ""

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
            except Exception as e:
                print(f"Failed to download image for {slug}: {e}")

    # Pull values and clean up whitespace
    author = str(recipe.get("Author (Your name)", "") or "").strip()
    serves = str(recipe.get("How many People does this serve?", "") or "").strip()
    notes  = str(recipe.get("Tips/Pairings/Note to Chef", "") or "").strip()
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

    return recipe_path, slug
