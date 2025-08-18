"""Removes newline characters within <p> and <h1>-<h6> tags in HTML files.

This script finds all files matching a specified glob pattern and removes any
newline characters found within the opening and closing tags for <p> and
<h1> through <h6>. The files are modified in-place.

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


def _remove_newlines_in_tag_content(match_obj):
    """Removes newline characters from a regex match object's content.

    This function is intended to be used as the replacement argument for
    re.sub(). It takes a match object, gets the full matched string,
    and returns it after removing all newline characters.

    Args:
        match_obj: A regex match object from re.sub.

    Returns:
        The matched string with newline characters removed.
    """
    # group(0) contains the entire matched string, e.g., "<h1>Line 1\nLine 2</h1>"
    tag_content = match_obj.group(0)
    return tag_content.replace("\n", "").replace("\r", "")


def process_file(file_path):
    """Reads a file, removes newlines in tags, and saves it back.

    The processed tags include <p> and <h1> through <h6>.

    Args:
        file_path (str): The path to the file to process.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # UPDATED REGEX:
        # This regex now matches <p> tags and <h1> through <h6> tags.
        # <(h[1-6]|p) -> Captures 'h1', 'h2', ..., 'h6', or 'p' as group 1.
        # .*?>         -> Matches any attributes within the opening tag.
        # .*?          -> Matches the content inside the tag.
        # </\1>        -> Matches the closing tag corresponding to the captured group 1.
        #
        # The re.DOTALL flag allows '.' to match newlines, which is crucial.
        modified_content = re.sub(
            r"<(h[1-6]|p).*?>.*?</\1>",
            _remove_newlines_in_tag_content,
            original_content,
            flags=re.DOTALL | re.IGNORECASE,
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
        description="Remove newline characters within <p> and <h1>-<h6> tags."
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
