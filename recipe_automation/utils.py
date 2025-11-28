import os
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

def get_category_path(category):
    root = "."
    fallback = "quick-meals"
    categories = {
        "baking": "baking",
        "cocktails": "cocktails",
        "desserts": "desserts",
        "dinner": "dinner",
        "brews": "brews",
        "meal prep": "meal-prep",
        "sauces": "sauces",
        "smoothies": "smoothies",
        "thanksgiving": "thanksgiving"
    }
    return os.path.join(root, categories.get(category.strip().lower(), fallback))

def extract_file_id(url):
    if "id=" in url:
        return url.split("id=")[-1].split("&")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    return None

def parse_readme_structure(content):
    """Parse the structure of a README.md file to identify sections.

    Returns:
        dict: A dictionary with section names as keys and their line indices as values.
              Special key 'main_title' contains the main title of the README.
              Special key 'default_section' contains the best section to add new links.
    """
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

def download_image_from_drive(file_id, dest_path):
    creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        _, done = downloader.next_chunk()
