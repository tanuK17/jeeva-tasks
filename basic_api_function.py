# File Processing:

# If a PDF file is uploaded, it reads each page using PyPDF2 to extract text
# If a text file is uploaded, it reads and decodes the text

# -------

# URL Handling:

# Fetches the content from the URL
# If the URL points to a PDF, it extracts text similarly to a PDF file
# If it’s plain text or HTML, it retrieves the raw content

# -------

# Directly assigns the provided text to the content

# To test end point:

# Send a PDF or .txt file through the /process_input/ endpoint
# URL or Plain Text: Use JSON with url or text fields

from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import Union
import requests
import PyPDF2
from io import BytesIO

app = FastAPI()

class InputData(BaseModel):
    url: Union[str, None] = None
    text: Union[str, None] = None

@app.post("/process_input/")
async def process_input(file: Union[UploadFile, None] = None, data: InputData = None):
    content = ""
    
    # Process PDF or text file
    if file:
        if file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file.file)
            content = " ".join([page.extract_text() for page in pdf_reader.pages])
        elif file.filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8")
    
    # Process URL
    elif data and data.url:
        response = requests.get(data.url)
        if response.headers["Content-Type"] == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
            content = " ".join([page.extract_text() for page in pdf_reader.pages])
        else:
            content = response.text
    
    # Process plain text
    elif data and data.text:
        content = data.text
    
    return {"extracted_content": content}
