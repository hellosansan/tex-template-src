"""Converts Word documents to plain text LaTeX format with image extraction.

This script parses .docx files from a specified directory (default: 'orgs'),
extracts text and images, and generates corresponding .tex files in the
current working directory. Images are saved sequentially to an 'imgs'
directory located in the current working directory, making it a sibling to
the input directory.
"""

import argparse
import logging
import sys
from pathlib import Path

from docx import Document

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def process_document(docx_path: Path, output_dir: Path, imgs_dir: Path) -> None:
    """Converts a single Word document to a .tex file and extracts images.

    Parses paragraphs and runs sequentially. Text is appended as plain text.
    Images contained within runs are extracted, saved as PNGs, and replaced
    with a LaTeX \img{} macro using updated relative paths.

    Args:
        docx_path: The Path object pointing to the input .docx file.
        output_dir: The Path object pointing to the directory for .tex files.
        imgs_dir: The Path object pointing to the sibling directory for images.
    """
    try:
        doc = Document(docx_path)
    except Exception as e:
        logging.error(f"Failed to read {docx_path.name}: {e}")
        return

    tex_content = []
    img_counter = 1

    for para in doc.paragraphs:
        para_text = ""
        for run in para.runs:
            para_text += run.text

            # Locate image elements embedded within the text run
            drawing_elements = run._element.xpath(".//w:drawing")
            for drawing in drawing_elements:
                blip_elements = drawing.xpath(".//a:blip")
                for blip in blip_elements:
                    embed_id = blip.get(
                        "{http://schemas.openxmlformats.org/officeDocument/"
                        "2006/relationships}embed"
                    )

                    if embed_id and embed_id in doc.part.related_parts:
                        image_part = doc.part.related_parts[embed_id]

                        # Define image filename using the document stem
                        img_filename = f"{docx_path.stem}_{img_counter}.png"
                        img_filepath = imgs_dir / img_filename

                        # Write the binary image blob to disk
                        with open(img_filepath, "wb") as img_file:
                            img_file.write(image_part.blob)

                        # Generate the LaTeX image tag (using POSIX path formatting)
                        # Relative path is now 'imgs/filename.png'
                        rel_img_path = Path("imgs") / img_filename
                        para_text += f"\\img{{{rel_img_path.as_posix()}}}"

                        logging.info(f"Extracted image: {img_filename}")
                        img_counter += 1

        if para_text.strip() or drawing_elements:
            tex_content.append(para_text)

    # Write the compiled content to the corresponding .tex file
    tex_filepath = output_dir / f"{docx_path.stem}.tex"
    try:
        with open(tex_filepath, "w", encoding="utf-8") as tex_file:
            tex_file.write("\n\n".join(tex_content))
        logging.info(f"Successfully created: {tex_filepath.name}")
    except IOError as e:
        logging.error(f"Failed to write .tex file for {docx_path.name}: {e}")


def main() -> None:
    """Main execution function for CLI argument parsing and directory setup."""
    parser = argparse.ArgumentParser(
        description="Convert .docx files in a directory to .tex format."
    )
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        default="orgs",
        help="Target directory containing .docx files (default: 'orgs').",
    )
    args = parser.parse_args()

    cwd = Path.cwd()
    input_dir = cwd / args.input_dir

    # Define imgs_dir as a sibling to the target directory (in cwd)
    imgs_dir = cwd / "imgs"

    if not input_dir.exists() or not input_dir.is_dir():
        logging.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    # Ensure the destination image directory exists
    imgs_dir.mkdir(parents=True, exist_ok=True)

    # Filter and process all .docx files in the target directory
    docx_files = list(input_dir.glob("*.docx"))
    if not docx_files:
        logging.warning(f"No .docx files found in directory: {input_dir}")
        sys.exit(0)

    logging.info(f"Found {len(docx_files)} document(s). Processing...")

    for docx_file in docx_files:
        # Ignore temporary/hidden Word files
        if docx_file.name.startswith("~"):
            continue
        process_document(docx_file, cwd, imgs_dir)

    logging.info("Conversion complete.")


if __name__ == "__main__":
    main()
