"""
Model Trainer for Shortlisting Prediction
Generates training data based on research findings and trains ML model.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
from pathlib import Path
import json

class ShortlistModelTrainer:
    """
    Trains ML model for shortlisting prediction based on research findings.
    
    Research Findings:
    - ATS awareness: 5.9x impact (p=0.002)
    - Skills knowledge: 7.4x impact (p<0.001)
    - Resume difficulty: r=-0.907 correlation
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            'skill_match_percentage',
            'ats_compatibility_score',
            'experience_match_score',
            'resume_quality_score',
            'education_match',
            'keyword_density',
            'resume_length_score'
        ]
    
    def generate_training_data(self, n_samples=1000):
        """
        Generate synthetic training data based on research findings.
        
        Research-based patterns:
        - High skill match + ATS aware → High shortlist probability
        - Low ATS score → Low shortlist probability (5.9x impact)
        - Low skill match → Low shortlist probability (7.4x impact)
        """
        np.random.seed(42)
        
        data = []
        
        for _ in range(n_samples):
            # Generate features
            skill_match = np.random.beta(2, 2)  # 0-1, centered around 0.5
            ats_score = np.random.beta(2, 5) if np.random.random() < 0.74 else np.random.beta(5, 2)  # 74% low ATS awareness
            experience_match = np.random.beta(3, 3)
            resume_quality = np.random.beta(3, 2)
            education_match = np.random.choice([0, 0.5, 1], p=[0.2, 0.3, 0.5])
            keyword_density = np.random.beta(2, 3)
            resume_length = np.random.beta(3, 2)
            
            # Calculate shortlist probability based on research findings
            # ATS: 5.9x impact, Skills: 7.4x impact
            base_prob = 0.1  # Base 10% success rate (research: 9.5%)
            
            # Apply research-based multipliers
            if ats_score > 0.7:
                ats_multiplier = 5.9  # Research finding
            else:
                ats_multiplier = 1.0
            
            if skill_match > 0.7:
                skill_multiplier = 7.4  # Research finding
            else:
                skill_multiplier = 1.0
            
            # Combined probability
            probability = base_prob * ats_multiplier * skill_multiplier
            probability *= (1 + experience_match * 0.5)
            probability *= (1 + resume_quality * 0.3)
            probability *= (1 + education_match * 0.2)
            
            # Add some noise
            probability += np.random.normal(0, 0.1)
            probability = np.clip(probability, 0, 1)
            
            # Binary outcome (shortlisted or not)
            shortlisted = 1 if probability > 0.5 else 0
            
            data.append({
                'skill_match_percentage': skill_match,
                'ats_compatibility_score': ats_score,
                'experience_match_score': experience_match,
                'resume_quality_score': resume_quality,
                'education_match': education_match,
                'keyword_density': keyword_density,
                'resume_length_score': resume_length,
                'shortlisted': shortlisted,
                'probability': probability
            })
        
        df = pd.DataFrame(data)
        
        # Print statistics
        print(f"Generated {n_samples} training samples")
        print(f"Shortlisted: {df['shortlisted'].sum()} ({df['shortlisted'].mean()*100:.1f}%)")
        print(f"Not shortlisted: {(1-df['shortlisted']).sum()} ({(1-df['shortlisted']).mean()*100:.1f}%)")
        
        return df
    
    def train_model(self, df):
        """Train Random Forest classifier."""
        X = df[self.feature_names]
        y = df['shortlisted']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nTraining set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        print("\nTraining Random Forest model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60)
        print(f"Accuracy:  {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1 Score:  {f1:.3f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Not Shortlisted', 'Shortlisted']))
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        print(f"\nCross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(feature_importance.to_string(index=False))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance.to_dict('records')
        }
    
    def save_model(self, model_dir='models'):
        """Save trained model and metadata."""
        model_path = Path(__file__).parent.parent.parent / model_dir
        model_path.mkdir(exist_ok=True)
        
        # Save model
        model_file = model_path / 'shortlist_predictor.pkl'
        joblib.dump(self.model, model_file)
        print(f"\n✓ Model saved to: {model_file}")
        
        # Save feature names
        features_file = model_path / 'feature_names.json'
        with open(features_file, 'w') as f:
            json.dump(self.feature_names, f)
        print(f"✓ Feature names saved to: {features_file}")
        
        return model_file


def main():
    """Main training pipeline."""
    print("="*60)
    print("SKILLLENS SHORTLISTING PREDICTION MODEL TRAINER")
    print("="*60)
    print("\nBased on research findings:")
    print("- ATS awareness: 5.9x impact (p=0.002)")
    print("- Skills knowledge: 7.4x impact (p<0.001)")
    print("- Average success rate: 9.5%")
    print("="*60)
    
    trainer = ShortlistModelTrainer()
    
    # Generate training data
    print("\n1. Generating training data...")
    df = trainer.generate_training_data(n_samples=2000)
    
    # Train model
    print("\n2. Training model...")
    metrics = trainer.train_model(df)
    
    # Save model
    print("\n3. Saving model...")
    model_file = trainer.save_model()
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE")
    print("="*60)
    print(f"\nModel ready for predictions!")
    print(f"Expected accuracy: {metrics['accuracy']:.1%}")
    
    return trainer, metrics


if __name__ == "__main__":
    trainer, metrics = main()
