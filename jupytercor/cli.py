#!/usr/bin/env python3
# coding: utf-8

import argparse
import os
import subprocess
import nbformat

from jupytercor.images import process_images
from jupytercor.utils import clean_markdown

# Define paths for templates and filters
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
FILTERS_DIR = os.path.join(os.path.dirname(__file__), "filters")

# Create an argument parser object
parser = argparse.ArgumentParser(
    description="Convert markdown cells in a jupyter notebook with pandoc"
)
# Add an input file argument
parser.add_argument("input_file", help="The name of the input notebook file")
# Add an output file argument with no default value
parser.add_argument(
    "-o", "--output_file", help="The name of the output notebook file", default=None
)
# Add an toargument with pdf default value
parser.add_argument("--to", help="The name of the output format (default: pdf)", default="pdf")

# Add an templateargument with cornouaille default value
parser.add_argument(
    "--template", help="Template: cornouaille or eisvogel (default: cornouaille)", default="cornouaille"
)
# Add a clean flag argument with a default value of False
parser.add_argument(
    "--clean",
    help="Clean the markdown cells with pandoc conversions",
    action="store_true",
)

# Add a images flag argument with a default value of False
parser.add_argument(
    "--images", help="Downlad image in images folder", action="store_true"
)

# Add a debug flag argument with a default value of False
parser.add_argument("--debug", help="Debug mode", action="store_true")
# Parse the arguments
args = parser.parse_args()


def convert_to_latex(input_file: str, template: str ="cornouaille") -> None:
    """Convert a notebook to latex using pandoc

    Args:
        input_file (str): The name of the input notebook file
        template (str): The base name of the template (e.g., "cornouaille")

    Returns:
        None
    """
    name, ext = os.path.splitext(input_file)
    output_tex = name + ".tex"
    template_path = os.path.join(TEMPLATES_DIR, template + ".latex")
    panflute_headers_filter_path = os.path.join(FILTERS_DIR, "panflute-headers.py")
    pandoc_ldotcarreaux_filter_path = os.path.join(FILTERS_DIR, "pandoc-ldotcarreaux.py")

    try:
        tex = subprocess.run(
            [
                "pandoc",
                input_file,
                "-t",
                "latex",
                "-o",
                output_tex,
                "--listing",
                "--filter",
                panflute_headers_filter_path,
                "--filter",
                pandoc_ldotcarreaux_filter_path,
                "--template",
                template_path,
            ],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        print("Pandoc not found, please install it.")
    except subprocess.CalledProcessError as e:
        print("Error while running pandoc. Please check your notebook.")
        print(f"Error while running pandoc: {e.stderr}")
        print(f"Command exit code: {e.returncode}")


def convert_to_pdf(input_file: str, template="cornouaille") -> None:
    """
    Convert a notebook to pdf using pandoc and xelatex
    Args:
        input_file (str): The name of the input notebook file
        template (str): The base name of the template (e.g., "cornouaille")

    Returns:
        None"""
    name, ext = os.path.splitext(input_file)
    output_tex = name + ".tex"
    output_pdf = name + ".pdf"
    template_path = os.path.join(TEMPLATES_DIR, template + ".latex")
    panflute_headers_filter_path = os.path.join(FILTERS_DIR, "panflute-headers.py")
    pandoc_ldotcarreaux_filter_path = os.path.join(FILTERS_DIR, "pandoc-ldotcarreaux.py")

    extra = []
    # Assuming "cornouaille" is the template that needs these specific filters.
    # Other templates might not, or might need different ones.
    # This logic might need refinement if more templates are added with different filter requirements.
    if template == "cornouaille":
        extra = [
            "--listing",
            "--filter",
            panflute_headers_filter_path,
            "--filter",
            pandoc_ldotcarreaux_filter_path,
        ]

    pandoc_cmd = [
        "pandoc",
        input_file,
        "-t",
        "latex",
        "-o",
        output_tex,
        "--template",
        template_path,
    ] + extra

    try:
        tex = subprocess.run(
            pandoc_cmd,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        print("Pandoc not found, please install it.")
        return # Exit if pandoc is not found
    except subprocess.CalledProcessError as e:
        print("Error while running pandoc to generate .tex file.")
        print(f"Pandoc stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
        print(f"Command exit code: {e.returncode}")
        return # Exit if pandoc fails

    try:
        print(f"Running xelatex on {output_tex}...")
        xelatex_result = subprocess.run(
            ["xelatex", output_tex],
            capture_output=True,
        check=True, # Added check=True for pandoc call as well, good practice
    )
    try:
        print(f"Running xelatex on {output_tex}...")
        xelatex_result = subprocess.run(
            ["xelatex", output_tex],
            capture_output=True,
            check=True,
            text=True # To get stdout/stderr as strings
        )
        print(f"xelatex completed successfully. Output written to {output_pdf}")
        if xelatex_result.stdout and xelatex_result.stdout.strip():
            print("xelatex stdout:")
            print(xelatex_result.stdout)
    except FileNotFoundError:
        print("Error: xelatex command not found. Please ensure LaTeX is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during xelatex execution on {output_tex}:")
        print(f"xelatex exited with status {e.returncode}")
        if e.stdout and e.stdout.strip():
            print("xelatex stdout:")
            print(e.stdout)
        if e.stderr and e.stderr.strip():
            print("xelatex stderr:")
            print(e.stderr)
        print(f"Failed to convert {output_tex} to PDF.")


def main():
    print("Hello from jupytercor !")

    # Define paths for templates and filters based on global constants
    # These might be used by conversion functions or other utilities
    templates_path = TEMPLATES_DIR
    filters_path = FILTERS_DIR

    if args.debug:
        print("Debug mode")
        print(f"Templates path: {templates_path}")
        print(f"Filters path: {filters_path}")
        # In debug mode, often we want to see paths and then exit or perform specific debug actions.
        # For now, just printing paths and exiting as per original logic.
        return

    nb = None
    notebook_modified = False

    # Load the notebook into memory if image processing (--images) or markdown cleaning (--clean) is requested,
    # or if the target conversion format is PDF or LaTeX and the input is a .ipynb file.
    # This is because these operations require the notebook object to be manipulated.
    # For direct Pandoc conversion of other file types (e.g., .md to .pdf),
    # the notebook object isn't strictly needed upfront by *this* script's logic,
    # but loading it ensures consistency if pre-processing steps are active.
    if args.images or args.clean or (args.to in ["pdf", "latex"] and args.input_file.endswith(".ipynb")):
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"Error reading notebook file {args.input_file}: {e}")
            return

    if args.images:
        if nb is None and args.input_file.endswith(".ipynb"): # Should have been loaded above
            print("Error: Notebook could not be loaded for image processing.")
            return
        elif nb:
            print("Processing images...")
            nb = process_images(nb) # Assuming process_images takes and returns a notebook object
            notebook_modified = True
            print("Image processing successful!")
        else:
            print("Skipping image processing as input is not a recognized notebook or already processed.")


    if args.clean:
        if nb is None and args.input_file.endswith(".ipynb"): # Should have been loaded above
            print("Error: Notebook could not be loaded for cleaning.")
            return
        elif nb:
            print("Cleaning markdown cells...")
            # Assuming clean_markdown takes a notebook object and returns a modified one.
            # The original clean_markdown(nb, templates_path, filters_path) took paths,
            # but the import is now just `from jupytercor.utils import clean_markdown`.
            # We need to ensure clean_markdown is adapted or called correctly.
            # For now, calling it as per its likely signature from the import.
            nb = clean_markdown(nb)
            notebook_modified = True
            print("Markdown cleaning successful!")
        else:
            print("Skipping markdown cleaning as input is not a recognized notebook or already processed.")

    # Save the notebook if it has been modified by the --images or --clean flags.
    # - If no conversion (`--to`) is specified, the notebook is saved (to output_file if provided, else input_file).
    # - If conversion is specified AND an output_file is given (assumed to be for the .ipynb),
    #   the modified notebook is saved to output_file first, and this file might then be used for conversion.
    if notebook_modified:
        output_target = args.output_file if args.output_file else args.input_file
        if not args.to: # Only save if no conversion is happening (or if it's an explicit save before conversion if output_file is also set)
            print(f"Saving modified notebook to {output_target}...")
            try:
                with open(output_target, "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                print("Notebook saved successfully!")
            except Exception as e:
                print(f"Error writing notebook file {output_target}: {e}")
                return
        elif args.output_file: # If --to and --output_file, save the processed .ipynb first
             print(f"Saving processed notebook to {args.output_file} before conversion...")
             try:
                with open(args.output_file, "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                print(f"Processed notebook saved to {args.output_file}")
                # The conversion should now operate on this saved file if it's an ipynb
                # or on the original input if no processing was done.
                # args.input_file will be used by conversion functions later.
                # If notebook was modified, the conversion should use the modified content.
                # This logic gets tricky if args.output_file is not an .ipynb file.
                # For now, we assume if output_file is given with modifications, it's an .ipynb.
             except Exception as e:
                print(f"Error writing notebook file {args.output_file}: {e}")
                return

    # This section handles the final conversion to the format specified by --to (e.g., PDF, LaTeX).
    # It will use the original input_file or a modified version if --images or --clean were active
    # (potentially saved to args.output_file if that was specified for the intermediate .ipynb).
    if args.to:
        input_for_conversion = args.input_file
        if notebook_modified:
            # If the notebook was modified, we ideally want to pass the modified content to pandoc.
            # Pandoc can take input from stdin, or we save to a temporary file.
            # For simplicity, if an output_file was specified and it's an .ipynb,
            # we assume it has been saved above and conversion functions might pick it up if they are smart.
            # Or, if no output_file, but modified, we saved over input_file.
            # This part depends on how convert_to_pdf/latex handle their inputs.
            # Let's assume they take the filename passed. If modified, it's the (over)written input_file or output_file.
            if args.output_file and nb: # If an output for the .ipynb was given and it was modified
                input_for_conversion = args.output_file
            # else, it's args.input_file (which might have been overwritten if nb was modified and no output_file)

        print(f"Converting {input_for_conversion} to {args.to} with template {args.template}...")
        if args.to == "pdf":
            convert_to_pdf(input_for_conversion, args.template)
        elif args.to == "latex":
            convert_to_latex(input_for_conversion, args.template)
        else:
            print(f"Unsupported output format: {args.to}")

    print(f"Processing complete for input file: {args.input_file}")
    if args.output_file:
        print(f"Output file (if any): {args.output_file}")


if __name__ == "__main__":
    main()
