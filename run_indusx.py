import os
import sys
import webbrowser
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    print("=" * 72)
    print(" INDUS-X | Industrial Quality Intelligence & Resolution Platform")
    print(" Architecture: See -> Verify -> Trace -> Decide -> Act -> Learn")
    print(" Governance: 'Autonomous where safe. Human-controlled where consequential.'")
    print("=" * 72)
    print("\n[+] Initializing Database & Provenance Ledger...")
    
    from app.core.database import init_db
    init_db()
    print("[✓] SQLite Database & Seed Data Loaded.")
    print("[✓] Append-Only Provenance Hash Chain Genesis Block Anchored.")
    print("[✓] 4 Industrial Scenarios Loaded (Baseline, Missing Bolt, Wrong Part, Surface Crack).")
    print("[✓] Closed-Loop MQTT Floor Containment Initialized.")
    print("[✓] SLA Reasoning Contract Agent Initialized (MSA-2026-09).")
    print("[✓] ISO 2859-1 Switching Engine Active.")

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    print(f"\n[🚀] Launching INDUS-X Command Center at: {url}")
    print("[*] Serving API endpoints at /api and static UI at /")
    print("Press CTRL+C to stop.\n")

    # Launch uvicorn server
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=False, app_dir=str(backend_dir))

if __name__ == "__main__":
    main()

