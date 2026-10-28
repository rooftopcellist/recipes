# Maintainer Guide

This document covers maintenance tasks for the recipes site.

## Recipe Automation

The recipe automation script automatically creates pull requests from Google Form submissions.

### Setup

```bash
make setup-automation
```

This will:
- Create a Python virtual environment in `recipe_automation/venv`
- Install required dependencies from `requirements.txt`

### Running the Automation

Before running, ensure you have:
1. `GITHUB_TOKEN` environment variable set
2. `credentials.json` for Google API access in the `recipe_automation` directory

```bash
export GITHUB_TOKEN=your_github_token
make run-automation
```

### What the Script Does

1. Fetches new recipe submissions from Google Sheets
2. Creates properly formatted Markdown files
3. Downloads uploaded photos from Google Drive
4. Standardizes images to consistent size and format
5. Creates a Git branch and commits the new recipe
6. Opens a pull request to the main repository

See `recipe_automation/README.md` for more detailed setup instructions.

## Image Standardization

All recipe images are automatically standardized to ensure consistency across the site. This happens automatically when images are downloaded during recipe automation.

### Default Settings

| Setting | Default Value |
|---------|---------------|
| Max Width | 1024px |
| Max Height | 768px |
| Format | JPEG |
| Quality | 95% |

Images smaller than the max dimensions are not upscaled. Aspect ratio is always preserved.

### Standalone Image Processing

You can also standardize images manually using the Make target:

```bash
# Basic usage - standardizes in place
make standardize-image IMAGE=path/to/image.jpg

# Specify output file
make standardize-image IMAGE=input.jpg OUTPUT=output.jpg

# Custom dimensions
make standardize-image IMAGE=photo.jpg MAX_WIDTH=1024 MAX_HEIGHT=768

# Custom format and quality
make standardize-image IMAGE=photo.png FORMAT=WEBP QUALITY=90
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `IMAGE` | Input image path (required) | - |
| `OUTPUT` | Output path (optional, overwrites input if not set) | Same as input |
| `MAX_WIDTH` | Maximum width in pixels | 1024 |
| `MAX_HEIGHT` | Maximum height in pixels | 768 |
| `FORMAT` | Output format (JPEG, PNG, WEBP) | JPEG |
| `QUALITY` | Quality for lossy formats (1-100) | 95 |

### Programmatic Usage

The image utilities can also be used directly in Python:

```python
from image_utils import standardize_image, get_image_info

# Get info about an image
info = get_image_info("photo.jpg")
print(f"Size: {info['width']}x{info['height']}")

# Standardize an image
standardize_image("input.jpg", "output.jpg", max_width=1024, quality=90)
```
