# PREREQUISITE - IF ON MAC - pip install fastapi pydantic requests PyPDF2 pytesseract Pillow fitz

# IF ON WINDOWS - pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import Union
import requests
import PyPDF2
from io import BytesIO
from PIL import Image
import pytesseract
import fitz  # this is PyMuPDF for image-based PDF handling

app = FastAPI()

class InputData(BaseModel):
    url: Union[str, None] = None
    text: Union[str, None] = None

async def extract_text_from_pdf(file):
    """Extracts text from PDF using PyPDF2 or OCR if necessary."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        content = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        if not content.strip():  # No text found, using OCR
            content = await extract_text_with_ocr(file)
        return content
    except Exception as e:
        return str(e)

async def extract_text_with_ocr(file):
    """Extracts text from image-based PDFs using OCR."""
    content = ""
    pdf_document = fitz.open("pdf", file.read())
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()  # Renders page to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        content += text
    return content

@app.post("/process_input/")
async def process_input(file: Union[UploadFile, None] = None, data: InputData = None):
    content = ""
    
    # Process PDF or text file
    if file:
        if file.filename.endswith(".pdf"):
            content = await extract_text_from_pdf(file.file)
        elif file.filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8")
    
    # Process URL
    elif data and data.url:
        response = requests.get(data.url)
        if response.headers["Content-Type"] == "application/pdf":
            content = await extract_text_from_pdf(BytesIO(response.content))
        else:
            content = response.text
    
    # Process plain text
    elif data and data.text:
        content = data.text
    
    return {"extracted_content": content}

# PyMuPDF (fitz) to open and read each page of the PDF as an image.
# PIL (Pillow) and Tesseract OCR (pytesseract) used to convert the image to text, 
# for scanned PDFs.
# we must first attempt to use PyPDF2 for extracting embedded text.
# fallback - if no text - is extract_text_with_ocr - so we can do OCR extraction
# in general, we handle uploads and URLs pointing to text-based / image-based pdfs


