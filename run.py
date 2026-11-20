"""
FALCON EYE — One-Click Command Center Launcher
Launches the FastAPI Gateway and Web Command Center on port 8000.
"""

import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sample_data.seed_db import seed_database
from sample_data.generate_samples import generate_crowd_image, generate_traffic_image, generate_fire_image, generate_surveillance_video


def main():
    print("=" * 72)
    print("               FALCON EYE — COMMAND CENTER INITIALIZATION")
    print("      AI-POWERED SMART PUBLIC SAFETY & EMERGENCY INTELLIGENCE")
    print("=" * 72)

    # 1. Ensure database is initialized
    db_file = os.path.join(BASE_DIR, "data", "falcon_eye.db")
    if not os.path.exists(db_file):
        print("[*] Initializing SQLite database and seed records...")
        seed_database()

    # 2. Ensure sample media exists
    crowd_sample = os.path.join(BASE_DIR, "sample_data", "sample_crowd.jpg")
    if not os.path.exists(crowd_sample):
        print("[*] Generating synthetic sample surveillance footage...")
        generate_crowd_image()
        generate_traffic_image()
        generate_fire_image()
        generate_surveillance_video()

    print("\n[+] SYSTEM ONLINE & OPERATIONAL")
    print("    • Web Command Center:   http://localhost:8000")
    print("    • Swagger API Docs:     http://localhost:8000/docs")
    print("    • Streamlit Dashboard:  streamlit run streamlit_app.py")
    print("    • 9-Stage Demo Button:  Available in Command Center Sidebar")
    print("=" * 72 + "\n")

    # Launch Uvicorn on 0.0.0.0 (allows localhost, 127.0.0.1, and local Wi-Fi access)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
