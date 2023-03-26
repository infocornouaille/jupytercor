import base64
import os
import re
import shutil

import markdown
import requests
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from PIL import Image
from slugify import slugify

from jupytercor.extract64 import *
from jupytercor.utils import *

# Expression régulière pour remplacer les liens vers les images
pattern_https = r"\((https?://.+)\)"
pattern64 = r"!\[.*?\]\(data:image\/.*?;base64,.+?\)"
regex_64 = re.compile("!\[(.*?)\]\((.+?)\)")


# Créer une classe qui hérite de Treeprocessor et qui extrait les URL des images
class ImgExtractor(Treeprocessor):
    def __init__(self, md):
        # Utiliser self.markdown pour stocker l'instance du module markdown passée en paramètre
        self.markdown = md

    def run(self, doc):
        self.markdown.images = []
        self.markdown.blocks = []
        for image in doc.findall(".//img"):
            self.markdown.images.append(image.get("src"))
            self.markdown.blocks.append(image)


# Créer une classe qui hérite de Extension et qui utilise la classe précédente
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
                # Open a file in images folder with same name as image
                with open(os.path.join("images", filename), "wb") as f:
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
    path = os.path.join("images", filename)
    # Return the relative path between parentheses instead of the URL
    return f"({path})"


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
            nom_fichier = match.group(1)
            name, ext = os.path.splitext(nom_fichier)
            nom_fichier = slugify(name) + ext
            contenu = match.group(2)
            extract_image_64(contenu, nom_fichier)
            sortie = string.replace(contenu, f"images/{nom_fichier}")
            return sortie
    return string


def process_attachemnts(cell, total_images):
    for key, value in cell["attachments"].items():
        if key in cell.source:
            print(key, "dans la source")
            for cle, valeur in value.items():
                extract_attachemnt_image(valeur, key, total_images)
                temp = cell.source
                temp = temp.replace(
                    f"attachment:{key}", "images/" + str(total_images) + "-" + key
                )
                cell.source = temp
    del cell["attachments"]

    return cell


def process_images(nb):
    """Process all images from a notebook

    Args:
        nb 'notebook': original notebook
    """
    total_images = 0
    if os.path.exists("images"):
        print("Le répertoire images existe déjà.")
    else:
        # Créer le répertoire
        try:
            os.mkdir("images")
        except OSError as e:
            # Gérer les éventuelles erreurs
            print(
                "Une erreur est survenue lors de la création du répertoire : 'images'"
            )
            return None

    # Loop through the cells and download images in images folder
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # if "[attachment:" in cell.source:
            if "attachments" in cell:
                total_images += 1
                process_attachemnts(cell, total_images)
            cell.source = test_base64(cell.source)
            download_image(cell.source.encode())
            # Appliquer la fonction replace_url sur toutes les occurrences du motif dans le texte avec re.sub
            result = re.sub(pattern_https, replace_url, cell.source)
            cell.source = result

    return nb
