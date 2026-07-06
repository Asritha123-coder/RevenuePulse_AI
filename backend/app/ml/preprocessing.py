"""
preprocessing.py
----------------
Data preprocessing module. Handles missing values, scaling, encoding,
and train-test splitting.
"""

from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class DataPreprocessor:
    """Handles data transformation pipelines for training and inference."""

    def __init__(self, num_cols: List[str], cat_cols: List[str]):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.medians: Dict[str, float] = {}
        self.modes: Dict[str, Any] = {}
        self.encoded_cat_cols: List[str] = []
        self._is_fitted = False

    def fit(self, df: pd.DataFrame) -> "DataPreprocessor":
        """Fit preprocessing parameters on training DataFrame."""
        # Calculate medians for numerical columns
        for col in self.num_cols:
            if col in df.columns:
                self.medians[col] = float(df[col].median()) if not df[col].isnull().all() else 0.0
                
        # Calculate modes for categorical columns
        for col in self.cat_cols:
            if col in df.columns:
                mode_series = df[col].dropna()
                self.modes[col] = mode_series.mode()[0] if not mode_series.empty else "Unknown"

        # Fit Scaler
        df_num = df[self.num_cols].copy()
        for col in self.num_cols:
            df_num[col] = df_num[col].fillna(self.medians.get(col, 0.0))
        self.scaler.fit(df_num)

        # Fit Encoder
        df_cat = df[self.cat_cols].copy().astype(str)
        for col in self.cat_cols:
            df_cat[col] = df_cat[col].fillna(self.modes.get(col, "Unknown"))
        self.encoder.fit(df_cat)
        self.encoded_cat_cols = list(self.encoder.get_feature_names_out(self.cat_cols))
        
        self._is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted scaling, imputations, and encodings to DataFrame."""
        if not self._is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transforming data.")
            
        df = df.copy()
        
        # 1. Handle Missing Numerical Values
        for col in self.num_cols:
            if col not in df.columns:
                df[col] = self.medians.get(col, 0.0)
            else:
                df[col] = df[col].fillna(self.medians.get(col, 0.0))
                
        # 2. Handle Missing Categorical Values
        for col in self.cat_cols:
            if col not in df.columns:
                df[col] = self.modes.get(col, "Unknown")
            else:
                df[col] = df[col].fillna(self.modes.get(col, "Unknown"))

        # 3. Transform Numerical Columns
        num_scaled = self.scaler.transform(df[self.num_cols])
        df_scaled_num = pd.DataFrame(num_scaled, columns=self.num_cols, index=df.index)

        # 4. Transform Categorical Columns
        cat_encoded = self.encoder.transform(df[self.cat_cols].astype(str))
        df_encoded_cat = pd.DataFrame(cat_encoded, columns=self.encoded_cat_cols, index=df.index)

        # Combine
        return pd.concat([df_scaled_num, df_encoded_cat], axis=1)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine fitting and transforming steps."""
        return self.fit(df).transform(df)

    def prepare_single_record(self, record: Dict[str, Any]) -> pd.DataFrame:
        """Prepare a single input dictionary for model prediction."""
        # Convert dictionary to DataFrame containing one row
        df = pd.DataFrame([record])
        return self.transform(df)


def create_train_test_split(
    df: pd.DataFrame, 
    target_col: str, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the dataset into training and testing segments.
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test
