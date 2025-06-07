#!/usr/bin/env python3
# coding: utf-8

# Standard library
import subprocess
from pathlib import Path
from typing import Optional

# Third-party
import nbformat
import typer

# First-party
from jupytercor.images import process_images
from jupytercor.utils import clean_markdown

# Define base directory and paths for templates and filters using pathlib
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
FILTERS_DIR = BASE_DIR / "filters"

app = typer.Typer(help="Convert markdown cells in a jupyter notebook with pandoc")

def convert_to_latex(input_file_str: str, template_name: str ="cornouaille") -> None:
    """Convert a notebook to latex using pandoc

    Args:
        input_file_str (str): The name of the input notebook file.
        template_name (str): The base name of the template (e.g., "cornouaille").

    Returns:
        None
    """
    input_file_path = Path(input_file_str)
    output_tex_path = input_file_path.with_suffix(".tex")
    template_file_path = TEMPLATES_DIR / (template_name + ".latex")
    panflute_headers_filter_path = FILTERS_DIR / "panflute-headers.py"
    pandoc_ldotcarreaux_filter_path = FILTERS_DIR / "pandoc-ldotcarreaux.py"

    pandoc_cmd = [
        "pandoc",
        str(input_file_path),
        "-t",
        "latex",
        "-o",
        str(output_tex_path),
        "--listing",
        "--filter",
        str(panflute_headers_filter_path),
        "--filter",
        str(pandoc_ldotcarreaux_filter_path),
        "--template",
        str(template_file_path),
    ]

    try:
        tex = subprocess.run(
            pandoc_cmd,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        print("Pandoc not found, please install it.")
    except subprocess.CalledProcessError as e:
        print("Error while running pandoc. Please check your notebook.")
        print(f"Error while running pandoc: {e.stderr.decode() if e.stderr else 'No stderr'}")
        print(f"Command exit code: {e.returncode}")


def convert_to_pdf(input_file_str: str, template_name: str ="cornouaille") -> None:
    """
    Convert a notebook to pdf using pandoc and xelatex
    Args:
        input_file_str (str): The name of the input notebook file.
        template_name (str): The base name of the template (e.g., "cornouaille").

    Returns:
        None"""
    input_file_path = Path(input_file_str)
    output_tex_path = input_file_path.with_suffix(".tex")
    output_pdf_path = input_file_path.with_suffix(".pdf") # For xelatex output reference
    template_file_path = TEMPLATES_DIR / (template_name + ".latex")
    panflute_headers_filter_path = FILTERS_DIR / "panflute-headers.py"
    pandoc_ldotcarreaux_filter_path = FILTERS_DIR / "pandoc-ldotcarreaux.py"

    extra = []
    if template_name == "cornouaille":
        extra = [
            "--listing",
            "--filter",
            str(panflute_headers_filter_path),
            "--filter",
            str(pandoc_ldotcarreaux_filter_path),
        ]

    pandoc_cmd_list = [
        "pandoc",
        str(input_file_path),
        "-t",
        "latex",
        "-o",
        str(output_tex_path),
        "--template",
        str(template_file_path),
    ] + extra

    try:
        tex = subprocess.run(
            pandoc_cmd_list,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        print("Pandoc not found, please install it.")
        return
    except subprocess.CalledProcessError as e:
        print("Error while running pandoc to generate .tex file.")
        print(f"Pandoc stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
        print(f"Command exit code: {e.returncode}")
        return

    try:
        print(f"Running xelatex on {str(output_tex_path)}...")
        xelatex_result = subprocess.run(
            ["xelatex", str(output_tex_path)],
            capture_output=True,
            check=True,
            text=True
        )
        print(f"xelatex completed successfully. Output written to {str(output_pdf_path)}")
        if xelatex_result.stdout and xelatex_result.stdout.strip():
            print("xelatex stdout:")
            print(xelatex_result.stdout)
    except FileNotFoundError:
        print("Error: xelatex command not found. Please ensure LaTeX is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during xelatex execution on {str(output_tex_path)}:")
        print(f"xelatex exited with status {e.returncode}")
        if e.stdout and e.stdout.strip():
            print("xelatex stdout:")
            print(e.stdout)
        if e.stderr and e.stderr.strip():
            print("xelatex stderr:")
            print(e.stderr)
        print(f"Failed to convert {str(output_tex_path)} to PDF.")

@app.command()
def jupytercor_cli(
    input_file: Path = typer.Argument(..., help="The name of the input notebook file", exists=True, file_okay=True, dir_okay=False, readable=True),
    output_file: Optional[Path] = typer.Option(None, "--output-file", "-o", help="The name of the output notebook file", file_okay=True, dir_okay=False, writable=True),
    to: str = typer.Option("pdf", "--to", help="The name of the output format (default: pdf)"),
    template: str = typer.Option("cornouaille", "--template", help="Template: cornouaille or eisvogel (default: cornouaille)"),
    clean: bool = typer.Option(False, "--clean", help="Clean the markdown cells with pandoc conversions", is_flag=True),
    images: bool = typer.Option(False, "--images", help="Download images into 'images' folder and update links", is_flag=True),
    debug: bool = typer.Option(False, "--debug", help="Debug mode", is_flag=True),
):
    """
    Main CLI logic for jupytercor.
    Processes a Jupyter notebook: optionally downloads images, cleans markdown,
    and converts the notebook to specified formats like PDF or LaTeX.
    """
    print("Hello from jupytercor !")

    # Define paths for templates and filters based on global constants
    # These might be used by conversion functions or other utilities
    # templates_path and filters_path are already Path objects from global scope.
    # No need to redefine them here unless for local shadowing, which is not the case.

    if debug:
        print("Debug mode")
        print(f"Templates path: {str(TEMPLATES_DIR)}") # Use global Path object
        print(f"Filters path: {str(FILTERS_DIR)}")   # Use global Path object
        return

    nb = None
    notebook_modified = False

    # Load the notebook into memory if image processing (--images) or markdown cleaning (--clean) is requested,
    # or if the target conversion format is PDF or LaTeX and the input is a .ipynb file.
    if images or clean or (to in ["pdf", "latex"] and input_file.suffix == ".ipynb"):
        try:
            # nbformat.read can take a file path string or a file-like object.
            # Path.open() returns a file-like object.
            with input_file.open("r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"Error reading notebook file {str(input_file)}: {e}")
            return

    if images:
        if nb is None and input_file.suffix == ".ipynb":
            print("Error: Notebook could not be loaded for image processing.")
            return
        elif nb:
            print("Processing images...")
            nb = process_images(nb)
            notebook_modified = True
            print("Image processing successful!")
        else:
            print("Skipping image processing as input is not a recognized notebook or already processed.")

    if clean:
        if nb is None and input_file.suffix == ".ipynb":
            print("Error: Notebook could not be loaded for cleaning.")
            return
        elif nb:
            print("Cleaning markdown cells...")
            nb = clean_markdown(nb)
            notebook_modified = True
            print("Markdown cleaning successful!")
        else:
            print("Skipping markdown cleaning as input is not a recognized notebook or already processed.")

    # Save the notebook if it has been modified by the --images or --clean flags.
    if notebook_modified:
        target_save_path: Path = output_file if output_file else input_file
        if not to:
            print(f"Saving modified notebook to {str(target_save_path)}...")
            try:
                with target_save_path.open("w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                print("Notebook saved successfully!")
            except Exception as e:
                print(f"Error writing notebook file {str(target_save_path)}: {e}")
                return
        elif output_file:
             print(f"Saving processed notebook to {str(output_file)} before conversion...")
             try:
                with output_file.open("w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                print(f"Processed notebook saved to {str(output_file)}")
             except Exception as e:
                print(f"Error writing notebook file {str(output_file)}: {e}")
                return

    # This section handles the final conversion to the format specified by --to (e.g., PDF, LaTeX).
    if to:
        input_for_conversion_path: Path = input_file
        if notebook_modified:
            if output_file and nb:
                input_for_conversion_path = output_file
            # If no output_file, input_file was (or should have been) overwritten if modified.

        # Convert functions expect string paths
        input_for_conversion_str = str(input_for_conversion_path)
        print(f"Converting {input_for_conversion_str} to {to} with template {template}...")
        if to == "pdf":
            convert_to_pdf(input_for_conversion_str, template)
        elif to == "latex":
            convert_to_latex(input_for_conversion_str, template)
        else:
            print(f"Unsupported output format: {to}")

    print(f"Processing complete for input file: {str(input_file)}")
    if output_file:
        print(f"Output file (if any): {str(output_file)}")


if __name__ == "__main__":
    app()
