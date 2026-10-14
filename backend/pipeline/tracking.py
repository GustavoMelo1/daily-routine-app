import hashlib

def calculate_image_hash(image_path):
    with open(image_path, "rb") as image_file:
        return hashlib.file_digest(image_file, "sha256").hexdigest()
