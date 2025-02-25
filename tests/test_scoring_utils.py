from utils.scoring_utils import process_single_resume
import pytest

def test_process_single_resume():
  
    with open("test_resume.pdf", "rb") as file:
        criteria = ["Python", "Machine Learning"]
        result = process_single_resume(file, criteria)
        assert isinstance(result, dict)
        assert "candidate_name" in result
        assert "total_score" in result
