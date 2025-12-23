"""
Image standardization utilities for recipe automation.

This module provides functions to standardize images to a consistent size,
format, and quality for use in recipe markdown files.
"""

import os
from PIL import Image

# Default settings for standardized images
DEFAULT_MAX_WIDTH = 800
DEFAULT_MAX_HEIGHT = 600
DEFAULT_FORMAT = "JPEG"
DEFAULT_QUALITY = 85


def standardize_image(
    input_path: str,
    output_path: str = None,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
    output_format: str = DEFAULT_FORMAT,
    quality: int = DEFAULT_QUALITY,
) -> str:
    """
    Standardize an image to a consistent size, format, and quality.

    Args:
        input_path: Path to the input image file.
        output_path: Path for the output image. If None, overwrites input file.
        max_width: Maximum width of the output image (default: 800).
        max_height: Maximum height of the output image (default: 600).
        output_format: Output format (default: "JPEG"). Supports JPEG, PNG, WEBP.
        quality: Output quality for lossy formats (1-100, default: 85).

    Returns:
        Path to the standardized image.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If quality is not between 1 and 100.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    if not 1 <= quality <= 100:
        raise ValueError(f"Quality must be between 1 and 100, got: {quality}")

    if output_path is None:
        output_path = input_path

    # Open and process the image
    with Image.open(input_path) as img:
        # Convert to RGB if necessary (for JPEG output)
        if output_format.upper() == "JPEG" and img.mode in ("RGBA", "P", "LA"):
            # Create a white background for transparent images
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif output_format.upper() == "JPEG" and img.mode != "RGB":
            img = img.convert("RGB")

        # Calculate new dimensions maintaining aspect ratio
        original_width, original_height = img.size
        
        # Only resize if the image is larger than the max dimensions
        if original_width > max_width or original_height > max_height:
            # Calculate the scaling factor
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_factor = min(width_ratio, height_ratio)

            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # Use LANCZOS for high-quality downscaling
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Save the image
        save_kwargs = {}
        if output_format.upper() in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        if output_format.upper() == "JPEG":
            save_kwargs["progressive"] = True

        img.save(output_path, format=output_format.upper(), **save_kwargs)

    return output_path


def get_image_info(image_path: str) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to the image file.

    Returns:
        Dictionary with image info (width, height, format, size_bytes).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": os.path.getsize(image_path),
        }


def main():
    """CLI entry point for image standardization."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Standardize images for recipe automation."
    )
    parser.add_argument("input", help="Path to the input image")
    parser.add_argument(
        "-o", "--output", help="Path for output image (default: overwrite input)"
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=DEFAULT_MAX_WIDTH,
        help=f"Maximum width (default: {DEFAULT_MAX_WIDTH})",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=DEFAULT_MAX_HEIGHT,
        help=f"Maximum height (default: {DEFAULT_MAX_HEIGHT})",
    )
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        choices=["JPEG", "PNG", "WEBP"],
        help=f"Output format (default: {DEFAULT_FORMAT})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help=f"Output quality 1-100 (default: {DEFAULT_QUALITY})",
    )

    args = parser.parse_args()

    # Get info before
    print(f"📷 Processing: {args.input}")
    before_info = get_image_info(args.input)
    print(f"   Before: {before_info['width']}x{before_info['height']} "
          f"{before_info['format']} ({before_info['size_bytes']:,} bytes)")

    # Standardize the image
    output = standardize_image(
        args.input,
        output_path=args.output,
        max_width=args.max_width,
        max_height=args.max_height,
        output_format=args.format,
        quality=args.quality,
    )

    # Get info after
    after_info = get_image_info(output)
    print(f"   After:  {after_info['width']}x{after_info['height']} "
          f"{after_info['format']} ({after_info['size_bytes']:,} bytes)")
    print(f"✅ Saved to: {output}")


if __name__ == "__main__":
    main()

