"""
Ensemble Prediction Model

This module combines multiple machine learning models to create robust price predictions.
Uses Prophet, ARIMA, LSTM, and Random Forest models in an ensemble approach.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Model imports
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available. Install with: pip install prophet")

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logging.warning("Statsmodels not available. Install with: pip install statsmodels")

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. Install with: pip install tensorflow")

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available. Install with: pip install scikit-learn")

logger = logging.getLogger(__name__)


class ProphetModel:
    """Prophet time series forecasting model."""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def train(self, data: pd.DataFrame, target_column: str = 'Close') -> bool:
        """
        Train the Prophet model.
        
        Args:
            data: DataFrame with datetime index and target column
            target_column: Name of the column to predict
            
        Returns:
            True if training successful, False otherwise
        """
        if not PROPHET_AVAILABLE:
            logger.error("Prophet not available")
            return False
            
        try:
            # Prepare data for Prophet
            prophet_data = pd.DataFrame({
                'ds': data.index,
                'y': data[target_column]
            })
            
            # Initialize and train model
            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            
            self.model.fit(prophet_data)
            self.is_trained = True
            
            logger.info("Prophet model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training Prophet model: {str(e)}")
            return False
    
    def predict(self, steps: int) -> Optional[pd.DataFrame]:
        """
        Make predictions using the trained model.
        
        Args:
            steps: Number of future periods to predict
            
        Returns:
            DataFrame with predictions or None if failed
        """
        if not self.is_trained:
            logger.error("Model not trained")
            return None
            
        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=steps)
            
            # Make predictions
            forecast = self.model.predict(future)
            
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(steps)
            
        except Exception as e:
            logger.error(f"Error making Prophet predictions: {str(e)}")
            return None


class ARIMAModel:
    """ARIMA time series model."""
    
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order
        self.model = None
        self.fitted_model = None
        self.is_trained = False
        
    def train(self, data: pd.DataFrame, target_column: str = 'Close') -> bool:
        """
        Train the ARIMA model.
        
        Args:
            data: DataFrame with target column
            target_column: Name of the column to predict
            
        Returns:
            True if training successful, False otherwise
        """
        if not STATSMODELS_AVAILABLE:
            logger.error("Statsmodels not available")
            return False
            
        try:
            # Prepare data
            ts_data = data[target_column].dropna()
            
            # Fit ARIMA model
            self.model = ARIMA(ts_data, order=self.order)
            self.fitted_model = self.model.fit()
            self.is_trained = True
            
            logger.info(f"ARIMA{self.order} model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training ARIMA model: {str(e)}")
            return False
    
    def predict(self, steps: int) -> Optional[np.ndarray]:
        """
        Make predictions using the trained model.
        
        Args:
            steps: Number of future periods to predict
            
        Returns:
            Array of predictions or None if failed
        """
        if not self.is_trained:
            logger.error("Model not trained")
            return None
            
        try:
            forecast = self.fitted_model.forecast(steps=steps)
            return forecast.values if hasattr(forecast, 'values') else forecast
            
        except Exception as e:
            logger.error(f"Error making ARIMA predictions: {str(e)}")
            return None


class LSTMModel:
    """LSTM neural network model for time series prediction."""
    
    def __init__(self, sequence_length: int = 60, units: int = 50):
        self.sequence_length = sequence_length
        self.units = units
        self.model = None
        self.scaler = None
        self.is_trained = False
        
    def train(self, data: pd.DataFrame, target_column: str = 'Close', epochs: int = 50) -> bool:
        """
        Train the LSTM model.
        
        Args:
            data: DataFrame with target column
            target_column: Name of the column to predict
            epochs: Number of training epochs
            
        Returns:
            True if training successful, False otherwise
        """
        if not TENSORFLOW_AVAILABLE:
            logger.error("TensorFlow not available")
            return False
            
        try:
            # Prepare data
            prices = data[target_column].values.reshape(-1, 1)
            
            # Scale data
            self.scaler = MinMaxScaler()
            scaled_data = self.scaler.fit_transform(prices)
            
            # Create sequences
            X, y = self._create_sequences(scaled_data)
            
            if len(X) == 0:
                logger.error("Not enough data to create sequences")
                return False
            
            # Build model
            self.model = Sequential([
                LSTM(self.units, return_sequences=True, input_shape=(X.shape[1], 1)),
                Dropout(0.2),
                LSTM(self.units, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            self.model.compile(optimizer='adam', loss='mean_squared_error')
            
            # Train model
            self.model.fit(X, y, batch_size=32, epochs=epochs, verbose=0)
            self.is_trained = True
            
            logger.info("LSTM model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {str(e)}")
            return False
    
    def predict(self, data: pd.DataFrame, target_column: str = 'Close', steps: int = 1) -> Optional[np.ndarray]:
        """
        Make predictions using the trained model.
        
        Args:
            data: Recent data for prediction
            target_column: Name of the target column
            steps: Number of future periods to predict
            
        Returns:
            Array of predictions or None if failed
        """
        if not self.is_trained:
            logger.error("Model not trained")
            return None
            
        try:
            # Get last sequence_length values
            recent_data = data[target_column].tail(self.sequence_length).values.reshape(-1, 1)
            scaled_data = self.scaler.transform(recent_data)
            
            predictions = []
            current_sequence = scaled_data.copy()
            
            for _ in range(steps):
                # Reshape for prediction
                X = current_sequence.reshape(1, self.sequence_length, 1)
                
                # Make prediction
                pred_scaled = self.model.predict(X, verbose=0)
                
                # Inverse transform
                pred = self.scaler.inverse_transform(pred_scaled)[0, 0]
                predictions.append(pred)
                
                # Update sequence for next prediction
                current_sequence = np.roll(current_sequence, -1)
                current_sequence[-1] = pred_scaled
            
            return np.array(predictions)
            
        except Exception as e:
            logger.error(f"Error making LSTM predictions: {str(e)}")
            return None
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i, 0])
            y.append(data[i, 0])
        
        return np.array(X), np.array(y)


class RandomForestModel:
    """Random Forest model for price prediction."""
    
    def __init__(self, n_estimators: int = 100):
        self.n_estimators = n_estimators
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_trained = False
        
    def train(self, data: pd.DataFrame, target_column: str = 'Close') -> bool:
        """
        Train the Random Forest model.
        
        Args:
            data: DataFrame with features and target
            target_column: Name of the column to predict
            
        Returns:
            True if training successful, False otherwise
        """
        if not SKLEARN_AVAILABLE:
            logger.error("Scikit-learn not available")
            return False
            
        try:
            # Create features
            features_df = self._create_features(data)
            
            # Remove rows with NaN values
            features_df = features_df.dropna()
            
            if len(features_df) == 0:
                logger.error("No valid data after feature creation")
                return False
            
            # Separate features and target
            X = features_df.drop(columns=[target_column])
            y = features_df[target_column]
            
            self.feature_columns = X.columns.tolist()
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info("Random Forest model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training Random Forest model: {str(e)}")
            return False
    
    def predict(self, data: pd.DataFrame, steps: int = 1) -> Optional[np.ndarray]:
        """
        Make predictions using the trained model.
        
        Args:
            data: Recent data for prediction
            steps: Number of future periods to predict
            
        Returns:
            Array of predictions or None if failed
        """
        if not self.is_trained:
            logger.error("Model not trained")
            return None
            
        try:
            # Create features for the last available data point
            features_df = self._create_features(data)
            
            # Get the last row with all features
            last_features = features_df[self.feature_columns].iloc[-1:].dropna()
            
            if len(last_features) == 0:
                logger.error("No valid features for prediction")
                return None
            
            # Scale features
            X_scaled = self.scaler.transform(last_features)
            
            # Make prediction (for simplicity, repeat the same prediction for multiple steps)
            prediction = self.model.predict(X_scaled)[0]
            predictions = np.full(steps, prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making Random Forest predictions: {str(e)}")
            return None
    
    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features for the Random Forest model."""
        df = data.copy()
        
        # Price-based features
        df['price_change'] = df['Close'].pct_change()
        df['price_change_2'] = df['Close'].pct_change(2)
        df['price_change_5'] = df['Close'].pct_change(5)
        
        # Moving averages
        df['sma_5'] = df['Close'].rolling(5).mean()
        df['sma_10'] = df['Close'].rolling(10).mean()
        df['sma_20'] = df['Close'].rolling(20).mean()
        
        # Volatility features
        df['volatility_5'] = df['Close'].rolling(5).std()
        df['volatility_10'] = df['Close'].rolling(10).std()
        
        # Volume features (if available)
        if 'Volume' in df.columns:
            df['volume_change'] = df['Volume'].pct_change()
            df['volume_sma_5'] = df['Volume'].rolling(5).mean()
        
        return df


class EnsemblePredictor:
    """
    Ensemble model that combines predictions from multiple models.
    """
    
    def __init__(self):
        self.models = {
            'prophet': ProphetModel(),
            'arima': ARIMAModel(),
            'lstm': LSTMModel(),
            'random_forest': RandomForestModel()
        }
        self.weights = {
            'prophet': 0.3,
            'arima': 0.2,
            'lstm': 0.3,
            'random_forest': 0.2
        }
        self.trained_models = []
        
    def train_all_models(self, data: pd.DataFrame, target_column: str = 'Close') -> Dict[str, bool]:
        """
        Train all available models.
        
        Args:
            data: Training data
            target_column: Target column name
            
        Returns:
            Dictionary with training results for each model
        """
        results = {}
        self.trained_models = []
        
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name} model...")
            success = model.train(data, target_column)
            results[model_name] = success
            
            if success:
                self.trained_models.append(model_name)
        
        logger.info(f"Successfully trained {len(self.trained_models)} out of {len(self.models)} models")
        return results
    
    def predict_ensemble(self, data: pd.DataFrame, steps: int = 1, 
                        target_column: str = 'Close') -> Optional[Dict[str, np.ndarray]]:
        """
        Make ensemble predictions using all trained models.
        
        Args:
            data: Recent data for prediction
            steps: Number of future periods to predict
            target_column: Target column name
            
        Returns:
            Dictionary with predictions from each model and ensemble result
        """
        if not self.trained_models:
            logger.error("No trained models available")
            return None
        
        predictions = {}
        
        # Get predictions from each trained model
        for model_name in self.trained_models:
            model = self.models[model_name]
            
            try:
                if model_name == 'prophet':
                    pred_df = model.predict(steps)
                    if pred_df is not None:
                        predictions[model_name] = pred_df['yhat'].values
                
                elif model_name == 'arima':
                    pred = model.predict(steps)
                    if pred is not None:
                        predictions[model_name] = pred
                
                elif model_name == 'lstm':
                    pred = model.predict(data, target_column, steps)
                    if pred is not None:
                        predictions[model_name] = pred
                
                elif model_name == 'random_forest':
                    pred = model.predict(data, steps)
                    if pred is not None:
                        predictions[model_name] = pred
                        
            except Exception as e:
                logger.error(f"Error getting predictions from {model_name}: {str(e)}")
        
        if not predictions:
            logger.error("No successful predictions from any model")
            return None
        
        # Calculate ensemble prediction
        ensemble_pred = self._calculate_ensemble(predictions, steps)
        predictions['ensemble'] = ensemble_pred
        
        return predictions
    
    def _calculate_ensemble(self, predictions: Dict[str, np.ndarray], steps: int) -> np.ndarray:
        """Calculate weighted ensemble prediction."""
        ensemble = np.zeros(steps)
        total_weight = 0
        
        for model_name, pred in predictions.items():
            if model_name in self.weights and len(pred) == steps:
                weight = self.weights[model_name]
                ensemble += weight * pred
                total_weight += weight
        
        if total_weight > 0:
            ensemble /= total_weight
        
        return ensemble
    
    def get_model_status(self) -> Dict[str, str]:
        """Get status of all models."""
        status = {}
        for model_name, model in self.models.items():
            if hasattr(model, 'is_trained'):
                status[model_name] = "Trained" if model.is_trained else "Not Trained"
            else:
                status[model_name] = "Not Available"
        
        return status


def main():
    """
    Example usage of the ensemble predictor.
    """
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    
    # Generate sample price data with trend
    trend = np.linspace(100, 120, 200)
    noise = np.random.normal(0, 2, 200)
    prices = trend + noise + 5 * np.sin(np.arange(200) * 0.1)
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, 200)
    })
    sample_data.set_index('Date', inplace=True)
    
    print("Ensemble Predictor Demo")
    print("=" * 40)
    
    # Initialize ensemble predictor
    ensemble = EnsemblePredictor()
    
    # Train all models
    print("Training models...")
    training_results = ensemble.train_all_models(sample_data)
    
    print("\nTraining Results:")
    for model, success in training_results.items():
        status = "Success" if success else "Failed"
        print(f"  {model}: {status}")
    
    # Make predictions
    print(f"\nMaking predictions for next 5 days...")
    predictions = ensemble.predict_ensemble(sample_data, steps=5)
    
    if predictions:
        print("\nPredictions:")
        for model, pred in predictions.items():
            print(f"  {model}: {pred}")
    
    # Show model status
    print(f"\nModel Status:")
    status = ensemble.get_model_status()
    for model, stat in status.items():
        print(f"  {model}: {stat}")


if __name__ == "__main__":
    main()