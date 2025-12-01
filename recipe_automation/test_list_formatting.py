#!/usr/bin/env python3
"""
Tests for the list formatting functions in recipes.py.

Tests cover:
- strip_list_prefix(): Removing various bullet/number prefixes
- format_bulleted_list(): Converting raw text to bulleted lists
- format_numbered_list(): Converting raw text to numbered lists
"""

from recipes import strip_list_prefix, format_bulleted_list, format_numbered_list


def test_strip_list_prefix():
    """Test strip_list_prefix() with various input formats."""

    # Plain text without prefixes should remain unchanged
    assert strip_list_prefix("Salt") == "Salt"
    assert strip_list_prefix("1 teaspoon sugar") == "1 teaspoon sugar"
    assert strip_list_prefix("Mix well") == "Mix well"

    # Asterisk bullet prefix should be stripped
    assert strip_list_prefix("* Salt") == "Salt"
    assert strip_list_prefix("*Salt") == "Salt"
    assert strip_list_prefix("*  Salt") == "Salt"

    # Dash bullet prefix should be stripped
    assert strip_list_prefix("- Salt") == "Salt"
    assert strip_list_prefix("-Salt") == "Salt"
    assert strip_list_prefix("-  Salt") == "Salt"

    # Unicode bullet prefix should be stripped
    assert strip_list_prefix("• Salt") == "Salt"
    assert strip_list_prefix("•Salt") == "Salt"

    # Number with period prefix should be stripped
    assert strip_list_prefix("1. Step one") == "Step one"
    assert strip_list_prefix("1.Step one") == "Step one"
    assert strip_list_prefix("10. Step ten") == "Step ten"
    assert strip_list_prefix("99. Step ninety-nine") == "Step ninety-nine"

    # Number with parenthesis prefix should be stripped
    assert strip_list_prefix("1) Step one") == "Step one"
    assert strip_list_prefix("1)Step one") == "Step one"
    assert strip_list_prefix("10) Step ten") == "Step ten"

    # Number with colon prefix should be stripped
    assert strip_list_prefix("1: Step one") == "Step one"
    assert strip_list_prefix("1:Step one") == "Step one"

    # Double bullet with asterisk and dash should be stripped
    assert strip_list_prefix("* -1 teaspoon salt") == "1 teaspoon salt"
    assert strip_list_prefix("* - 1 teaspoon salt") == "1 teaspoon salt"
    assert strip_list_prefix("*-1 teaspoon salt") == "1 teaspoon salt"

    # Double numbered prefix should be stripped
    assert strip_list_prefix("1. 1. Step one") == "Step one"
    assert strip_list_prefix("2. 2. Step two") == "Step two"
    assert strip_list_prefix("1. 1. 1. Triple") == "Triple"

    # Mixed bullet and number prefix should be stripped
    assert strip_list_prefix("* 1. Item") == "Item"
    assert strip_list_prefix("- 1. Item") == "Item"

    # Empty string should return empty string
    assert strip_list_prefix("") == ""

    # Line with only prefix should return empty string
    assert strip_list_prefix("* ") == ""
    assert strip_list_prefix("1. ") == ""
    assert strip_list_prefix("- ") == ""

    # Whitespace should be properly handled
    assert strip_list_prefix("  * Salt  ") == "Salt"
    assert strip_list_prefix("  1. Step  ") == "Step"

    print("All strip_list_prefix tests passed!")


def test_format_bulleted_list():
    """Test format_bulleted_list() with various input formats."""

    # Plain text lines should be converted to bullets
    raw = "Salt\nPepper\nGarlic"
    expected = "* Salt\n* Pepper\n* Garlic"
    assert format_bulleted_list(raw) == expected

    # Already bulleted lines with asterisk should be normalized
    raw = "* Salt\n* Pepper\n* Garlic"
    expected = "* Salt\n* Pepper\n* Garlic"
    assert format_bulleted_list(raw) == expected

    # Already bulleted lines with dash should be normalized
    raw = "- Salt\n- Pepper\n- Garlic"
    expected = "* Salt\n* Pepper\n* Garlic"
    assert format_bulleted_list(raw) == expected

    # Double bullet prefixes should be cleaned up
    raw = "* -1 teaspoon sugar\n* -1 tablespoon water\n* -2 cups flour"
    expected = "* 1 teaspoon sugar\n* 1 tablespoon water\n* 2 cups flour"
    assert format_bulleted_list(raw) == expected

    # Empty lines should be removed from output
    raw = "Salt\n\nPepper\n\n\nGarlic"
    expected = "* Salt\n* Pepper\n* Garlic"
    assert format_bulleted_list(raw) == expected

    # Whitespace should be stripped from lines
    raw = "  Salt  \n  Pepper  \n  Garlic  "
    expected = "* Salt\n* Pepper\n* Garlic"
    assert format_bulleted_list(raw) == expected

    # Mixed formats should all be normalized
    raw = "* Salt\n- Pepper\n• Garlic\nOnion"
    expected = "* Salt\n* Pepper\n* Garlic\n* Onion"
    assert format_bulleted_list(raw) == expected

    print("All format_bulleted_list tests passed!")


def test_format_numbered_list():
    """Test format_numbered_list() with various input formats."""

    # Plain text lines should be converted to numbered list
    raw = "Mix ingredients\nBake at 350\nCool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Already numbered lines should be renumbered
    raw = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Double numbered prefixes should be cleaned up
    raw = "1. 1. Mix ingredients\n2. 2. Bake at 350\n3. 3. Cool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Incorrect numbering should be corrected
    raw = "5. Mix ingredients\n10. Bake at 350\n1. Cool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Empty lines should be removed from output
    raw = "Mix ingredients\n\nBake at 350\n\n\nCool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Whitespace should be stripped from lines
    raw = "  Mix ingredients  \n  Bake at 350  \n  Cool and serve  "
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    # Bulleted input should be converted to numbered list
    raw = "* Mix ingredients\n* Bake at 350\n* Cool and serve"
    expected = "1. Mix ingredients\n2. Bake at 350\n3. Cool and serve"
    assert format_numbered_list(raw) == expected

    print("All format_numbered_list tests passed!")


if __name__ == "__main__":
    test_strip_list_prefix()
    test_format_bulleted_list()
    test_format_numbered_list()
    print("\nAll list formatting tests passed!")

