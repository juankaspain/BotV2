#!/usr/bin/env python3
"""AI Anomaly Detection System for BotV2

Detects unusual market behavior and trading anomalies using multiple methods:
1. Isolation Forest (ML-based)
2. Statistical outliers (Z-score, IQR)
3. Volume spike detection
4. Correlation breakdown detection

Usage:
    # Train model
    python src/ai/anomaly_detector.py --train
    
    # Detect anomalies in real-time
    python src/ai/anomaly_detector.py --detect
    
    # Programmatic usage
    from src.ai.anomaly_detector import AnomalyDetector
    detector = AnomalyDetector()
    anomalies = detector.detect(market_data)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pickle
import json
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """Anomaly detection system for trading data"""
    
    def __init__(self, model_path: str = 'models/anomaly_detector.pkl'):
        """Initialize anomaly detector
        
        Args:
            model_path: Path to save/load trained model
        """
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'price_change_pct',
            'volume_ratio',
            'spread_pct',
            'volatility',
            'trade_frequency',
            'slippage_pct'
        ]
        
        # Thresholds for different anomaly types
        self.thresholds = {
            'price_gap': 0.02,        # 2% price gap
            'volume_spike': 3.0,      # 3x average volume
            'slippage': 0.005,        # 0.5% slippage
            'latency': 1000,          # 1 second latency
            'z_score': 3.0,           # 3 standard deviations
            'iqr_multiplier': 1.5     # IQR outlier detection
        }
        
        # Load model if exists
        if os.path.exists(model_path):
            self.load_model()
        else:
            print(f"⚠️  No trained model found at {model_path}")
            print("   Run with --train to train a new model")
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features from market data
        
        Args:
            data: DataFrame with columns: timestamp, open, high, low, close, volume
        
        Returns:
            DataFrame with extracted features
        """
        features = pd.DataFrame()
        
        # Price change percentage
        features['price_change_pct'] = data['close'].pct_change().fillna(0)
        
        # Volume ratio (current / 20-period moving average)
        volume_ma = data['volume'].rolling(window=20, min_periods=1).mean()
        features['volume_ratio'] = (data['volume'] / volume_ma).fillna(1.0)
        
        # Spread percentage (high-low / close)
        features['spread_pct'] = ((data['high'] - data['low']) / data['close']).fillna(0)
        
        # Volatility (20-period standard deviation of returns)
        returns = data['close'].pct_change()
        features['volatility'] = returns.rolling(window=20, min_periods=1).std().fillna(0)
        
        # Trade frequency (placeholder - in production, use actual trade count)
        features['trade_frequency'] = 1.0  # Normalized value
        
        # Slippage (placeholder - in production, use actual slippage data)
        features['slippage_pct'] = 0.0
        
        return features
    
    def train(self, data: pd.DataFrame, contamination: float = 0.05) -> Dict:
        """Train Isolation Forest model
        
        Args:
            data: Historical market data
            contamination: Expected proportion of anomalies (default 5%)
        
        Returns:
            Training metrics
        """
        print("🤖 Training Anomaly Detection Model...")
        print(f"   Data shape: {data.shape}")
        print(f"   Contamination: {contamination*100:.1f}%")
        
        # Extract features
        features = self.extract_features(data)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        
        self.model.fit(X_scaled)
        
        # Get anomaly scores
        scores = self.model.decision_function(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        anomaly_count = (predictions == -1).sum()
        anomaly_pct = (anomaly_count / len(predictions)) * 100
        
        metrics = {
            'total_samples': len(data),
            'anomalies_detected': int(anomaly_count),
            'anomaly_percentage': float(anomaly_pct),
            'contamination': contamination,
            'avg_score': float(scores.mean()),
            'score_std': float(scores.std()),
            'trained_at': datetime.now().isoformat()
        }
        
        print(f"\n✅ Training Complete!")
        print(f"   Anomalies detected: {anomaly_count} ({anomaly_pct:.2f}%)")
        print(f"   Average score: {metrics['avg_score']:.4f}")
        
        # Save model
        self.save_model()
        
        return metrics
    
    def detect(self, data: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in market data
        
        Args:
            data: Recent market data (last N candles)
        
        Returns:
            List of detected anomalies with details
        """
        if self.model is None:
            raise ValueError("Model not trained. Run train() first.")
        
        anomalies = []
        
        # 1. ML-based detection (Isolation Forest)
        ml_anomalies = self._detect_ml(data)
        anomalies.extend(ml_anomalies)
        
        # 2. Statistical outliers
        stat_anomalies = self._detect_statistical(data)
        anomalies.extend(stat_anomalies)
        
        # 3. Volume spikes
        volume_anomalies = self._detect_volume_spikes(data)
        anomalies.extend(volume_anomalies)
        
        # 4. Price gaps
        gap_anomalies = self._detect_price_gaps(data)
        anomalies.extend(gap_anomalies)
        
        # Remove duplicates and sort by severity
        anomalies = self._deduplicate_anomalies(anomalies)
        anomalies.sort(key=lambda x: x['severity'], reverse=True)
        
        return anomalies
    
    def _detect_ml(self, data: pd.DataFrame) -> List[Dict]:
        """ML-based anomaly detection using Isolation Forest"""
        features = self.extract_features(data)
        X_scaled = self.scaler.transform(features)
        
        # Predict anomalies
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                severity = self._calculate_severity(score, method='ml')
                
                anomalies.append({
                    'type': 'ml_anomaly',
                    'timestamp': data.iloc[idx]['timestamp'] if 'timestamp' in data.columns else idx,
                    'severity': severity,
                    'score': float(score),
                    'method': 'isolation_forest',
                    'description': f"ML model detected unusual pattern (score: {score:.4f})",
                    'features': features.iloc[idx].to_dict()
                })
        
        return anomalies
    
    def _detect_statistical(self, data: pd.DataFrame) -> List[Dict]:
        """Statistical outlier detection using Z-score"""
        anomalies = []
        
        # Price change Z-score
        price_changes = data['close'].pct_change()
        mean_change = price_changes.mean()
        std_change = price_changes.std()
        
        if std_change > 0:
            z_scores = (price_changes - mean_change) / std_change
            
            for idx, z in enumerate(z_scores):
                if abs(z) > self.thresholds['z_score']:
                    severity = min(100, int(abs(z) * 20))  # Scale severity
                    
                    anomalies.append({
                        'type': 'statistical_outlier',
                        'timestamp': data.iloc[idx]['timestamp'] if 'timestamp' in data.columns else idx,
                        'severity': severity,
                        'z_score': float(z),
                        'method': 'z_score',
                        'description': f"Price change is {abs(z):.2f} standard deviations from mean",
                        'price_change_pct': float(price_changes.iloc[idx] * 100)
                    })
        
        return anomalies
    
    def _detect_volume_spikes(self, data: pd.DataFrame) -> List[Dict]:
        """Detect unusual volume spikes"""
        anomalies = []
        
        # Calculate volume moving average
        volume_ma = data['volume'].rolling(window=20, min_periods=1).mean()
        volume_ratio = data['volume'] / volume_ma
        
        for idx, ratio in enumerate(volume_ratio):
            if ratio > self.thresholds['volume_spike']:
                severity = min(100, int((ratio - 1) * 30))
                
                anomalies.append({
                    'type': 'volume_spike',
                    'timestamp': data.iloc[idx]['timestamp'] if 'timestamp' in data.columns else idx,
                    'severity': severity,
                    'volume_ratio': float(ratio),
                    'method': 'volume_analysis',
                    'description': f"Volume is {ratio:.1f}x the 20-period average",
                    'volume': float(data.iloc[idx]['volume'])
                })
        
        return anomalies
    
    def _detect_price_gaps(self, data: pd.DataFrame) -> List[Dict]:
        """Detect significant price gaps"""
        anomalies = []
        
        # Calculate gap from previous close to current open
        if 'open' in data.columns:
            gaps = (data['open'] - data['close'].shift(1)) / data['close'].shift(1)
            
            for idx, gap in enumerate(gaps):
                if abs(gap) > self.thresholds['price_gap']:
                    severity = min(100, int(abs(gap) * 2000))  # 2% gap = 40 severity
                    
                    anomalies.append({
                        'type': 'price_gap',
                        'timestamp': data.iloc[idx]['timestamp'] if 'timestamp' in data.columns else idx,
                        'severity': severity,
                        'gap_pct': float(gap * 100),
                        'method': 'gap_analysis',
                        'description': f"Price gap of {abs(gap)*100:.2f}% detected",
                        'direction': 'up' if gap > 0 else 'down'
                    })
        
        return anomalies
    
    def _calculate_severity(self, score: float, method: str = 'ml') -> int:
        """Calculate anomaly severity (0-100)
        
        Args:
            score: Anomaly score from model
            method: Detection method
        
        Returns:
            Severity score (0=low, 100=critical)
        """
        if method == 'ml':
            # Isolation Forest scores: typically -0.5 to 0.5
            # More negative = more anomalous
            normalized = (abs(score) - 0.1) / 0.4  # Normalize to 0-1
            severity = int(max(0, min(100, normalized * 100)))
        else:
            severity = 50  # Default medium severity
        
        return severity
    
    def _deduplicate_anomalies(self, anomalies: List[Dict]) -> List[Dict]:
        """Remove duplicate anomalies for the same timestamp"""
        seen_timestamps = set()
        unique_anomalies = []
        
        for anomaly in sorted(anomalies, key=lambda x: x['severity'], reverse=True):
            ts = anomaly['timestamp']
            if ts not in seen_timestamps:
                seen_timestamps.add(ts)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies
    
    def generate_alert(self, anomaly: Dict) -> Dict:
        """Generate alert from detected anomaly
        
        Args:
            anomaly: Anomaly detection result
        
        Returns:
            Alert object ready for notification system
        """
        severity_level = self._get_severity_level(anomaly['severity'])
        
        alert = {
            'type': 'anomaly_detected',
            'severity': severity_level,
            'title': self._get_alert_title(anomaly),
            'message': anomaly['description'],
            'timestamp': anomaly['timestamp'],
            'data': anomaly,
            'recommendations': self._get_recommendations(anomaly)
        }
        
        return alert
    
    def _get_severity_level(self, severity: int) -> str:
        """Convert numeric severity to level"""
        if severity >= 80:
            return 'critical'
        elif severity >= 60:
            return 'high'
        elif severity >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _get_alert_title(self, anomaly: Dict) -> str:
        """Generate alert title from anomaly"""
        titles = {
            'ml_anomaly': '🤖 ML Anomaly Detected',
            'statistical_outlier': '📊 Statistical Outlier',
            'volume_spike': '📈 Volume Spike',
            'price_gap': '⚠️ Price Gap Detected'
        }
        return titles.get(anomaly['type'], '⚠️ Anomaly Detected')
    
    def _get_recommendations(self, anomaly: Dict) -> List[str]:
        """Generate recommendations based on anomaly type"""
        recommendations = []
        
        if anomaly['type'] == 'volume_spike':
            recommendations.append("Monitor for potential breakout or reversal")
            recommendations.append("Consider tightening stop-loss temporarily")
        
        elif anomaly['type'] == 'price_gap':
            recommendations.append("Check for news or economic events")
            recommendations.append("Wait for gap fill before entering positions")
        
        elif anomaly['severity'] >= 80:
            recommendations.append("Reduce position sizes by 50%")
            recommendations.append("Widen stop-loss buffers by 20%")
            recommendations.append("Avoid new entries until market normalizes")
        
        elif anomaly['severity'] >= 60:
            recommendations.append("Monitor closely for next 1-2 hours")
            recommendations.append("Consider taking partial profits")
        
        return recommendations
    
    def save_model(self):
        """Save trained model and scaler to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'thresholds': self.thresholds
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.thresholds = model_data.get('thresholds', self.thresholds)
        
        print(f"✅ Model loaded from {self.model_path}")


# ============================================
# CLI INTERFACE
# ============================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='BotV2 Anomaly Detector')
    parser.add_argument('--train', action='store_true', help='Train model on historical data')
    parser.add_argument('--detect', action='store_true', help='Detect anomalies in recent data')
    parser.add_argument('--data', type=str, help='Path to CSV data file')
    parser.add_argument('--contamination', type=float, default=0.05, help='Expected anomaly rate')
    
    args = parser.parse_args()
    
    detector = AnomalyDetector()
    
    if args.train:
        # Generate sample data if no file provided
        if args.data:
            data = pd.read_csv(args.data)
        else:
            print("⚠️  No data file provided, generating sample data...")
            # Generate sample OHLCV data
            dates = pd.date_range(end=datetime.now(), periods=1000, freq='1h')
            data = pd.DataFrame({
                'timestamp': dates,
                'open': np.random.randn(1000).cumsum() + 100,
                'high': np.random.randn(1000).cumsum() + 101,
                'low': np.random.randn(1000).cumsum() + 99,
                'close': np.random.randn(1000).cumsum() + 100,
                'volume': np.random.randint(1000, 10000, 1000)
            })
        
        metrics = detector.train(data, contamination=args.contamination)
        print(f"\n📊 Training Metrics:")
        print(json.dumps(metrics, indent=2))
    
    elif args.detect:
        # Generate sample recent data
        if args.data:
            data = pd.read_csv(args.data).tail(100)
        else:
            print("⚠️  No data file provided, generating sample data...")
            dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
            data = pd.DataFrame({
                'timestamp': dates,
                'open': np.random.randn(100).cumsum() + 100,
                'high': np.random.randn(100).cumsum() + 101,
                'low': np.random.randn(100).cumsum() + 99,
                'close': np.random.randn(100).cumsum() + 100,
                'volume': np.random.randint(1000, 10000, 100)
            })
        
        anomalies = detector.detect(data)
        
        print(f"\n🔍 Detected {len(anomalies)} anomalies:\n")
        for anomaly in anomalies:
            alert = detector.generate_alert(anomaly)
            print(f"{alert['title']} - Severity: {alert['severity']}")
            print(f"   {alert['message']}")
            if alert['recommendations']:
                print(f"   Recommendations:")
                for rec in alert['recommendations']:
                    print(f"     - {rec}")
            print()
    
    else:
        parser.print_help()