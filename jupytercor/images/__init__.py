import base64
import re
import shutil
from pathlib import Path

import markdown
import requests
from PIL import Image # PIL.Image.open can handle Path objects
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from slugify import slugify

from jupytercor.extract64 import extract_image_64, extract_attachemnt_image
from jupytercor.utils import is_valid_url

# Define the directory for storing images
IMAGES_DIR = Path("images")

# Regular expression to replace image links
pattern_https = r"\((https?://.+)\)"
pattern64 = r"!\[.*?\]\(data:image\/.*?;base64,.+?\)"
regex_64 = re.compile("!\[(.*?)\]\((.+?)\)")


# A Treeprocessor subclass that extracts image URLs.
class ImgExtractor(Treeprocessor):
    def __init__(self, md):
        # Store the markdown instance.
        self.markdown = md

    def run(self, doc):
        self.markdown.images = []
        self.markdown.blocks = []
        for image in doc.findall(".//img"):
            self.markdown.images.append(image.get("src"))
            self.markdown.blocks.append(image)


# An Extension subclass that uses the ImgExtractor.
class ImgExtension(Extension):
    def extendMarkdown(self, md):
        img_ext = ImgExtractor(md)
        md.treeprocessors.register(img_ext, "img_ext", 15)


def download_image(cell: str) -> None:
    """Download images from markdown cell and save them in images folder

    Args:
        cell (str): Markdown cell

    Returns:
        None
    """

    md = markdown.Markdown(extensions=[ImgExtension()])
    # Convert markdown cell to extract image urls in md.images
    md.convert(cell)
    # Iterate over image urls and download them with requests

    for url in md.images:
        if is_valid_url(url):
            # Get filename from url (after last /)
            filename = url.split("/")[-1]
            print(f"Downloading {filename}")
            # Send a GET request to the url and check the response status (200 = OK)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # Ensure images directory exists
                IMAGES_DIR.mkdir(parents=True, exist_ok=True)
                # Open a file in images folder with same name as image
                image_path = IMAGES_DIR / filename
                with image_path.open("wb") as f:
                    # Copy response content to file with shutil
                    shutil.copyfileobj(response.raw, f)
            else:
                print(f"Error downloading image {filename}")


def replace_url(match) -> str:
    """Replace the URL in the markdown cell with the relative path to the downloaded image

    Args:
        match (re.Match[str]): match object from re.match()

    Returns:
        str: relative path to the downloaded image
    """
    # Get the URL captured by group 1 of the regular expression
    url = match.group(1)
    # Get the image filename from the URL (after the last /)
    filename = url.split("/")[-1]
    # Build the relative path to the downloaded image in the images folder
    path = IMAGES_DIR / filename
    # Return the relative path between parentheses instead of the URL
    return f"({str(path)})"


def test_base64(string: str) -> str:
    """Test if string is base64 encoded

    Args:
        string (str): string to test

        Returns:
            str: string if not base64 encoded, else base64 decoded string"""
    # Use re.match() to check if the string matches the pattern
    match = re.match(pattern64, string)
    if match:
        match = regex_64.search(string)
        if match:
            nom_fichier_orig = match.group(1)
            original_path = Path(nom_fichier_orig)
            name = original_path.stem
            ext = original_path.suffix
            nom_fichier_slug = slugify(name) + ext
            contenu = match.group(2)
            extract_image_64(contenu, nom_fichier_slug, IMAGES_DIR)
            sortie = string.replace(contenu, str(IMAGES_DIR / nom_fichier_slug))
            return sortie
    return string


def process_attachemnts(cell, total_images):
    for key_filename, value_mimetypes in cell["attachments"].items():
        if key_filename in cell.source:
            print(f"Processing attachment: {key_filename} in source")
            for _mimetype, base64_data in value_mimetypes.items(): # _mimetype (e.g., image/png) is not used for filename
                # It's better to slugify or sanitize key_filename before using it as a filename part
                # For now, using original key_filename as per existing logic for file naming.
                extract_attachemnt_image(base64_data, key_filename, total_images, IMAGES_DIR)
                temp_source = cell.source
                # Construct the new path using IMAGES_DIR
                new_image_path = IMAGES_DIR / f"{total_images}-{key_filename}"
                temp_source = temp_source.replace(
                    f"attachment:{key_filename}", str(new_image_path)
                )
                cell.source = temp_source
    del cell["attachments"]

    return cell


def process_images(nb):
    """Process all images from a notebook

    Args:
        nb 'notebook': original notebook
    """
    total_images = 0
    # Create images directory if it doesn't exist (using Path object)
    try:
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory '{IMAGES_DIR}': {e}")
        return None # Or handle error as appropriate

    # Loop through the cells to process images in markdown cells.
    # The order of operations for each markdown cell is:
    # 1. Process attachments (if any) using `process_attachemnts`.
    # 2. Process embedded base64 images using `test_base64`.
    # 3. Download remote images using `download_image` and update links.
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            if "attachments" in cell:
                total_images += 1
                process_attachemnts(cell, total_images)
            cell.source = test_base64(cell.source)
            # Call download_image with string cell.source, not bytes
            download_image(cell.source)
            # Apply the replace_url function to all occurrences of the pattern in the text with re.sub
            result = re.sub(pattern_https, replace_url, cell.source)
            cell.source = result

    return nb
