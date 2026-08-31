import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import IncidentRequest, IncidentResponse
from app.model_loader import predict_severity, get_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IT Incident Severity Classifier",
    version="1.0.0",
    description="Capstone API – predicts severity of IT incident reports"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_model_on_startup():
    logger.info("Loading model...")
    get_model()
    logger.info("Model ready.")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/v1/predict", response_model=IncidentResponse)
def predict(payload: IncidentRequest):
    try:
        result = predict_severity(payload.text)
        logger.info(f"Prediction: {result['severity']} ({result['confidence']})")
        return result
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})