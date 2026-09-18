from pipeline.ocr import extract
from pipeline.publisher import publish_days
from pathlib import Path

def find_image_files(folder_path):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"Pasta de imagens inválida: {folder}")
    image_extensions = [".jpg", ".jpeg", ".png"]
    image_files = []
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    return image_files

def process_folder(folder_path):
    image_files = find_image_files(folder_path)
    if not image_files:
        print(f"Nenhuma imagem encontrada em: {folder_path}")
        return []
    failures = []
    for image_path in image_files:
        try:
            result = extract(str(image_path))
            publish_days(result)
        except Exception as error:
            failures.append({
                "image_path": str(image_path),
                "error": str(error),
            })
    return failures
if __name__ == "__main__":
    try:
        failures = process_folder("images")
    except NotADirectoryError as error:
        raise SystemExit(str(error))
    else:
        for failure in failures:
            print(f"Falha em {failure['image_path']}: {failure['error']}")