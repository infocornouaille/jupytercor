import os
import re
import shutil
import base64
from PIL import Image

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import requests
from slugify import slugify

from jupytercor.extract64 import *


from jupytercor.utils import *

# Expression régulière pour remplacer les liens vers les images
pattern_https = r"\((https?://.+)\)"
# pattern64 = r"!\[.*?\]\(data:image\/.*?;base64,[a-zA-Z0-9+/=]+\)"
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


def download_image(cell):
    """Download images from url in markdown cell"""

    md = markdown.Markdown(extensions=[ImgExtension()])
    # Appliquer la méthode convert pour extraire les URL des images dans la liste md.images
    md.convert(cell)
    # Parcourir la liste des URL des images et les télécharger avec requests

    for url in md.images:
        # print(url)
        # print(url)
        if is_valid_url(url):
            # Récupérer le nom du fichier image à partir de l'URL (après le dernier /)
            filename = url.split("/")[-1]
            print(f"Téléchargement de {filename}")
            # Envoyer une requête GET à l'URL et vérifier le statut de la réponse (200 = OK)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # Ouvrir un fichier dans le dossier images avec le même nom que l'image
                with open(os.path.join("images", filename), "wb") as f:
                    # Copier le contenu de la réponse dans le fichier avec shutil
                    shutil.copyfileobj(response.raw, f)


# Définir une fonction qui remplace chaque URL par le chemin relatif vers l'image téléchargée
def replace_url(match):
    """remplace chaque URL par le chemin relatif vers l'image téléchargée"""
    # Récupérer l'URL capturée par le groupe 1 de l'expression régulière
    url = match.group(1)
    # Récupérer le nom du fichier image à partir de l'URL (après le dernier /)
    filename = url.split("/")[-1]
    # Construire le chemin relatif vers l'image téléchargée dans le dossier images
    path = os.path.join("images", filename)
    # Retourner le chemin relatif entre parenthèses à la place de l'URL
    return f"({path})"


def test_base64(string):
    # Use re.match() to check if the string matches the pattern
    match = re.match(pattern64, string)
    if match:
        #     pass
        #     print("Match found:", match.group())
        # else:
        #     print("No match found")

        match = regex_64.search(string)
        if match:
            nom_fichier = match.group(1)
            name, ext = os.path.splitext(nom_fichier)
            print(name, ext)
            nom_fichier = slugify(name) + ext
            contenu = match.group(2)
            # print("Nom du fichier :", nom_fichier)
            # print("Contenu :", contenu)
            extract_image_64(contenu, nom_fichier)

            sortie = string.replace(contenu, f"images/{nom_fichier}")
            return sortie
    return string


def process_attachemnts(cell, total_images):
    for key, value in cell["attachments"].items():
        if key in cell.source:
            print(key, "dans la source")
            for cle, valeur in value.items():
                # print(valeur[:100])
                # print(type(valeur))
                width = 100
                height = 200
                # png_recovered = base64.b64decode(valeur)
                # img = Image.fromstr('RGBA', (width, height), valeur)
                # Decode the base64 data to bytes
                # imagedata = base64.b64decode(valeur)
                extract_attachemnt_image(valeur, key, total_images)
                temp = cell.source
                truc = "![image.png](attachment:image.png)"
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
