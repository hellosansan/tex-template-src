"""Removes newline characters within <p> tags in HTML files.

This script finds all files matching a specified glob pattern and removes any
newline characters found within the opening <p> and closing </p> tags.
The files are modified in-place.

Example:
    To process all .html files in the 'src' directory:
        $ python clean_html.py "src/*.html"

    To recursively process all .html files under the 'views' directory:
        $ python clean_html.py "views/**/*.html"
"""

import argparse
import glob
import os
import re


def _remove_newlines_in_paragraph(match_obj):
    """Removes newline characters from a regex match object's content.

    This function is intended to be used as the replacement argument for
    re.sub(). It takes a match object, gets the full matched string,
    and returns it after removing all newline characters.

    Args:
        match_obj: A regex match object from re.sub.

    Returns:
        The matched string with newline characters removed.
    """
    # group(0) contains the entire matched string, e.g., "<p>Line 1\nLine 2</p>"
    paragraph_content = match_obj.group(0)
    return paragraph_content.replace("\n", "").replace("\r", "")


def process_file(file_path):
    """Reads a file, removes newlines in <p> tags, and saves it back.

    Args:
        file_path (str): The path to the file to process.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # The re.DOTALL (or re.S) flag allows '.' to match any character,
        # including newlines. This is crucial for multi-line <p> tags.
        modified_content = re.sub(
            r"<p>.*?</p>",
            _remove_newlines_in_paragraph,
            original_content,
            flags=re.DOTALL,
        )

        if modified_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            print(f"Processed: {file_path}")
        else:
            print(f"No changes needed: {file_path}")

    except IOError as e:
        print(f"Error: Could not read or write file {file_path}. Reason: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {file_path}: {e}")


def main():
    """Parses command-line arguments and processes the files."""
    parser = argparse.ArgumentParser(
        description="Remove newline characters within <p> tags in specified files."
    )
    parser.add_argument(
        "path_pattern",
        type=str,
        help='Path pattern for the files to process, e.g., "src/*.html".',
    )

    args = parser.parse_args()

    # Use recursive=True to support the "**" wildcard for directories.
    file_list = glob.glob(args.path_pattern, recursive=True)

    if not file_list:
        print(f'Warning: No files found matching the pattern "{args.path_pattern}".')
        return

    print(f"Found {len(file_list)} files. Starting processing...")

    for file_path in file_list:
        if os.path.isfile(file_path):
            process_file(file_path)

    print("\nAll files have been processed.")


if __name__ == "__main__":
    main()
