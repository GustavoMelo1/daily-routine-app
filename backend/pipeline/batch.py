from pipeline.ocr import extract
from pipeline.publisher import publish_days
from pathlib import Path

def find_image_files(folder_path):
    folder = Path(folder_path)
    image_extensions = [".jpg", ".jpeg", ".png"]
    image_files = []
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    return image_files

def process_folder(folder_path):
    image_files = find_image_files(folder_path)
    for image_path in image_files:
        result = extract(str(image_path))
        publish_days(result)
if __name__ == "__main__":
    process_folder("images")