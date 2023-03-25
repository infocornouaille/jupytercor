import base64
from PIL import Image
from io import BytesIO


def extract_image_64(base64_string: str, nom_fichier: str) -> None:
    """Extract an image from a base64 string and save it to a file

    Args:
        base64_string (str): The base64 string
        nom_fichier (str): The name of the file to save the image to

        Returns:
            None"""
    # Remove the prefix and get only the base64 data
    base64_data = base64_string.split(",")[-1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Create an image object from the bytes
    image = Image.open(BytesIO(image_bytes))
    # Save the image to a file
    image.save(f"images/{nom_fichier}")


def extract_attachemnt_image(
    base64_data: str, nom_fichier: str, total_images: int
) -> None:
    """Extract an image from a base64 string and save it to a file

    Args:
        base64_data (str): The base64 string
        nom_fichier (str): The name of the file to save the image to
        total_images (int): The number of images

        Returns:
            None"""
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Create an image object from the bytes
    image = Image.open(BytesIO(image_bytes))
    # Save the image to a file
    image.save(f"images/{total_images}-{nom_fichier}")
