"""
Predictions API Router
Endpoints for ML-based shortlisting predictions.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.prediction_models import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse
)
from app.services.predictive_model import get_predictor

router = APIRouter()


@router.post("/shortlist-probability", response_model=PredictionResponse)
async def predict_shortlist_probability(request: PredictionRequest):
    """
    Predict the probability of being shortlisted for a job.
    
    Uses ML model trained on research findings:
    - ATS awareness: 5.9x impact (p=0.002)
    - Skills knowledge: 7.4x impact (p<0.001)
    
    **Research Justification**: Addresses the finding that average success
    rate is only 9.5%. Helps students target high-probability opportunities.
    
    Returns probability (0-100%), confidence level, contributing factors,
    and specific recommendations for improvement.
    """
    try:
        predictor = get_predictor()
        prediction = await predictor.predict_shortlist_probability(request)
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prediction: {str(e)}"
        )


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict shortlisting probability for multiple job descriptions.
    
    Useful for:
    - Comparing multiple job opportunities
    - Ranking jobs by fit
    - Identifying best-match positions
    
    Returns ranked list of jobs with probabilities.
    """
    try:
        predictor = get_predictor()
        predictions = await predictor.predict_batch(request)
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating batch predictions: {str(e)}"
        )


@router.get("/health")
async def predictions_health_check():
    """Health check for predictions service."""
    try:
        predictor = get_predictor()
        model_loaded = predictor.model is not None
        
        return {
            "status": "healthy" if model_loaded else "degraded",
            "service": "Predictions",
            "model_loaded": model_loaded,
            "features": [
                "Shortlisting Probability",
                "Batch Predictions",
                "Confidence Scoring",
                "Recommendations"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Predictions service unavailable: {str(e)}"
        )
