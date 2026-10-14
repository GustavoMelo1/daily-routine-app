import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from requests.exceptions import RequestException
from pipeline.ocr import extract
from pipeline import import_client
from pipeline.payloads import build_import_payload
from pipeline.tracking import calculate_image_hash

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
    return sorted(image_files)


def process_image(image_path):
    image_hash = calculate_image_hash(image_path)
    record = import_client.get_or_create_import(image_hash)
    import_id = record["id"]
    if record["status"] == "completed":
        return "already_completed"
    if record["status"] in ("failed", "processing"):
        try:
            import_client.retry_import(import_id)
        except RequestException as error:
            if record["status"] == "processing" and error.response is not None and error.response.status_code == 409:
                return "busy"
            raise
    token = import_client.start_import(import_id)
    try:
        payload = import_client.get_payload(import_id)
        if payload is None:
            payload = build_import_payload(extract(str(image_path)))
            if calculate_image_hash(image_path) != image_hash:
                raise ValueError("Imagem alterada durante o OCR; execute novamente")
            import_client.save_payload(import_id, token, payload)
        import_client.publish_import(import_id, token, payload)
        return "completed"
    except Exception as error:
        # A response can be lost after the API has already committed successfully.
        try:
            if import_client.get_or_create_import(image_hash)["status"] == "completed":
                return "completed"
            import_client.fail_import(import_id, token, str(error))
        except RequestException:
            logger.warning("Não foi possível registrar a falha da importação %s; ela poderá ser recuperada após uma hora", import_id)
        raise

def process_folder(folder_path):
    logger.info("Iniciando processamento de pasta: %s", folder_path)
    image_files = find_image_files(folder_path)
    if not image_files:
        logger.info("Nenhuma imagem encontrada em: %s", folder_path)
        return []
    import_client.check_import_api()
    failures = []
    for image_path in image_files:
        logger.info("Processando imagem: %s", image_path)
        try:
            outcome = process_image(image_path)
            logger.info("Resultado da imagem: %s | %s", image_path, outcome)
        except Exception as error:
            logger.exception("Falha ao processar imagem: %s", image_path)
            failures.append({"image_path": str(image_path),"error": str(error),})
    return failures
def main(argv=None):
    backend = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Importar imagens com controle de repetição e retomada")
    parser.add_argument("--folder", type=Path, default=backend / "images")
    parser.add_argument("--log-file", type=Path, default=backend / "logs" / "batch.log")
    args = parser.parse_args(argv)
    try:
        args.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(args.log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                            handlers=[logging.StreamHandler(), file_handler], force=True)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        failures = process_folder(args.folder)
    except (OSError, RequestException, ValueError) as error:
        logger.error("Não foi possível executar o lote: %s", error)
        return 1
    logger.info("Lote encerrado. Imagens com falha: %s", len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
