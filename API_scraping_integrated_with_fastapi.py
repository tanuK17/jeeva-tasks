# For API scraping, we can integrate it directly into the FastAPI function, 
#so we get retrieval of data from APIs alongside file, URL,  text inputs.

import requests
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from typing import Union
from io import BytesIO
import PyPDF2
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

app = FastAPI()

class InputData(BaseModel):
    url: Union[str, None] = None
    text: Union[str, None] = None
    api_url: Union[str, None] = None  # Added API URL field

async def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        content = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        if not content.strip():
            content = await extract_text_with_ocr(file)
        return content
    except Exception as e:
        return str(e)

async def extract_text_with_ocr(file):
    content = ""
    pdf_document = fitz.open("pdf", file.read())
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
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
    
    # Process API scraping
    elif data and data.api_url:
        response = requests.get(data.api_url)
        if response.status_code == 200:
            content = response.json()  # IF NON JSON THEN response.text 
        else:
            content = f"Error: {response.status_code} - {response.reason}"
    
    # Process plain text
    elif data and data.text:
        content = data.text
    
    return {"extracted_content": content}

