from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class ClaimData(BaseModel):
    worker_id: str
    zone: str

@app.post("/api/fraud-score")
def fraud_score(data: ClaimData):
    return {
        "fraud_score": round(random.uniform(0.01, 0.15), 2)
    }
