import os
import sys
import json
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

from ingestion.cleaners.text_processor import main as run_processing
from indexing.main import build_index

def update_metadata():
    metadata_path = "data/structured/courses.json"
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {}
                
    if "metadata" not in data:
        data["metadata"] = {}
        
    data["metadata"]["last_updated"] = now
    
    # Count processed funds
    cleaned_dir = "data/cleaned"
    if os.path.exists(cleaned_dir):
        data["funds_count"] = len([f for f in os.listdir(cleaned_dir) if f.endswith('.json')])
    
    with open(metadata_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"--- Metadata updated: {now} ---")

def refresh_all():
    print("=== STARTING DATA REFRESH PIPELINE ===")
    
    # 1. Scraping (Phase 1 - Crawler)
    print("STAGING: Phase 1 Crawler (Mocking - using existing raw files)...")
    # In a real scenario, we'd call ingestion/crawlers/main.py here
    
    # 2. Pre-processing (Phase 1 - Cleaners)
    print("STAGING: Phase 1 Processing...")
    run_processing()
    
    # 3. Embedding & Indexing (Phase 2)
    print("STAGING: Phase 2 Indexing...")
    build_index()
    
    # 4. Update Versioning/Metadata (Phase 5)
    update_metadata()
    
    print("=== PIPELINE EXECUTION COMPLETE ===")

if __name__ == "__main__":
    refresh_all()
