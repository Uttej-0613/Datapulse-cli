import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from pathlib import Path

def train_model(data: list[dict], model_path: str = "salary_predictor.pkl") -> dict:
    """
    Trains a Linear Regression model on the cleaned data.
    Returns a dictionary with model, metrics, and formula.
    """
    if not data:
        raise ValueError("Cannot train on empty data!")
    
    X = np.array([[row['age']] for row in data])
    y = np.array([row['salary'] for row in data])
    
    model = LinearRegression()
    model.fit(X, y)
    
    predictions = model.predict(X)
    r2 = r2_score(y, predictions)
    
    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    return {
        'model': model,
        'r2_score': r2,
        'slope': model.coef_[0],
        'intercept': model.intercept_,
        'model_path': model_path
    }

def predict_age(model, age: int) -> float:
    """Predict salary for a given age using the trained model."""
    return model.predict([[age]])[0]
