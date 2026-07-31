# app/core/config.py
import os
import json

def setup_kaggle_credentials():
    """Set up Kaggle credentials from environment variables"""
    username = os.environ.get('KAGGLE_USERNAME')
    key = os.environ.get('KAGGLE_KEY')
    
    if username and key:
        try:
            kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
            os.makedirs(kaggle_dir, exist_ok=True)
            
            json_path = os.path.join(kaggle_dir, 'kaggle.json')
            with open(json_path, 'w') as f:
                json.dump({"username": username, "key": key}, f)
            
            try:
                os.chmod(json_path, 0o600)
            except:
                pass
            
            os.environ['KAGGLE_CONFIG_DIR'] = kaggle_dir
            print(f"✅ Kaggle credentials configured for user: {username}")
        except Exception as e:
            print(f"⚠️ Failed to setup Kaggle credentials: {e}")
    else:
        print("⚠️ KAGGLE_USERNAME and KAGGLE_KEY not set")
        print(f"  Username: {'SET' if username else 'MISSING'}")
        print(f"  Key: {'SET' if key else 'MISSING'}")