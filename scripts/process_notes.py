"""Replaces inline reference markers with content from source paragraphs.

This script processes text files to find reference markers like [[1]], [[2]],
etc. It distinguishes between "source" markers (at the beginning of a line)
and "target" markers (inline).

Each target marker is replaced by the content of its corresponding source
paragraph, formatted as the literal string '\\nauthor{content}'. The original
source paragraphs are then removed from the file.

Example:
    To process all .md files in the 'notes' directory:
        $ python replace_refs.py "notes/*.md"
"""

import argparse
import glob
import os
import re


def process_file(file_path):
    """
    Reads a file, performs the marker replacement, and writes back the result.

    Args:
        file_path (str): The path to the file to process.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Step 1: Find all source paragraphs and store them in a dictionary.
        source_regex = re.compile(r"^\[\[(\d+)\]\](.*)", re.MULTILINE)
        sources = {
            match.group(1): match.group(2).strip()
            for match in source_regex.finditer(content)
        }

        if not sources:
            print(f'Info: No source markers found in "{file_path}". Skipping.')
            return

        # Step 2: Define a replacer function for all markers.
        def replacer(match):
            """Replaces a marker based on its position."""
            marker_num = match.group(1)
            start_index = match.start()

            is_source_marker = start_index == 0 or content[start_index - 1] == "\n"

            if is_source_marker:
                return match.group(0)
            else:
                if marker_num in sources:
                    replacement_text = sources[marker_num]
                    # CORRECTED LINE:
                    # Use '\\n' to produce a literal backslash-n string,
                    # not a newline character.
                    return f"\\nauthor{{{replacement_text}}}"
                else:
                    print(
                        f'Warning in "{file_path}": '
                        f"Target [[{marker_num}]] has no matching source."
                    )
                    return match.group(0)

        # Step 3: Run the replacer on all markers found in the content.
        all_markers_regex = re.compile(r"\[\[(\d+)\]\]")
        content = all_markers_regex.sub(replacer, content)

        # Step 4: Remove all original source lines from the content.
        removal_regex = re.compile(r"^\[\[\d+\]\].*?(\r\n?|\n|$)", re.MULTILINE)
        final_content = removal_regex.sub("", content)

        # Step 5: Write the modified content back to the file if it changed.
        if final_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            print(f"Processed: {file_path}")
        else:
            print(f"No changes needed: {file_path}")

    except IOError as e:
        print(f'Error: Could not read or write file "{file_path}". Reason: {e}')
    except Exception as e:
        print(f'An unexpected error occurred while processing "{file_path}": {e}')


def main():
    """Parses command-line arguments and processes the files."""
    parser = argparse.ArgumentParser(
        description=(
            "Replaces inline [[number]] markers with content from "
            "source lines beginning with the same marker."
        )
    )
    parser.add_argument(
        "path_pattern",
        type=str,
        help='Path pattern for the files to process, e.g., "notes/*.md".',
    )

    args = parser.parse_args()

    file_list = glob.glob(args.path_pattern, recursive=True)

    if not file_list:
        print(f'Warning: No files found matching pattern "{args.path_pattern}".')
        return

    print(f"Found {len(file_list)} files. Starting processing...")

    for file_path in file_list:
        if os.path.isfile(file_path):
            process_file(file_path)

    print("\nAll files have been processed.")


if __name__ == "__main__":
    main()
