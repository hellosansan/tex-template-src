"""Cleans up files by removing blank lines and then adding new ones.

This script processes text files in two stages:
1. It removes all existing blank lines (lines that are empty or contain only
   whitespace).
2. It then inserts a new blank line after every single line of the
   remaining content.

The files are modified in-place.

Example:
    To process all .txt files in the 'data' directory:
        $ python format_lines.py "data/*.txt"
"""

import argparse
import glob
import os


def process_file(file_path):
    """
    Reads a file, removes all blank lines, then adds a blank line
    after every line, and writes the result back to the file.

    Args:
        file_path (str): The path to the file to process.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Step 1: Remove all blank lines.
        non_blank_lines = [line for line in lines if line.strip()]

        if not non_blank_lines:
            if lines:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")
                print(f"Processed (cleared): {file_path}")
            else:
                print(f"No changes needed (already empty): {file_path}")
            return

        # Step 2: Add a blank line after EVERY line.
        result_lines = []
        for i, line in enumerate(non_blank_lines):
            # Append the current content line.
            result_lines.append(line)
            # Add a blank line after it, unless it's the very last line.
            is_not_last_line = (i + 1) < len(non_blank_lines)
            if is_not_last_line:
                result_lines.append("\n")

        final_content = "".join(result_lines)
        original_content = "".join(lines)

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
            "Removes all blank lines from files, then adds one "
            "blank line after every line."
        )
    )
    parser.add_argument(
        "path_pattern",
        type=str,
        help='Path pattern for the files to process, e.g., "data/*.txt".',
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
