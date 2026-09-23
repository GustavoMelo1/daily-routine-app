import logging
from pipeline.ocr import extract
from pipeline.publisher import publish_days
from pathlib import Path

logger = logging.getLogger(__name__)

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
    logger.info("Iniciando processamento de pasta: %s", folder_path)
    image_files = find_image_files(folder_path)
    if not image_files:
        logger.info("Nenhuma imagem encontrada em: %s", folder_path)
        return []
    failures = []
    for image_path in image_files:
        logger.info("Processando imagem: %s", image_path)
        try:
            result = extract(str(image_path))
            publish_days(result)
            logger.info("Processamento concluído sem exceção: %s", image_path)
        except Exception as error:
            logger.exception("Falha ao processar imagem: %s", image_path)
            failures.append({"image_path": str(image_path),"error": str(error),})
    return failures
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",)
    try:
        failures = process_folder("images")
    except NotADirectoryError as error:
        raise SystemExit(str(error))
    else:
        logger.info("Lote encerrado. Imagens com falha: %s", len(failures))