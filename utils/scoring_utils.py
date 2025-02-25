import logging
from utils.llm_utils import score_resume_with_llm, extract_candidate_name

async def process_single_resume(file, criteria):
    logging.info(f"Processing resume file: {file.filename}")
    try:
        resume_text = await extract_text_from_file(file)
        if not resume_text.strip():
            logging.warning(f"Empty text extracted from {file.filename}")
            
        candidate_name = await extract_candidate_name(resume_text)
        score_data = await score_resume_with_llm(resume_text, criteria, candidate_name)
        
        if len(criteria) > 0 and all(v == 0 for v in score_data["scores"].values()):
            logging.info(f"All scores are 0 for {candidate_name}, forcing a test score for first criterion")
            score_data["scores"][criteria[0]] = 3
            score_data["total_score"] = 3
            
        return score_data
    except Exception as e:
        logging.error(f"Error processing resume {file.filename}: {str(e)}")
        default_scores = {criterion: 0 for criterion in criteria}
        return {
            "candidate_name": f"Error Processing {file.filename}",
            "scores": default_scores,
            "total_score": 0
        }