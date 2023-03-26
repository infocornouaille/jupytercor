import subprocess
from urllib.parse import urlparse
import os

import nbformat


def is_valid_url(url: str) -> bool:
    """Check if the url is valid
    Args:
        url (str): The url to check

        Returns:
            bool: True if the url is valid, False otherwise"""
    try:
        result = urlparse(url)
        # Check if the scheme is http or https
        return result.scheme in ("http", "https")
    except:
        return False


def clean_markdown(nb: nbformat, templates_path, filters_path) -> nbformat:
    """Clean the markdown cells with pandoc conversions
    Read the input notebook and convert all markdown cells into a clean markdown without html tags.

    Args:
        nb (nbformat): The notebook to clean

        Returns:
            nbformat: The cleaned notebook"""
    # Loop through the cells and transform markdown cells with pandoc if clean is True
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # pre process the markdown
            cell.source = cell.source.replace("\\$", "xdollarx")
            # Replace the list items with a dash instead of a star
            if "\n* " in cell.source:
                cell.source = cell.source.replace("\n* ", "\n\n- ")
            # Run a pandoc command to convert markdown to html with a custom filter
            html = subprocess.run(
                [
                    "pandoc",
                    "-f",
                    "markdown",
                    "-t",
                    "html",
                    "-o",
                    "-",
                    "--filter",
                    os.path.join(filters_path, "panflute-breakline.py"),
                ],
                input=cell.source.encode(encoding="utf-8"),
                capture_output=True,
            )

            # Check for pandoc errors
            if html.returncode != 0:
                raise ValueError(
                    f"Pandoc failed to convert markdown to html with the following error: {html.stderr.decode()}"
                )
            
            

            # Run a pandoc command to convert html to markdown with a custom filter
            result = subprocess.run(
                ["pandoc", "-f", "html", "-t", "gfm-raw_html", "-o", "-"],
                input=html.stdout,
                capture_output=True,
            )

            # Check for pandoc errors
            if result.returncode != 0:
                raise ValueError(
                    f"Pandoc failed to convert html to markdown with the following error: {result.stderr.decode()}"
                )

            # post process the markdown
            result = result.stdout.decode(encoding="utf-8")
            result = result.replace("\\$", "$")
            result = result.replace("xdollarx", "\\$")

            # Replace the cell source with the transformed text

            cell.source = result

    return nb
