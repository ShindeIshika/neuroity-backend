# app/core/config.py
import os
import json
import tempfile

def setup_kaggle_credentials():
    """Set up Kaggle credentials from environment variable"""
    kaggle_json = os.environ.get('KAGGLE_JSON')
    if kaggle_json:
        try:
            # Create .kaggle directory
            kaggle_dir = os.path.expanduser('~/.kaggle')
            os.makedirs(kaggle_dir, exist_ok=True)
            
            # Write kaggle.json
            json_path = os.path.join(kaggle_dir, 'kaggle.json')
            with open(json_path, 'w') as f:
                f.write(kaggle_json)
            
            # Set permissions (Linux/macOS only)
            os.chmod(json_path, 0o600)
            
            # Set environment variable
            os.environ['KAGGLE_CONFIG_DIR'] = kaggle_dir
            print("✅ Kaggle credentials configured from environment")
        except Exception as e:
            print(f"⚠️ Failed to setup Kaggle credentials: {e}")