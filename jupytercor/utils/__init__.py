import subprocess
from urllib.parse import urlparse

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


def clean_markdown(nb: nbformat) -> nbformat:
    """Clean the markdown cells with pandoc conversions
    Read the input notebook and convert all markdown cells into a clean markdown without html tags.

    Args:
        nb (nbformat): The notebook to clean

        Returns:
            nbformat: The cleaned notebook"""
    # Loop through the cells and transform markdown cells with pandoc if clean is True
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # Run a pandoc command to convert markdown to html
            html = subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "html", "-o", "-"],
                input=cell.source.encode(),
                capture_output=True,
            )

            # Check for pandoc errors
            if html.returncode != 0:
                raise ValueError(
                    f"Pandoc failed to convert markdown to html with the following error: {html.stderr.decode()}"
                )

            # Run a pandoc command to convert html to markdown
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

            # Replace the cell source with the transformed text
            cell.source = result.stdout.decode()

    return nb
