import logging
import json
import re
import groq
import os  # Import the os module
from typing import List, Dict

# Define constants
MODEL = "llama3-70b-8192"
groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

async def extract_criteria_with_llm(text: str) -> List[str]:
    logging.info("Extracting criteria from job description")
    prompt = f"""
    You are an AI assistant that helps recruiters extract key ranking criteria from job descriptions.
    
    Given the following job description, extract a list of clear, specific criteria that can be used to evaluate candidates.
    Focus on required skills, certifications, experience, and qualifications. Format your response as a JSON array of strings,
    with each string representing one specific criterion.
    
    Job Description:
    {text}
    
    Format your response as a JSON array of strings like this:
    ["Must have certification XYZ", "5+ years of experience in Python development", "Strong background in Machine Learning"]
    """
    
    try:
        logging.info("Calling Groq API for criteria extraction")
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts key criteria from job descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        response_text = completion.choices[0].message.content.strip()
        logging.info(f"Received response of length {len(response_text)}")
        logging.info(f"Raw LLM response for criteria: {response_text}")
        
        criteria_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if criteria_match:
            criteria_json = criteria_match.group(0)
            criteria = json.loads(criteria_json)
            logging.info(f"Successfully extracted {len(criteria)} criteria: {criteria}")
            return criteria
        else:
            logging.error("Failed to extract criteria list from response")
            raise ValueError("Failed to extract criteria list from response")
            
    except Exception as e:
        logging.error(f"Error with Groq LLM processing for criteria extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error with Groq LLM processing: {str(e)}")

async def score_resume_with_llm(resume_text: str, criteria: List[str], candidate_name: str) -> Dict[str, any]:
    logging.info(f"Scoring resume for candidate: {candidate_name}")
    
    criteria_mapping = {f"criterion{i+1}": criterion for i, criterion in enumerate(criteria)}
    
    prompt = f"""
    You are an AI assistant that helps recruiters score resumes against job criteria.
    
    Given the following resume and criteria, score the candidate on each criterion on a scale of 0-5,
    where 0 means not mentioned/completely missing and 5 means excellent match/fully meets the criterion.
    
    Resume:
    {resume_text[:4000]}
    
    Criteria to evaluate:
    {json.dumps(criteria_mapping, indent=2)}
    
    For the candidate named "{candidate_name}", provide scores in clean JSON format WITHOUT ANY COMMENTS:
    {{
      "candidate_name": "{candidate_name}",
      "scores": {{
        "criterion1": score,
        "criterion2": score,
        ...
      }},
      "total_score": sum_of_scores
    }}
    
    IMPORTANT: Return only the JSON object without any comments, explanations, or backticks.
    """
    
    try:
        logging.info(f"Making Groq API call for {candidate_name}")
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that scores resumes based on job criteria. Return only clean JSON without comments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        response_text = completion.choices[0].message.content.strip()
        logging.info(f"Received response of length {len(response_text)}")
        
        json_text = response_text
        if "```" in json_text:
            json_text = json_text.split("```")[1].strip()
            if json_text.startswith("json"):
                json_text = json_text[4:].strip()
                
        try:
            score_data = json.loads(json_text)
            logging.info(f"Successfully parsed score data for {candidate_name}")
            
            normalized_scores = {}
            for criterion in criteria:
                for key, value in score_data["scores"].items():
                    if criteria_mapping.get(key) == criterion:
                        normalized_scores[criterion] = value
                        break
                if criterion not in normalized_scores:
                    normalized_scores[criterion] = 0
                     
            score_data["scores"] = normalized_scores
            score_data["total_score"] = sum(normalized_scores.values())
            
            return score_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON response for {candidate_name}: {e}")
            logging.error(f"Problematic JSON text: {json_text}")
            raise
            
    except Exception as e:
        logging.error(f"Error with Groq LLM processing for scoring: {str(e)}")
        default_scores = {criterion: 0 for criterion in criteria}
        return {
            "candidate_name": candidate_name,
            "scores": default_scores,
            "total_score": 0
        }

async def extract_candidate_name(text: str) -> str:
    logging.info("Extracting candidate name from resume")
    prompt = f"""
    Extract the full name of the candidate from this resume text. If no name is found,
    return "Unknown Candidate". Just return the name, nothing else.
    
    Resume:
    {text[:1000]}  # Using first 1000 chars to save tokens
    """
    
    try:
        logging.info("Calling Groq API for name extraction")
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You extract candidate names from resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        name = completion.choices[0].message.content.strip()
        logging.info(f"Extracted name: {name}")
        
        if "unknown" in name.lower():
            return "Unknown Candidate"
        return name.strip('".')
        
    except Exception as e:
        logging.error(f"Error with Groq LLM processing for name extraction: {str(e)}")
        return "Unknown Candidate"