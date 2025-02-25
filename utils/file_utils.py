import logging
from fastapi import UploadFile
import io
import PyPDF2
from docx import Document

async def extract_text_from_file(file: UploadFile) -> str:
    logging.info(f"Extracting text from {file.filename}")
    content = await file.read()
    file_extension = Path(file.filename).suffix.lower()
    text = ""
    
    try:
        if file_extension == '.pdf':
            logging.info(f"Processing as PDF: {file.filename}")
            with io.BytesIO(content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        
        elif file_extension in ['.docx', '.doc']:
            logging.info(f"Processing as DOCX: {file.filename}")
            with io.BytesIO(content) as docx_file:
                doc = Document(docx_file)
                paragraphs = [p.text for p in doc.paragraphs]
                text = '\n'.join(paragraphs)
        
        else:
            logging.info(f"Processing as plain text: {file.filename}")
            text = content.decode('utf-8')
        
        logging.info(f"Extracted {len(text)} characters from {file.filename}")
        logging.info(f"First 100 chars: {text[:100]}")
        
        if not text.strip():
            logging.warning(f"Warning: No text extracted from {file.filename}")
            
    except Exception as e:
        logging.error(f"Error extracting text from file {file.filename}: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Error extracting text from file: {str(e)}")
    
    return text