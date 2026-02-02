"""
Predictive Model Service
Provides shortlisting probability predictions using trained ML model.
"""

import logging
from typing import List, Dict, Tuple
from pathlib import Path
import joblib
import json
import numpy as np

from app.models.prediction_models import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse, JobPrediction
)
from app.services.resume_parser import ResumeParser
from app.services.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


class PredictiveModel:
    """
    ML-based prediction service for shortlisting probability.
    Uses trained Random Forest model based on research findings.
    """
    
    def __init__(self):
        """Initialize the predictive model."""
        self.model = None
        self.feature_names = None
        self.resume_parser = ResumeParser()
        self.scoring_engine = ScoringEngine()
        self._load_model()
    
    def _load_model(self):
        """Load trained model from disk."""
        try:
            model_dir = Path(__file__).parent.parent.parent / 'models'
            model_file = model_dir / 'shortlist_predictor.pkl'
            features_file = model_dir / 'feature_names.json'
            
            if not model_file.exists():
                logger.warning(f"Model file not found: {model_file}")
                logger.warning("Run model_trainer.py to train the model first")
                return
            
            self.model = joblib.load(model_file)
            
            with open(features_file, 'r') as f:
                self.feature_names = json.load(f)
            
            logger.info(f"Model loaded successfully from {model_file}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def _extract_features(self, resume_text: str, job_description: str, 
                         user_skills: List[str], experience_years: float) -> np.ndarray:
        """
        Extract features for prediction.
        
        Features:
        - skill_match_percentage
        - ats_compatibility_score
        - experience_match_score
        - resume_quality_score
        - education_match
        - keyword_density
        - resume_length_score
        """
        try:
            # Parse resume
            resume_data = self.resume_parser.parse_text(resume_text)
            
            # Get scoring
            scores = self.scoring_engine.calculate_comprehensive_score(
                resume_data, job_description
            )
            
            # Extract features
            features = [
                scores.get('skill_match', 0.5),  # skill_match_percentage
                scores.get('ats_score', 0.5),    # ats_compatibility_score
                min(experience_years / 5.0, 1.0),  # experience_match_score (normalized)
                scores.get('overall_score', 0.5) / 100.0,  # resume_quality_score
                scores.get('education_match', 0.5),  # education_match
                scores.get('keyword_density', 0.5),  # keyword_density
                min(len(resume_text) / 2000.0, 1.0)  # resume_length_score (normalized)
            ]
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            # Return default features
            return np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]])
    
    def _get_confidence_level(self, probability: float, feature_values: np.ndarray) -> str:
        """Determine confidence level based on probability and feature variance."""
        # High confidence if probability is extreme (very high or very low)
        if probability > 0.8 or probability < 0.2:
            return "High"
        # Medium confidence for moderate probabilities
        elif 0.3 <= probability <= 0.7:
            # Check feature variance
            variance = np.var(feature_values)
            if variance < 0.05:
                return "Medium"
            else:
                return "Low"
        else:
            return "Medium"
    
    def _generate_recommendations(self, features: np.ndarray, probability: float) -> List[str]:
        """Generate recommendations based on feature values."""
        recommendations = []
        
        feature_dict = {
            'skill_match': features[0][0],
            'ats_score': features[0][1],
            'experience': features[0][2],
            'resume_quality': features[0][3],
            'education': features[0][4],
            'keywords': features[0][5],
            'length': features[0][6]
        }
        
        # Skill match
        if feature_dict['skill_match'] < 0.7:
            recommendations.append(f"Improve skill match (currently {feature_dict['skill_match']*100:.0f}%) - add missing required skills")
        
        # ATS compatibility
        if feature_dict['ats_score'] < 0.7:
            recommendations.append(f"Improve ATS compatibility (currently {feature_dict['ats_score']*100:.0f}%) - optimize formatting and keywords")
        
        # Experience
        if feature_dict['experience'] < 0.5:
            recommendations.append("Highlight relevant experience more prominently")
        
        # Resume quality
        if feature_dict['resume_quality'] < 0.6:
            recommendations.append("Improve overall resume quality - use action verbs and quantify achievements")
        
        # Keywords
        if feature_dict['keywords'] < 0.6:
            recommendations.append("Increase keyword density - include more job-relevant terms")
        
        if not recommendations:
            recommendations.append("Your resume looks strong! Consider applying to this position.")
        
        return recommendations[:3]  # Top 3 recommendations
    
    async def predict_shortlist_probability(self, request: PredictionRequest) -> PredictionResponse:
        """
        Predict shortlisting probability for a resume-JD pair.
        
        Args:
            request: Prediction request with resume and JD
            
        Returns:
            Prediction response with probability and recommendations
        """
        if self.model is None:
            # Return default prediction if model not loaded
            return PredictionResponse(
                shortlist_probability=50.0,
                confidence="Low",
                factors={
                    "skill_match": 0.5,
                    "ats_compatibility": 0.5,
                    "experience_match": 0.5,
                    "resume_quality": 0.5
                },
                recommendations=["Model not loaded. Train the model first using model_trainer.py"]
            )
        
        try:
            # Extract features
            features = self._extract_features(
                request.resume_text or "",
                request.job_description,
                request.user_skills,
                request.experience_years
            )
            
            # Predict probability
            probability = self.model.predict_proba(features)[0][1]  # Probability of class 1 (shortlisted)
            probability_percentage = probability * 100
            
            # Get confidence
            confidence = self._get_confidence_level(probability, features)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(features, probability)
            
            # Create factors dict
            factors = {
                "skill_match": float(features[0][0]),
                "ats_compatibility": float(features[0][1]),
                "experience_match": float(features[0][2]),
                "resume_quality": float(features[0][3])
            }
            
            return PredictionResponse(
                shortlist_probability=round(probability_percentage, 1),
                confidence=confidence,
                factors=factors,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return PredictionResponse(
                shortlist_probability=50.0,
                confidence="Low",
                factors={},
                recommendations=[f"Error in prediction: {str(e)}"]
            )
    
    async def predict_batch(self, request: BatchPredictionRequest) -> BatchPredictionResponse:
        """
        Predict shortlisting probability for multiple job descriptions.
        
        Args:
            request: Batch prediction request
            
        Returns:
            Batch prediction response with ranked jobs
        """
        predictions = []
        
        for jd in request.job_descriptions:
            single_request = PredictionRequest(
                resume_text=request.resume_text,
                job_description=jd,
                user_skills=request.user_skills,
                experience_years=request.experience_years
            )
            
            pred = await self.predict_shortlist_probability(single_request)
            
            predictions.append({
                'job_description': jd,
                'probability': pred.shortlist_probability,
                'confidence': pred.confidence
            })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Add ranks
        job_predictions = [
            JobPrediction(
                job_description=p['job_description'],
                shortlist_probability=p['probability'],
                confidence=p['confidence'],
                rank=idx + 1
            )
            for idx, p in enumerate(predictions)
        ]
        
        return BatchPredictionResponse(
            predictions=job_predictions,
            best_match=job_predictions[0] if job_predictions else None,
            total_jobs=len(job_predictions)
        )


# Singleton instance
_predictor_instance = None

def get_predictor() -> PredictiveModel:
    """Get singleton instance of the predictor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = PredictiveModel()
    return _predictor_instance
