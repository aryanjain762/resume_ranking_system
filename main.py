from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from utils.file_utils import extract_text_from_file
from utils.llm_utils import extract_criteria_with_llm, score_resume_with_llm, extract_candidate_name
from utils.scoring_utils import process_single_resume
from config import FASTAPI_HOST, FASTAPI_PORT
from logging_utils import setup_logging
import logging
import json
import io
import csv


setup_logging()

app = FastAPI(
    title="Resume Ranking System",
    description="API to extract ranking criteria from job descriptions and score resumes based on those criteria",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-criteria", response_model=dict, tags=["Criteria Extraction"])
async def extract_criteria(file: UploadFile = File(...)):
    """
    Extract key ranking criteria from a job description file (PDF or DOCX).
    """
    job_description_text = await extract_text_from_file(file)
    if not job_description_text.strip():
        raise HTTPException(status_code=422, detail="Empty job description text extracted")
    criteria = await extract_criteria_with_llm(job_description_text)
    return {"criteria": criteria}

@app.post("/score-resumes", tags=["Resume Scoring"])
async def score_resumes(
    criteria: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Score multiple resumes against the provided criteria.
    """
    try:
        criteria_list = json.loads(criteria)
        if not isinstance(criteria_list, list):
            criteria_list = [c.strip() for c in criteria.split(',') if c.strip()]
    except json.JSONDecodeError:
        criteria_list = [c.strip() for c in criteria.split(',') if c.strip()]
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if not criteria_list:
        raise HTTPException(status_code=400, detail="No criteria provided")
    
    scores = []
    for file in files:
        result = await process_single_resume(file, criteria_list)
        scores.append(result)
    
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["Candidate Name"] + criteria_list + ["Total Score"]
    writer.writerow(header)
    for score_data in scores:
        row = [score_data["candidate_name"]]
        for criterion in criteria_list:
            row.append(score_data["scores"].get(criterion, 0))
        row.append(score_data["total_score"])
        writer.writerow(row)
    output.seek(0)
    
    response = StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=resume_scores.csv"
    return response

if __name__ == "__main__":
    import uvicorn
    logging.info("Starting Resume Ranking System")
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)
