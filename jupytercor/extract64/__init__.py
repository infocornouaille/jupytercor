import base64
from io import BytesIO
from pathlib import Path
from PIL import Image


def extract_image_64(base64_string: str, nom_fichier: str, base_path: Path) -> None:
    """Extract an image from a base64 string and save it to a file

    Args:
        base64_string (str): The base64 string.
        nom_fichier (str): The name of the file to save the image to.
        base_path (Path): The base directory to save the image in.

        Returns:
            None"""
    # Remove the prefix and get only the base64 data
    base64_data = base64_string.split(",")[-1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Create an image object from the bytes
    image = Image.open(BytesIO(image_bytes))
    # Ensure the base path exists
    base_path.mkdir(parents=True, exist_ok=True)
    # Save the image to a file
    image.save(base_path / nom_fichier)


def extract_attachemnt_image(
    base64_data: str, nom_fichier: str, total_images: int, base_path: Path
) -> None:
    """Extract an image from a base64 string and save it to a file

    Args:
        base64_data (str): The base64 string.
        nom_fichier (str): The name of the file to save the image to.
        total_images (int): The number of images, used for prefixing filename.
        base_path (Path): The base directory to save the image in.

        Returns:
            None"""
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Create an image object from the bytes
    image = Image.open(BytesIO(image_bytes))
    # Ensure the base path exists
    base_path.mkdir(parents=True, exist_ok=True)
    # Save the image to a file
    output_filename = f"{total_images}-{nom_fichier}"
    image.save(base_path / output_filename)
