import base64
import pandas as pd
from typing import Dict, List
import os

def encode_image(image_bytes: bytes) -> str:
    """Encodes bytes to a base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def load_divisions_and_departments(file_path: str) -> Dict[str, List[str]]:
    """
    Loads division and department mapping from an Excel file.
    Expected columns: 'Division', 'Department'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found at {file_path}")
    
    df = pd.read_excel(file_path)
    
    # Clean up column names just in case
    df.columns = [c.strip() for c in df.columns]
    
    mapping = {}
    for division, group in df.groupby('Division'):
        mapping[str(division).strip()] = group['Department'].dropna().unique().tolist()
    
    return mapping
