from utils.file_utils import extract_text_from_file
import pytest

def test_extract_text_from_file():
    # Test extracting text from a PDF file
    with open("test_resume.pdf", "rb") as file:
        text = extract_text_from_file(file)
        assert isinstance(text, str)
        assert len(text) > 0
      
