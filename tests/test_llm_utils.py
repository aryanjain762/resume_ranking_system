from utils.llm_utils import extract_criteria_with_llm
import pytest

def test_extract_criteria_with_llm():
 
    job_description = "Sample job description text."
    criteria = extract_criteria_with_llm(job_description)
    assert isinstance(criteria, list)
    assert len(criteria) > 0
