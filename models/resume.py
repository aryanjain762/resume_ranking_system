from pydantic import BaseModel

class Resume(BaseModel):
    name: str
    skills: list
    experience: list
    education: list
