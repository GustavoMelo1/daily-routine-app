from PIL import Image

import os
import genai
import pytesseract

os.getenv("GEMINI_API_KEY")

config='--psm 6'
lang='por'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

resultado = pytesseract.image_to_string(Image.open('exemplo.jpeg'), lang=lang, config=config)
print(resultado)