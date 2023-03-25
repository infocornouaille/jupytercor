from urllib.parse import urlparse
import subprocess
import nbformat


def is_valid_url(url):
    # Parse l'url en ses composants
    result = urlparse(url)
    # Retourne True si le schéma est http ou https
    return result.scheme in ("http", "https")


def clean_markdown(nb: nbformat):
    """Read the input notebook and convert all markdown cells
    into a clean markdown without html tags"""
    # Loop through the cells and transform markdown cells with pandoc if clean is True

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # Run a pandoc command to convert markdown to html
            html = subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "html", "-o", "-"],
                input=cell.source.encode(),
                capture_output=True,
            )
            result = subprocess.run(
                ["pandoc", "-f", "html", "-t", "gfm-raw_html", "-o", "-"],
                input=html.stdout,
                capture_output=True,
            )
            # Replace the cell source with the transformed text
            cell.source = result.stdout.decode()

    return nb
