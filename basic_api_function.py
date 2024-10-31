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
