# INDUS-X — Industrial Quality Intelligence & Resolution Platform

> **Track Alignment:** ⚙️ Smart Industry & Automation (with Embedded Governance & FinTech Liability Resolution)  
> **Core Lifecycle:** See ➔ Verify ➔ Trace ➔ Decide ➔ Act ➔ Learn  
> **Governance Mantra:** *"Autonomous where safe. Human-controlled where consequential."*

---

## 🚀 Quick Start (One Command)

Launch the complete application (FastAPI backend + 4-Quadrant Industrial UI):

```bash
python run_indusx.py
```

Then open your browser at:
👉 **`http://127.0.0.1:8000`**

---

## 🏛️ End-to-End System Architecture

INDUS-X implements the full 8-layer industrial quality operating system:

| Layer | Component | Functionality |
| :--- | :--- | :--- |
| **Layer 1** | `scenario_simulator.py` | Multi-defect industrial test bench with 4 scenarios (Pass, Missing Bolt, Wrong Nut, Crack) + angle/lighting perturbations |
| **Layer 2** | `reference_grid.py` | Geometric CAD/BOM tolerance verification solving the "detecting absence" paradox |
| **Layer 3** | `consolidator.py` | 4-Gate incident consolidation (ByteTrack, IoU > 0.5, 5-frame persistence, peak sharpness selection) calculating 96.3% noise reduction |
| **Layer 4** | `provenance.py` | Append-only SHA-256 cryptographic hash chain with live ledger verification and interactive tamper simulator |
| **Layer 5** | `traceability.py` | Blast-radius resolver mapping frame defect ➔ Workstation ➔ Batch B-042 ➔ Vendor-X ➔ Clause 4.2 ➔ $12,532 Net Cost Savings |
| **Layer 6A**| `automation.py` | Closed-loop industrial floor containment (simulated MQTT payload: Diverter Arm #03 pulse) |
| **Layer 6B**| `sla_agent.py` | Contextual SLA Reasoning Agent reading MSA-2026-09 Clause 4.2 to generate structured liability dossier & NCR |
| **Layer 7** | `governance.py` | 3-Tier Risk-Aware Governance Gate (Tier 1 Auto ➔ Tier 2 QE Approve ➔ Tier 3 PM Authorize) |
| **Layer 8** | `supplier_intelligence.py` | FMEA volume-normalized risk scoring (78/100) + ISO 2859-1 switching to Tightened Pre-Line Audit II + Operator feedback loop |

---

## 🎯 3-Minute Demo Choreography for Judges

1. **Scenario 0 (Baseline Pass):** Click `[0: Pass]` ➔ click `[Execute Test Run]`. Show that the reference grid confirms all 4 bolts present with 0 false alarms.
2. **Scenario 1 (Structural Absence):** Click `[1: Missing Bolt]` ➔ click `[Execute Test Run]`.
   - Watch the CAD reference overlay flag `Slot C [ABSENT]`.
   - Watch Quadrant 2 deduplicate 23–27 camera frames into **1 consolidated record (QI-0041)** with **95.7%+ noise reduction**.
   - Watch the append-only SHA-256 hash block seal in real-time.
   - Watch the closed-loop diverter arm pulse.
3. **Traceability & Cost Calculation:**
   - Look at Quadrant 3: 388 in-flight units at risk ➔ **$12,532 Net Cost Savings**.
   - Review the SLA Contract Dossier citing MSA-2026-09 Clause 4.2 (0.5% AQL breach).
4. **Role-Based Governance Gate:**
   - Switch role to `Operator`: show that `[Approve Quarantine]` is locked.
   - Switch role to `Quality Engineer`: click `[Approve Quarantine & NCR]` to sign the action into the immutable Chain of Custody.
5. **Live Tamper Demonstration:**
   - Click `[Simulate DB Tamper]` in Quadrant 2.
   - Watch the system instantly detect `INTEGRITY BREACH DETECTED AT BLOCK #1` and turn the badge bright red!
   - Click `[Reset / Recalibrate Chain]` to restore ledger integrity.
6. **Supplier Intelligence & ISO 2859-1:**
   - Show Quadrant 4: Vendor-X normalized risk score is 78.0/100 (FMEA weighted).
   - Show that ISO 2859-1 automatically escalates upcoming Batch B-043 to **Tightened Pre-Line Audit II**.
   - Submit operator feedback `[✓ Correct]` to close the loop on model accuracy.

