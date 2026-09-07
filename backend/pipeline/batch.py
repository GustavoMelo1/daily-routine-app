from pipeline.ocr import extract
from pipeline.publisher import publish_days


if __name__ == "__main__":
    result = extract("exemplo.jpeg")
    publish_days(result)