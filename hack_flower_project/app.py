"""Streamlit dashboard for SmartRoad AI — Civic Road Safety & Municipal Infrastructure Portal."""

from pathlib import Path
import hashlib
import hmac
import os
import tempfile
from datetime import date, timedelta

import cv2
import numpy as np
import streamlit as st

from smartroad import auto_detect_models, extract_media_telemetry, evaluate_sla
from smartroad.pipeline import RoadAnalyzer
from smartroad.reporting import (
    IncidentDatabase,
    STATUSES,
    export_incidents,
    generate_pdf_report,
    record_image_hazard_incidents,
)
from smartroad.safety import PEOPLE, VEHICLES, is_hazard_label

# ────────────────────────────────────────────────────────────────
# Page configuration & Modern Dark Theme Styling
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartRoad AI | Civic Safety & PWD Infrastructure Portal",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Theme & Layout styling */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Main Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0b192c 0%, #1e3e62 50%, #000000 100%);
        border: 1px solid #1f4068;
        padding: 1.6rem 2.2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #58a6ff, #38d9a9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-banner p {
        margin: 0.4rem 0 0 0;
        color: #8b949e;
        font-size: 1.0rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        text-align: center;
        color: #e6edf3;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    .metric-card .value {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.35rem;
    }
    .metric-vehicle .value { color: #3fb950; }
    .metric-person .value { color: #58a6ff; }
    .metric-hazard .value { color: #f85149; }
    .metric-plate .value { color: #39c5bb; }
    .metric-risk .value { color: #d29922; }
    .metric-track .value { color: #bc8cff; }

    /* Citizen Receipt Card */
    .receipt-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95), rgba(13, 17, 23, 0.95));
        border: 1px solid #238636;
        border-radius: 12px;
        padding: 1.3rem 1.6rem;
        margin: 1rem 0;
        box-shadow: 0 6px 18px rgba(35, 134, 54, 0.18);
    }
    .receipt-card h3 {
        color: #3fb950;
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }

    /* Workflow Stage Progress */
    .workflow-bar {
        display: flex;
        align-items: center;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.2rem;
        font-size: 0.85rem;
    }
    .workflow-step {
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-weight: 600;
    }
    .workflow-step.active {
        background: #1f6feb;
        color: #ffffff;
    }
    .workflow-step.completed {
        background: rgba(56, 185, 80, 0.2);
        color: #3fb950;
    }
    .workflow-step.pending {
        color: #8b949e;
    }
    .workflow-arrow {
        margin: 0 0.5rem;
        color: #8b949e;
    }

    /* Severity badges */
    .badge-critical {
        background-color: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid #f85149;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid #d29922;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-moderate {
        background-color: rgba(88, 166, 255, 0.2);
        color: #58a6ff;
        border: 1px solid #58a6ff;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: rgba(63, 185, 80, 0.2);
        color: #3fb950;
        border: 1px solid #3fb950;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Event cards */
    .event-high {
        background: linear-gradient(90deg, rgba(248, 81, 73, 0.18), transparent);
        border-left: 4px solid #f85149;
        padding: 0.7rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
    }
    .event-warn {
        background: linear-gradient(90deg, rgba(210, 153, 34, 0.18), transparent);
        border-left: 4px solid #d29922;
        padding: 0.7rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
    }

    /* Notification alert styles */
    .notif-critical {
        background: rgba(248, 81, 73, 0.12);
        border-left: 4px solid #f85149;
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 0.95rem;
        margin-bottom: 0.6rem;
    }
    .notif-warning {
        background: rgba(210, 153, 34, 0.12);
        border-left: 4px solid #d29922;
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 0.95rem;
        margin-bottom: 0.6rem;
    }
    .notif-info {
        background: rgba(88, 166, 255, 0.12);
        border-left: 4px solid #58a6ff;
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 0.95rem;
        margin-bottom: 0.6rem;
    }
    .notif-success {
        background: rgba(63, 185, 80, 0.12);
        border-left: 4px solid #3fb950;
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 0.95rem;
        margin-bottom: 0.6rem;
    }

    .workflow-step.rejected {
        background: rgba(248, 81, 73, 0.25);
        color: #f85149;
    }

    /* Status indicators */
    .status-loaded { color: #3fb950; font-weight: 600; }
    .status-missing { color: #f85149; font-weight: 600; }

    /* Citizen & MCD Two-Way SMS styles */
    .sms-container {
        background: #0f141c;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        max-height: 420px;
        overflow-y: auto;
    }
    .sms-bubble-mcd {
        background: linear-gradient(135deg, #162447 0%, #1f4068 100%);
        border: 1px solid #58a6ff;
        color: #e6edf3;
        border-radius: 12px 12px 12px 3px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .sms-bubble-meta {
        font-size: 0.76rem;
        color: #8b949e;
        margin-top: 0.35rem;
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 0.3rem;
    }
    .geo-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(88, 166, 255, 0.15);
        border: 1px solid #58a6ff;
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# App Banner
# ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>🚦 SmartRoad AI</h1>
    <p>Civic Road Safety, Defect Deduplication, Vehicle Tracking &amp; Municipal Work-Order Management</p>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# Sidebar — Model Settings & Live Health Check
# ────────────────────────────────────────────────────────────────
detected = auto_detect_models()

with st.sidebar:
    st.header("⚙️ Model Configuration")
    model = st.text_input(
        "YOLOv8 Base Weights",
        value="yolov8n.pt",
        help="Standard COCO weights for vehicles, bicycles, pedestrians, traffic signs.",
    )
    hazard_default = detected.get("hazard_model") or ""
    hazard_model = st.text_input(
        "Road-Hazard Weights",
        value=hazard_default,
        help="Specialized detector for potholes, construction zones, debris, sand.",
    )
    plate_default = detected.get("plate_model") or ""
    plate_model = st.text_input(
        "License-Plate Weights",
        value=plate_default,
        help="Detector for vehicle number plates passed into OCR.",
    )
    confidence = st.slider("Detection Confidence", 0.05, 0.95, 0.25, 0.05)

    st.divider()
    st.subheader("📋 System Readiness")
    st.markdown(f"**Main YOLO:** <span class='status-loaded'>✓ {Path(model).name}</span>", unsafe_allow_html=True)
    if hazard_model and Path(hazard_model).is_file():
        st.markdown(f"**Hazard Model:** <span class='status-loaded'>✓ Active ({Path(hazard_model).name})</span>", unsafe_allow_html=True)
    else:
        st.markdown("**Hazard Model:** <span class='status-missing'>✗ Not Detected</span>", unsafe_allow_html=True)
        st.caption("Road hazards and potholes won't be flagged without hazard weights.")

    if plate_model and Path(plate_model).is_file():
        st.markdown(f"**Plate Model:** <span class='status-loaded'>✓ Active ({Path(plate_model).name})</span>", unsafe_allow_html=True)
    else:
        st.markdown("**Plate Model:** <span class='status-missing'>✗ Not Detected</span>", unsafe_allow_html=True)
        st.caption("Plates will only be detected if present in base classes.")

# ────────────────────────────────────────────────────────────────
# Helper Rendering Utilities
# ────────────────────────────────────────────────────────────────
def _metric_card(label: str, value, css_class: str = "") -> str:
    return f"""<div class="metric-card {css_class}">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>"""

def _severity_badge(level: str) -> str:
    lvl = str(level).lower()
    cls = f"badge-{lvl}" if lvl in ("critical", "high", "moderate", "low") else "badge-moderate"
    return f"<span class='{cls}'>{str(level).upper()}</span>"

def _render_events(events, container):
    for event in events:
        cls = "event-high" if event.severity == "high" else "event-warn"
        icon = "🔴" if event.severity == "high" else "⚠️"
        container.markdown(
            f'<div class="{cls}"><strong>{icon} {event.title}</strong><br/>'
            f'<small>{event.details}</small></div>',
            unsafe_allow_html=True,
        )

# Instantiate Database
reports_dir = Path("data/reports")
reports_dir.mkdir(parents=True, exist_ok=True)
incident_db = IncidentDatabase(reports_dir / "reports.db")

@st.cache_resource
def get_analyzer(model_path, plate_path, confidence_value, hazard_path):
    return RoadAnalyzer(model_path or None, plate_path or None, confidence_value, hazard_path or None)

# ────────────────────────────────────────────────────────────────
# Municipal Authentication Helper
# ────────────────────────────────────────────────────────────────
def _municipal_login():
    """Gate municipal content using staff credentials with standard PWD defaults."""
    expected_user = os.environ.get("SMARTROAD_PWD_USERNAME", "pwd-staff")
    expected_password = os.environ.get("SMARTROAD_PWD_PASSWORD", "choose-your-own-password")

    if st.session_state.get("municipal_actor"):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"👷‍♂️ **Active Staff Session:** `{st.session_state['municipal_actor']}` (Public Works Division)")
        with col2:
            if st.button("🚪 Sign Out", use_container_width=True):
                del st.session_state["municipal_actor"]
                st.rerun()
        return st.session_state["municipal_actor"]

    st.markdown("""
    <div style="background: linear-gradient(135deg, #161b22, #0d1117); border: 1px solid #30363d; border-radius: 12px; padding: 1.4rem 1.8rem; margin: 1rem 0;">
        <h3 style="color: #58a6ff; margin: 0 0 0.5rem 0;">🔒 Municipal Staff Sign-In</h3>
        <p style="color: #8b949e; font-size: 0.92rem; margin: 0;">Authorized Public Works Department (PWD) &amp; Municipal Road Maintenance engineers only.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("municipal_login_form"):
        username = st.text_input("Staff Username", value="pwd-staff")
        password = st.text_input("Staff Password", type="password")
        st.caption("ℹ️ Demo Credentials: Username: `pwd-staff` | Password: `choose-your-own-password` (or customize via $env:SMARTROAD_PWD_USERNAME / $env:SMARTROAD_PWD_PASSWORD)")
        submitted = st.form_submit_button("Sign In to Municipal Portal", type="primary", use_container_width=True)

    if submitted:
        if hmac.compare_digest(username.encode("utf-8"), expected_user.encode("utf-8")) and hmac.compare_digest(password.encode("utf-8"), expected_password.encode("utf-8")):
            st.session_state["municipal_actor"] = username
            st.success("Authentication successful! Welcome to the Municipal Triage Portal.")
            st.rerun()
        else:
            st.error("Sign-in failed. Please verify your staff credentials.")
    return None

# ────────────────────────────────────────────────────────────────
# Municipal Portal Renderer
# ────────────────────────────────────────────────────────────────
def _render_municipal_portal(db: IncidentDatabase, actor: str):
    # Scan for any newly breached SLAs and generate alerts
    db.check_and_generate_sla_alerts()
    all_tickets = db.list()

    # ────────────────────────────────────────────────────────────
    # MCD Officer Notification Center
    # ────────────────────────────────────────────────────────────
    unread_count = db.unread_notification_count()
    notif_label = f"🔔 MCD Officer Notification Center ({unread_count} New Alert{'s' if unread_count != 1 else ''})" if unread_count > 0 else "🔔 MCD Officer Notification Center (All caught up)"
    with st.expander(notif_label, expanded=(unread_count > 0)):
        notifications = db.get_notifications(limit=20)
        n_col1, n_col2 = st.columns([4, 1])
        with n_col1:
            st.caption("Real-time municipal alerts: 24h/48h SLA breaches, critical hazard filings, and contractor work completion submissions requiring inspection.")
        with n_col2:
            if st.button("✓ Mark All as Read", key="btn_mark_all_read", use_container_width=True):
                db.mark_all_notifications_read()
                st.rerun()

        if not notifications:
            st.info("No active notifications at this time.")
        else:
            for n in notifications:
                cat_icon = "🚨" if n["category"] == "CRITICAL_HAZARD" else ("⚠️" if n["category"] == "SLA_BREACH" else ("👷" if n["category"] == "WORK_SUBMITTED" else ("❌" if n["category"] == "REWORK_REQUIRED" else "🏆")))
                read_badge = " • <span style='color:#f85149; font-weight:700;'>UNREAD</span>" if not n["is_read"] else ""
                st.markdown(f"""
                <div class="notif-{n['severity']}">
                    <strong>{cat_icon} {n['title']}</strong> &nbsp; <small style="color:#8b949e">{n['created_at']}{read_badge}</small><br/>
                    <span style="font-size:0.9rem; color:#e6edf3;">{n['message']}</span>
                </div>
                """, unsafe_allow_html=True)

    # Administrative maintenance expander
    with st.expander("🛠️ Administrative Tools & Database Maintenance"):
        st.write("Clean up duplicate test records or review system status.")
        if st.button("🧹 Prune Legacy Duplicate Test Records"):
            pruned = db.prune_legacy_duplicates()
            st.success(f"Cleaned up {pruned} repetitive test ticket(s). Database is now synchronized!")
            st.rerun()

    # Executive KPI Cards (Enhanced for MCD)
    total_inc = len(all_tickets)
    crit_inc = sum(i["severity"] in ("Critical", "High") for i in all_tickets)
    new_inc = sum(i["status"] == "New Submission" for i in all_tickets)
    disp_inc = sum(i["status"] == "Work-Order Dispatched" for i in all_tickets)
    review_inc = sum(i["status"] == "Work Completed - Awaiting Inspection" for i in all_tickets)
    closed_inc = sum(i["status"] in ("MCD Inspected & Closed", "Repaired & Closed") for i in all_tickets)

    p1, p2, p3, p4, p5, p6 = st.columns(6)
    p1.markdown(_metric_card("Total Defects", total_inc), unsafe_allow_html=True)
    p2.markdown(_metric_card("Critical / High", crit_inc, "metric-hazard"), unsafe_allow_html=True)
    p3.markdown(_metric_card("New Queue", new_inc, "metric-risk"), unsafe_allow_html=True)
    p4.markdown(_metric_card("In Progress", disp_inc, "metric-track"), unsafe_allow_html=True)
    p5.markdown(_metric_card("Awaiting Inspection", review_inc, "metric-plate"), unsafe_allow_html=True)
    p6.markdown(_metric_card("Certified Closed", closed_inc, "metric-vehicle"), unsafe_allow_html=True)

    st.markdown("---")

    # Filter Toolbar
    f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
    sev = f1.selectbox("Filter by Severity", ["All", "Critical", "High", "Moderate", "Low"])
    status = f2.selectbox("Filter by Workflow Status", ["All", *STATUSES])
    duplicates = f3.selectbox("Filter Repeat Reports", ["All", "Repeat Flagged Only", "Unique / Original Only"])
    query = f4.text_input("Search Ticket, Hazard, Road, Area, or Landmark", placeholder="e.g. MG Road, Pothole, WO-2026…")

    filtered = [
        t for t in all_tickets
        if (sev == "All" or t["severity"] == sev)
        and (status == "All" or t["status"] == status)
        and (duplicates == "All" or (bool(t.get("duplicate_of")) == (duplicates == "Repeat Flagged Only")))
        and (not query or any(
            query.casefold() in (t.get(k) or "").casefold()
            for k in ("ticket_id", "hazard_type", "road_name", "area", "landmark", "assigned_to", "work_order_ref")
        ))
    ]

    st.subheader(f"📋 Defect Triage Queue ({len(filtered)} matching tickets)")

    if not filtered:
        st.info("No tickets currently match the selected filters.")
        return

    # Filtered Exports — strictly export only `filtered` rows!
    a, b, c = st.columns(3)
    try:
        pdf_bytes = generate_pdf_report(filtered)
        a.download_button(
            f"📄 Download PDF Audit ({len(filtered)} tickets)",
            pdf_bytes,
            file_name="PWD_Road_Defect_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as exc:
        a.error(f"PDF export error: {exc}")

    b.download_button(
        f"📊 Export Filtered CSV ({len(filtered)} rows)",
        export_incidents(filtered, "csv"),
        file_name="smartroad_incidents.csv",
        mime="text/csv",
        use_container_width=True,
    )
    c.download_button(
        f"💾 Export Filtered JSON ({len(filtered)} items)",
        export_incidents(filtered, "json"),
        file_name="smartroad_incidents.json",
        mime="application/json",
        use_container_width=True,
    )

    st.dataframe([
        {
            "Ticket ID": t["ticket_id"],
            "Hazard": t["hazard_type"],
            "Severity": t["severity"],
            "Score": f"{t['priority_score']}/100",
            "Location": " / ".join(filter(None, [t.get("road_name"), t.get("area"), t.get("landmark")])) or "Not specified",
            "Status": t["status"],
            "SLA Countdown": evaluate_sla(t.get("due_date"), t.get("status"), t.get("closed_at"))["badge"],
            "Due Date": t.get("due_date", "")[:10] if t.get("due_date") else "—",
            "Assigned To": t.get("assigned_to") or "—",
            "Citizen Contact": t.get("citizen_phone") or "—",
            "Geo Source": t.get("geo_source") or "—",
            "Repeat Flag": t.get("duplicate_of") or "Original",
        }
        for t in filtered
    ], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🔎 Detailed Incident Dossier & Action Panel")

    ticket_ids = [t["ticket_id"] for t in filtered]
    selected_ticket = st.selectbox("Select Ticket to Inspect & Update", ticket_ids)
    item = next(t for t in filtered if t["ticket_id"] == selected_ticket)

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### 📸 Visual Evidence Dossier")
        snap = item.get("snapshot_path")
        crop = item.get("crop_path")
        clip = item.get("clip_path")
        closure = item.get("closure_evidence_path")

        if snap and Path(snap).is_file():
            st.image(snap, caption="Annotated Wide-Angle Evidence Snapshot", use_container_width=True)

        c1, c2 = st.columns(2)
        if crop and Path(crop).is_file():
            c1.image(crop, caption="High-Res Defect Cutout", use_container_width=True)
        if clip and Path(clip).is_file():
            c2.video(clip)

        if closure and Path(closure).is_file():
            st.markdown("#### 👷 Contractor Work Completion Evidence")
            st.image(closure, caption="Contractor Repair Verification Photo", use_container_width=True)

        if item.get("latitude") is not None and item.get("longitude") is not None:
            st.markdown("#### 🗺️ Defect Geo-Location (GIS Map)")
            st.map(data=[{"lat": item["latitude"], "lon": item["longitude"]}], zoom=15)

    with right:
        st.markdown("#### 📋 Incident Specifications & SLA Tracking")
        st.markdown(f"**Ticket ID:** `{item['ticket_id']}` &nbsp;|&nbsp; **Category:** `{item['hazard_type']}`")
        st.markdown(f"**Severity:** {_severity_badge(item['severity'])} &nbsp; **Priority Score:** `{item['priority_score']}/100`", unsafe_allow_html=True)
        
        sla_eval = evaluate_sla(item.get("due_date"), item.get("status"), item.get("closed_at"))
        st.markdown(f"**SLA Benchmark:** `{sla_eval['badge']}` &nbsp;|&nbsp; **Due Date:** `{item.get('due_date') or 'Unset'}`")
        st.caption(f"Reasoning: {item.get('severity_reason') or 'Heuristic image-space estimation.'}")

        loc_str = " / ".join(filter(None, [item.get("road_name"), item.get("area"), item.get("landmark")])) or "Not provided"
        geo_badge = f"&nbsp;<span class='geo-pill'>{item.get('geo_source') or 'MANUAL_INPUT'}</span>" if item.get("geo_source") else ""
        st.markdown(f"**Location:** {loc_str}{geo_badge}", unsafe_allow_html=True)
        if item.get("latitude") is not None and item.get("longitude") is not None:
            st.markdown(f"**Coordinates:** `{item['latitude']:.6f}, {item['longitude']:.6f}`")

        c_phone = item.get("citizen_phone") or "Not provided"
        c_name = item.get("citizen_name") or "Anonymous"
        st.markdown(f"**Citizen Contact:** `{c_phone}` &nbsp;|&nbsp; **Reporter:** `{c_name}`")
        st.markdown(f"**Lane Position:** `{item['lane_position']} Lane` &nbsp;|&nbsp; **Video Time:** `{item['video_timestamp']:.2f}s`")
        st.markdown(f"**Confidence:** `{item['max_confidence']:.1%}` &nbsp;|&nbsp; **Sightings:** `{item['observations']} frame(s)`")

        if item.get("duplicate_of"):
            st.warning(f"🔁 **Repeat Report Flag:** Associated with earlier incident `{item['duplicate_of']}`.")

        # Location Editor Expander for MCD Staff
        with st.expander("✏️ Update Incident Location & GIS Pin in MCD System", expanded=False):
            st.caption("MCD staff can refine or correct street address, ward, and GPS coordinates for field crews.")
            with st.form(f"mcd_update_loc_{selected_ticket}"):
                u_c1, u_c2, u_c3 = st.columns(3)
                u_road = u_c1.text_input("Road / Street Name", value=item.get("road_name") or "", key=f"uroad_{selected_ticket}")
                u_area = u_c2.text_input("City / Ward / Area", value=item.get("area") or "", key=f"uarea_{selected_ticket}")
                u_landmark = u_c3.text_input("Nearby Landmark", value=item.get("landmark") or "", key=f"uland_{selected_ticket}")
                u_g1, u_g2, u_g3 = st.columns(3)
                u_lat_str = u_g1.text_input("Latitude", value=str(item.get("latitude")) if item.get("latitude") is not None else "", key=f"ulat_{selected_ticket}")
                u_lon_str = u_g2.text_input("Longitude", value=str(item.get("longitude")) if item.get("longitude") is not None else "", key=f"ulon_{selected_ticket}")
                u_src = u_g3.selectbox("Geo-Source Verification", ["MCD_OFFICER_VERIFIED", "MUNICIPAL_GIS_SURVEY", "LIVE_DEVICE_GPS", "EXIF_METADATA", "MANUAL_INPUT"], index=0, key=f"usrc_{selected_ticket}")
                u_note = st.text_input("Location Revision Note (Optional)", placeholder="e.g. Corrected to exact junction near pillar 14", key=f"unote_{selected_ticket}")
                save_loc_btn = st.form_submit_button("💾 Save Updated Location", type="primary", use_container_width=True)
            if save_loc_btn:
                try:
                    n_lat = float(u_lat_str.strip()) if u_lat_str.strip() else None
                    n_lon = float(u_lon_str.strip()) if u_lon_str.strip() else None
                    db.update_location(
                        selected_ticket,
                        road_name=u_road,
                        area=u_area,
                        landmark=u_landmark,
                        latitude=n_lat,
                        longitude=n_lon,
                        geo_source=u_src,
                        actor=actor,
                        note=u_note.strip()
                    )
                    st.success("Incident location updated successfully in MCD records!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Error updating location: {err}")

        # Citizen Communication & SMS Dispatch Expander
        with st.expander("📲 Two-Way Citizen Communication & Outward SMS Dispatch", expanded=False):
            st.markdown(f"**Registered Citizen Phone:** `{c_phone}` &nbsp;|&nbsp; **Reporter:** `{c_name}`")
            
            notifs = db.get_citizen_notifications(selected_ticket)
            if notifs:
                st.markdown("##### 📜 Outward Notification History for this Ticket")
                for n in notifs:
                    st.markdown(f"""
                    <div class="sms-bubble-mcd">
                        <strong>{n['title']}</strong><br/>
                        {n['message']}
                        <div class="sms-bubble-meta">
                            <span>Channel: {n.get('channel', 'SMS_GATEWAY')} • Status: {n.get('delivery_status', 'DELIVERED')}</span>
                            <span>{n['created_at']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No outward SMS notifications sent for this ticket yet.")

            st.markdown("##### 📤 Send Direct SMS / Official Notice to Citizen")
            with st.form(f"direct_sms_form_{selected_ticket}"):
                target_phone = st.text_input("Citizen Mobile Number", value=item.get("citizen_phone") or "", placeholder="e.g. +91 98765 43210", key=f"tphone_{selected_ticket}")
                preset = st.selectbox("Quick Notification Template", [
                    "Custom Message",
                    "Crew is on site conducting road milling and asphalt leveling.",
                    "Temporary cold patch applied for immediate safety. Full resurfacing scheduled.",
                    "Could you please clarify the exact landmark or nearby building to help our crew locate this defect?",
                    "Road repair completed and cured. Quality audit certified.",
                    "Road temporarily cordoned off for hot-mix paving. Expected open in 3 hours."
                ], key=f"preset_{selected_ticket}")
                default_msg = "" if preset == "Custom Message" else preset
                sms_body = st.text_area("SMS Message Body", value=default_msg, placeholder="Type official update message for citizen...", key=f"sbody_{selected_ticket}")
                send_sms_btn = st.form_submit_button("📤 Send SMS via MCD Gateway", type="primary", use_container_width=True)
            if send_sms_btn:
                if not target_phone.strip():
                    st.error("Please provide a valid mobile number.")
                elif not sms_body.strip():
                    st.error("Please enter a message to send.")
                else:
                    try:
                        db.send_citizen_notification(selected_ticket, target_phone.strip(), sms_body.strip(), sender_actor=actor)
                        st.success(f"SMS notification successfully dispatched to {target_phone.strip()} via MCD Gateway!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error dispatching notification: {exc}")

        st.divider()

        # Step-by-Step MCD Municipal Workflow Management
        curr_status = item["status"]
        st.markdown(f"#### ⚡ MCD Municipal Workflow: Current Status — **{curr_status}**")

        # Visual workflow stepper for the 5 MCD stages
        is_closed_status = curr_status in ("MCD Inspected & Closed", "Repaired & Closed")
        is_rework = curr_status == "Rejected - Rework Required"
        
        s1 = "completed" if curr_status not in ("New Submission",) else "active"
        s2 = "completed" if curr_status not in ("New Submission", "Verified") else ("active" if curr_status == "Verified" else "pending")
        s3 = "completed" if curr_status not in ("New Submission", "Verified", "Work-Order Dispatched") else ("active" if curr_status == "Work-Order Dispatched" else "pending")
        s4 = "rejected" if is_rework else ("completed" if is_closed_status else ("active" if curr_status == "Work Completed - Awaiting Inspection" else "pending"))
        s5 = "completed" if is_closed_status else "pending"

        s4_label = "4. Rework Required" if is_rework else "4. Awaiting Inspection"

        st.markdown(f"""
        <div class="workflow-bar">
            <span class="workflow-step {s1}">1. New</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s2}">2. Verified</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s3}">3. Dispatched</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s4}">{s4_label}</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s5}">5. Certified Closed</span>
        </div>
        """, unsafe_allow_html=True)

        # Stage 1: New Submission -> Verified
        if curr_status == "New Submission":
            st.markdown("##### Step 1: Technical Review & Defect Verification")
            st.caption("Verify that the photo/video shows a genuine defect requiring MCD municipal intervention.")
            with st.form(f"verify_form_{selected_ticket}"):
                verify_note = st.text_input("Staff Verification Note (Required)", placeholder="e.g. Confirmed severe pothole depth > 4cm on active lane", key=f"vn_{selected_ticket}")
                submitted_verify = st.form_submit_button("✓ Mark Verified", type="primary", use_container_width=True)
            if submitted_verify:
                if not verify_note.strip():
                    st.error("Verification requires a brief staff review note.")
                else:
                    try:
                        db.update_status(selected_ticket, "Verified", actor=actor, note=verify_note.strip())
                        st.success(f"Ticket {selected_ticket} verified!")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Stage 2: Verified -> Work-Order Dispatched
        elif curr_status in ("Verified", "Rejected - Rework Required"):
            st.markdown("##### Step 2: Assign Work-Order & Dispatch Maintenance Crew")
            if is_rework:
                st.error(f"⚠️ Re-Dispatch Required. Rejection Reason: {item.get('rejection_reason') or 'Substandard patch'}")
            st.caption("Assign this defect to a contractor with an SLA completion due date.")
            with st.form(f"dispatch_form_{selected_ticket}"):
                c_a, c_b = st.columns(2)
                assignee = c_a.text_input("Assigned Crew / Supervisor *", value=item.get("assigned_to") or "MCD Maintenance Zone North", key=f"as_{selected_ticket}")
                work_ref = c_b.text_input("Work-Order Reference # *", value=item.get("work_order_ref") or f"WO-MCD-{selected_ticket[-4:]}", key=f"wo_{selected_ticket}")
                c_c, c_d = st.columns(2)
                default_due = date.today() + (timedelta(days=1) if item["severity"] == "Critical" else (timedelta(days=2) if item["severity"] == "High" else timedelta(days=5)))
                due_val = c_c.date_input("Target Completion Due Date *", value=default_due, key=f"dd_{selected_ticket}")
                contractor = c_d.text_input("Contractor / Agency", value=item.get("contractor") or "Delhi Asphalt Infra Works Ltd.", key=f"ct_{selected_ticket}")
                dispatch_notes = st.text_area("Dispatch Notes & Instructions", placeholder="e.g. Priority repair required within SLA using hot-mix asphalt.", key=f"dn_{selected_ticket}")
                submitted_dispatch = st.form_submit_button("🚀 Confirm Dispatch & Assign Work-Order", type="primary", use_container_width=True)
            if submitted_dispatch:
                if not assignee.strip() or not work_ref.strip():
                    st.error("Both Assigned Crew and Work-Order Reference are required for dispatch.")
                else:
                    try:
                        db.update_status(
                            selected_ticket,
                            "Work-Order Dispatched",
                            actor=actor,
                            note=dispatch_notes.strip() or "Dispatched to maintenance unit",
                            assigned_to=assignee.strip(),
                            work_order_ref=work_ref.strip(),
                            due_date=due_val.isoformat(),
                            contractor=contractor.strip(),
                        )
                        st.success(f"Work-Order {work_ref} dispatched to {assignee}!")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Stage 3: Work-Order Dispatched -> Work Completed - Awaiting Inspection
        elif curr_status == "Work-Order Dispatched":
            st.markdown("##### Step 3: Contractor Work Completion Submission")
            st.markdown(f"**Current Assignee:** `{item.get('assigned_to')}` &nbsp;|&nbsp; **WO #:** `{item.get('work_order_ref')}`")
            st.markdown(f"**Target Due Date:** `{item.get('due_date')}` &nbsp;|&nbsp; **Contractor:** `{item.get('contractor')}`")
            st.caption("Contractor submits post-repair evidence photo for MCD Officer inspection and quality sign-off.")

            with st.form(f"contractor_submit_form_{selected_ticket}"):
                close_note = st.text_area("Contractor Completion Notes *", placeholder="e.g. Pothole filled with dense asphalt, rolled and compacted level with roadway. Traffic restored.", key=f"cn_{selected_ticket}")
                close_file = st.file_uploader("Upload Repair Completion Evidence Photo *", type=["jpg", "jpeg", "png", "webp"], key=f"cf_{selected_ticket}")
                submitted_work = st.form_submit_button("📤 Submit Repair for MCD Officer Inspection", type="primary", use_container_width=True)
            if submitted_work:
                if not (close_note.strip() or close_file):
                    st.error("Completion submission requires repair notes and an evidence photo.")
                else:
                    evidence_path = db.save_closure_evidence(selected_ticket, close_file.getvalue(), Path(close_file.name).suffix) if close_file else None
                    try:
                        db.update_status(
                            selected_ticket,
                            "Work Completed - Awaiting Inspection",
                            actor=f"Contractor ({item.get('contractor') or 'Field Crew'})",
                            note=close_note.strip() or "Contractor submitted repair evidence",
                            closure_evidence_path=evidence_path,
                        )
                        st.success(f"Repair submitted! MCD Officer notified for inspection on Ticket {selected_ticket}.")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Stage 4: Work Completed - Awaiting Inspection -> MCD Inspected & Closed OR Rejected
        elif curr_status == "Work Completed - Awaiting Inspection":
            st.markdown("##### Step 4: MCD Officer Inspection & Quality Sign-Off")
            st.info("🔎 Contractor has submitted repair work. Inspect the before-and-after evidence photos on the left before certifying.")

            st.markdown(f"**Submitted Notes:** {item.get('closure_notes') or 'No notes provided'}")

            ins_col1, ins_col2 = st.columns(2)
            with ins_col1:
                with st.form(f"approve_form_{selected_ticket}"):
                    officer_notes = st.text_input("Officer Certification Note", value="Inspected on site. Patch compacted level and sealed.", key=f"on_{selected_ticket}")
                    approve_btn = st.form_submit_button("✅ Approve & Certify Closed", type="primary", use_container_width=True)
                if approve_btn:
                    try:
                        db.update_status(
                            selected_ticket,
                            "MCD Inspected & Closed",
                            actor=actor,
                            note=officer_notes.strip() or "Quality inspected and certified closed by MCD officer",
                        )
                        st.success(f"Ticket {selected_ticket} certified closed by {actor}!")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

            with ins_col2:
                with st.form(f"reject_form_{selected_ticket}"):
                    rejection_reason = st.text_input("Rejection / Rework Reason", placeholder="e.g. Edges unsealed, cold mix used, uneven level", key=f"rr_{selected_ticket}")
                    reject_btn = st.form_submit_button("❌ Reject & Demand Rework", type="secondary", use_container_width=True)
                if reject_btn:
                    if not rejection_reason.strip():
                        st.error("Rejection requires specifying a defect rework reason.")
                    else:
                        try:
                            db.update_status(
                                selected_ticket,
                                "Rejected - Rework Required",
                                actor=actor,
                                note=rejection_reason.strip(),
                                rejection_reason=rejection_reason.strip(),
                            )
                            st.warning(f"Repair rejected! Contractor notified for rework on Ticket {selected_ticket}.")
                            st.rerun()
                        except ValueError as err:
                            st.error(str(err))

        # Stage 5: Closed
        elif is_closed_status:
            st.success("🎉 This road defect has been inspected, approved, and formally closed in MCD records.")
            st.markdown(f"**Work-Order Reference:** `{item.get('work_order_ref')}`")
            st.markdown(f"**Assigned Crew:** `{item.get('assigned_to')}` &nbsp;|&nbsp; **Contractor:** `{item.get('contractor')}`")
            if item.get("inspected_by"):
                st.markdown(f"**Certified By:** `{item['inspected_by']}`")
            if item.get("closure_notes"):
                st.markdown(f"**Officer / Repair Notes:** {item['closure_notes']}")

        # Audit Trail Expander
        history = db.audit_history(selected_ticket)
        with st.expander(f"📜 Official Action & Audit Trail ({len(history)} events)", expanded=False):
            if history:
                st.dataframe([
                    {
                        "Timestamp": h["created_at"],
                        "Staff Member": h["actor"],
                        "Action": h["action"],
                        "Previous Status": h.get("old_value") or "—",
                        "New Status": h.get("new_value") or "—",
                        "Notes": h.get("note") or "—",
                    }
                    for h in history
                ], use_container_width=True, hide_index=True)
            else:
                st.caption("No audit history events recorded for this ticket yet.")

# ────────────────────────────────────────────────────────────────
# Citizen Real-Time Tracker & Two-Way SMS Portal Helper
# ────────────────────────────────────────────────────────────────
def _render_citizen_tracker(db: IncidentDatabase):
    """Citizen Complaint Tracking Portal & Live SMS Notifications Inbox."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #161b22, #0d1117); border: 1px solid #1f6feb; border-radius: 12px; padding: 1.2rem 1.6rem; margin-bottom: 1.2rem;">
        <h3 style="color: #58a6ff; margin: 0 0 0.4rem 0;">📱 Citizen Real-Time Complaint Tracker &amp; SMS Inbox</h3>
        <p style="color: #8b949e; font-size: 0.95rem; margin: 0;">Track the lifecycle of your reported road defects, view municipal inspection notes, contractor repair photos, and read all two-way SMS dispatch updates.</p>
    </div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        track_query = st.text_input("Enter Ticket ID or Registered Mobile Number", placeholder="e.g., PWD-HAZ-20261015-E4C183 or 9876543210", key="cit_track_q")
    with t_col2:
        st.write("")
        st.write("")
        find_btn = st.button("🔎 Track Complaint", type="primary", use_container_width=True)

    if track_query.strip():
        clean_q = track_query.strip().casefold()
        all_incidents = db.list()
        matched = [
            t for t in all_incidents
            if t["ticket_id"].casefold() == clean_q
            or (t.get("citizen_phone") and clean_q in t.get("citizen_phone", "").casefold())
        ]

        if not matched:
            st.warning(f"No defect reports found for '{track_query.strip()}'. Please check your ticket ID or mobile number.")
            return

        if len(matched) > 1:
            sel_label = st.selectbox(
                f"Found {len(matched)} matching reports. Select ticket to inspect:",
                [f"{t['ticket_id']} — {t['hazard_type']} at {t.get('road_name') or 'Unnamed road'} ({t['status']})" for t in matched],
                key="cit_track_select"
            )
            ticket_id_target = sel_label.split(" — ")[0]
            item = next(t for t in matched if t["ticket_id"] == ticket_id_target)
        else:
            item = matched[0]

        curr_status = item["status"]
        st.markdown(f"### 📋 Incident Report: `{item['ticket_id']}`")

        # 5-stage visual stepper
        is_closed_status = curr_status in ("MCD Inspected & Closed", "Repaired & Closed")
        is_rework = curr_status == "Rejected - Rework Required"
        s1 = "completed" if curr_status not in ("New Submission",) else "active"
        s2 = "completed" if curr_status not in ("New Submission", "Verified") else ("active" if curr_status == "Verified" else "pending")
        s3 = "completed" if curr_status not in ("New Submission", "Verified", "Work-Order Dispatched") else ("active" if curr_status == "Work-Order Dispatched" else "pending")
        s4 = "rejected" if is_rework else ("completed" if is_closed_status else ("active" if curr_status == "Work Completed - Awaiting Inspection" else "pending"))
        s5 = "completed" if is_closed_status else "pending"
        s4_label = "4. Rework Ordered" if is_rework else "4. Under Inspection"

        st.markdown(f"""
        <div class="workflow-bar">
            <span class="workflow-step {s1}">1. Registered</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s2}">2. Verified</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s3}">3. Dispatched</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s4}">{s4_label}</span>
            <span class="workflow-arrow">➔</span>
            <span class="workflow-step {s5}">5. Certified Closed</span>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("#### 📸 Evidence & Geo-Location")
            snap = item.get("snapshot_path")
            closure = item.get("closure_evidence_path")
            if snap and Path(snap).is_file():
                st.image(snap, caption="Original Hazard Snapshot", use_container_width=True)
            if closure and Path(closure).is_file():
                st.markdown("##### 👷 Contractor Repair Evidence")
                st.image(closure, caption="Contractor Work Completion Photo", use_container_width=True)
            if item.get("latitude") is not None and item.get("longitude") is not None:
                st.markdown("##### 🗺️ Geographic Location Pin")
                st.map(data=[{"lat": item["latitude"], "lon": item["longitude"]}], zoom=15)

        with col_right:
            st.markdown("#### 📊 Municipal Resolution Status")
            st.markdown(f"**Hazard Category:** `{item['hazard_type']}` &nbsp;|&nbsp; **Severity:** {_severity_badge(item['severity'])}", unsafe_allow_html=True)
            sla_eval = evaluate_sla(item.get("due_date"), item.get("status"), item.get("closed_at"))
            st.markdown(f"**Target SLA:** `{sla_eval['badge']}` &nbsp;|&nbsp; **Target Date:** `{item.get('due_date') or 'Pending Triage'}`")
            loc_str = " / ".join(filter(None, [item.get("road_name"), item.get("area"), item.get("landmark")])) or "Not provided"
            geo_badge = f"&nbsp;<span class='geo-pill'>{item.get('geo_source') or 'LIVE_DEVICE_GPS'}</span>" if item.get("geo_source") else ""
            st.markdown(f"**Road Location:** {loc_str}{geo_badge}", unsafe_allow_html=True)
            if item.get("latitude") is not None and item.get("longitude") is not None:
                st.markdown(f"**Coordinates:** `{item['latitude']:.6f}, {item['longitude']:.6f}`")

            st.markdown(f"**Assigned Contractor:** `{item.get('contractor') or 'Queued for Assignment'}`")
            if item.get("work_order_ref"):
                st.markdown(f"**Work-Order Reference:** `{item['work_order_ref']}`")
            if item.get("inspected_by"):
                st.markdown(f"**MCD Certifying Officer:** `{item['inspected_by']}`")
            if item.get("closure_notes"):
                st.markdown(f"**Repair / Certification Notes:** {item['closure_notes']}")

            st.markdown("---")
            st.markdown("#### 💬 Two-Way SMS Updates Sent to Your Phone")
            notifs = db.get_citizen_notifications(item["ticket_id"])
            if not notifs and item.get("citizen_phone"):
                notifs = db.get_citizen_notifications(item["citizen_phone"])

            if notifs:
                st.caption(f"Showing {len(notifs)} real-time SMS alert(s) sent from MCD Control Center:")
                for n in notifs:
                    st.markdown(f"""
                    <div class="sms-bubble-mcd">
                        <strong>🏛️ {n['title']}</strong><br/>
                        <span style="font-size:0.92rem;">{n['message']}</span>
                        <div class="sms-bubble-meta">
                            <span>📡 Gateway: {n.get('channel', 'SMS_GATEWAY')} • Status: {n.get('delivery_status', 'DELIVERED')}</span>
                            <span>{n['created_at']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No SMS notifications recorded yet. Real-time updates will appear here and via SMS as your report progresses.")

# ────────────────────────────────────────────────────────────────
# Top Navigation — Dual Portals
# ────────────────────────────────────────────────────────────────
portal_tabs = st.tabs([
    "🚗 Citizen Hazard Reporting Portal",
    "🏛️ Municipal & PWD Action Portal",
])

# ================================================================
# TAB 1: CITIZEN REPORTING PORTAL
# ================================================================
with portal_tabs[0]:
    with st.expander("📱 Track My Complaint & Real-Time Citizen SMS Updates", expanded=False):
        _render_citizen_tracker(incident_db)

    st.subheader("📢 Report Road Hazards & Infrastructure Defects")
    st.caption("Citizens, dashcam drivers, and commuters can submit photos or video footage. Defects are automatically deduplicated and submitted to municipal road maintenance teams.")

    # Location Information Section
    with st.expander("📍 Location & Reporter Contact Details (Recommended)", expanded=True):
        # Check if real-time GPS was captured from browser geolocation
        q_lat = st.query_params.get("live_lat")
        q_lon = st.query_params.get("live_lon")
        if q_lat and not st.session_state.get("cit_lat"):
            st.session_state["cit_lat"] = str(q_lat)
        if q_lon and not st.session_state.get("cit_lon"):
            st.session_state["cit_lon"] = str(q_lon)

        cp1, cp2 = st.columns(2)
        citizen_phone = cp1.text_input("Mobile / WhatsApp Number (for Live Two-Way SMS Updates) *", placeholder="e.g., 9876543210 or +91 98765 43210", key="cit_phone")
        citizen_name = cp2.text_input("Reporter Name (Optional)", placeholder="e.g., Ramesh Kumar", key="cit_name")

        c1, c2, c3 = st.columns(3)
        road_name = c1.text_input("Road / Street Name", placeholder="e.g., MG Road / Highway 48", key="cit_road")
        area = c2.text_input("City / Area", placeholder="e.g., Downtown / Sector 4", key="cit_area")
        landmark = c3.text_input("Nearby Landmark", placeholder="e.g., Near Metro Pillar 128", key="cit_landmark")
        g1, g2 = st.columns(2)
        default_lat = q_lat if q_lat else ""
        default_lon = q_lon if q_lon else ""
        latitude_text = g1.text_input("Latitude (GPS)", value=default_lat, placeholder="e.g., 28.6139", key="cit_lat")
        longitude_text = g2.text_input("Longitude (GPS)", value=default_lon, placeholder="e.g., 77.2090", key="cit_lon")

        # Real-Time Device Geolocation Button (HTML5 Geolocation API)
        st.components.v1.html("""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <button id="gps_btn" onclick="getLiveGPS()" style="
                    background: linear-gradient(135deg, #1f6feb, #238636);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 7px 14px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                ">
                    📡 Get Live Real-Time GPS (Device Sensor)
                </button>
                <span id="gps_status" style="margin-left: 10px; font-size: 0.82rem; color: #8b949e;"></span>
            </div>
            <script>
            function getLiveGPS() {
                var status = document.getElementById('gps_status');
                status.innerText = "Acquiring live satellite coordinates...";
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(pos) {
                        var lat = pos.coords.latitude.toFixed(6);
                        var lon = pos.coords.longitude.toFixed(6);
                        status.innerText = "✓ Coordinates: " + lat + ", " + lon;
                        try {
                            var parentUrl = new URL(window.parent.location.href);
                            parentUrl.searchParams.set("live_lat", lat);
                            parentUrl.searchParams.set("live_lon", lon);
                            window.parent.location.href = parentUrl.href;
                        } catch(e) {
                            prompt("Live Coordinates Acquired:", lat + ", " + lon);
                        }
                    }, function(err) {
                        status.innerText = "GPS Error: " + err.message;
                    }, { enableHighAccuracy: true, timeout: 8000 });
                } else {
                    status.innerText = "Geolocation not supported by browser.";
                }
            }
            </script>
        """, height=44)

    try:
        latitude = float(latitude_text) if latitude_text.strip() else None
        longitude = float(longitude_text) if longitude_text.strip() else None
        if (latitude is None) != (longitude is None):
            raise ValueError("Enter both latitude and longitude, or leave both blank.")
        if latitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Latitude must be between -90 and 90; longitude between -180 and 180.")
        location_error = None
    except ValueError as exc:
        latitude = longitude = None
        location_error = str(exc)

    if location_error:
        st.warning(location_error)

    uploaded = st.file_uploader(
        "Upload a road image or dashcam video",
        type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi", "mkv"],
        help="Upload clear photos of road defects or dashcam driving clips (up to 200MB).",
        key="cit_upload",
    )

    if uploaded:
        suffix = Path(uploaded.name).suffix.lower()
        file_bytes = uploaded.getvalue()
        source_hash = hashlib.sha256(file_bytes).hexdigest()

        # ─── MULTI-SOURCE GEOLOCATION RECONCILIATION ──────────
        import math
        telemetry = extract_media_telemetry(file_bytes, uploaded.name)
        exif_lat = telemetry.get("latitude")
        exif_lon = telemetry.get("longitude")
        has_exif = exif_lat is not None and exif_lon is not None
        has_live = bool(q_lat and q_lon)
        has_manual = bool(latitude_text.strip() and longitude_text.strip())

        geo_source = "MANUAL_INPUT"
        final_lat = latitude
        final_lon = longitude

        if has_exif and (has_live or has_manual):
            st.markdown("##### 📍 Multi-Source Geolocation Detected")
            loc_options = [
                f"📸 Embedded Camera GPS ({exif_lat:.5f}, {exif_lon:.5f})",
                f"📡 My Live Device Location ({float(q_lat or latitude or 0):.5f}, {float(q_lon or longitude or 0):.5f})",
                f"📝 Manual Street Location ({road_name or 'Road'} / {area or 'Area'})"
            ]
            chosen_loc = st.radio("This photo contains original camera metadata, but live/manual location was also provided. Choose target location:", loc_options, index=0, key="loc_choice_radio")
            if chosen_loc.startswith("📸"):
                final_lat, final_lon = exif_lat, exif_lon
                geo_source = "EXIF_METADATA"
            elif chosen_loc.startswith("📡"):
                final_lat = float(q_lat) if q_lat else latitude
                final_lon = float(q_lon) if q_lon else longitude
                geo_source = "LIVE_DEVICE_GPS"
            else:
                final_lat, final_lon = latitude, longitude
                geo_source = "MANUAL_INPUT"

            if has_live and exif_lat is not None and q_lat:
                try:
                    p1, p2 = math.radians(exif_lat), math.radians(float(q_lat))
                    dp = p2 - p1
                    dl = math.radians(float(q_lon) - exif_lon)
                    a = math.sin(dp / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2)**2
                    dist_km = (6_371_000 * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0, 1 - a)))) / 1000.0
                    if dist_km > 2.0:
                        st.warning(f"ℹ️ **Location Discrepancy Notice**: Photo capture position is **{dist_km:.1f} km away** from your device's live location. Report will be filed under: `{geo_source}`.")
                except Exception:
                    pass
        elif has_exif:
            final_lat, final_lon = exif_lat, exif_lon
            geo_source = "EXIF_METADATA"
            st.success(f"📍 **{telemetry['summary']}** — Auto-extracted from photo camera EXIF.")
        elif has_live:
            final_lat, final_lon = float(q_lat), float(q_lon)
            geo_source = "LIVE_DEVICE_GPS"
            st.info(f"📥 **Forwarded / Downloaded Media**: No embedded camera EXIF GPS found. Using your verified **Live Device GPS ({final_lat:.5f}, {final_lon:.5f})**.")
        elif has_manual:
            final_lat, final_lon = latitude, longitude
            geo_source = "MANUAL_INPUT"
            st.info(f"📥 **Forwarded / Downloaded Media**: Using manual coordinates **({final_lat:.5f}, {final_lon:.5f})**.")
        else:
            geo_source = "STREET_ADDRESS_ONLY"
            st.caption("ℹ️ Downloaded / Forwarded Media: No GPS coordinates provided. Defect will be logged by street/landmark.")

        latitude, longitude = final_lat, final_lon

        # ─── IMAGE SUBMISSION ──────────────────────────────────
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            analysis_key = hashlib.sha256(
                file_bytes + f"{model}|{hazard_model}|{plate_model}|{confidence}|{road_name}|{area}|{landmark}|{latitude}|{longitude}".encode()
            ).hexdigest()

            prior = incident_db.submission(source_hash)
            prior_incidents = incident_db.incidents_for_submission(source_hash)
            is_completed = bool(prior and prior.get("status") == "COMPLETED")
            is_failed = bool(prior and prior.get("status") == "FAILED")
            is_stale_proc = bool(prior and prior.get("status") == "PROCESSING")

            if location_error:
                st.info("Please correct the GPS coordinates above before proceeding.")
            else:
                if is_failed:
                    err_msg = prior.get("error_message") or "Interrupted before completion"
                    st.warning(f"⚠️ A previous processing attempt encountered an issue: {err_msg}. Incomplete data was cleaned up — ready to retry.")
                    btn_label = "🔄 Retry Image Analysis & File Report"
                    btn_type = "primary"
                elif is_stale_proc:
                    st.warning("⚠️ A previous processing attempt was interrupted or timed out. You can re-run analysis below.")
                    btn_label = "🔄 Retry Image Analysis"
                    btn_type = "primary"
                elif is_completed:
                    st.info(f"ℹ️ Analysis was previously completed for this image ({len(prior_incidents)} registered ticket(s)). You can review existing records below or re-analyze with updated model parameters.")
                    existing = prior_incidents or incident_db.legacy_incidents_for_filename(uploaded.name)
                    if existing:
                        st.markdown("#### 📋 Associated Municipal Incident Ticket(s)")
                        st.dataframe([
                            {
                                "Ticket ID": inc["ticket_id"],
                                "Hazard": inc["hazard_type"],
                                "Severity": inc["severity"],
                                "Priority Score": f"{inc['priority_score']}/100",
                                "Lane": inc["lane_position"],
                                "Status": inc["status"],
                                "Possible Repeat Of": inc.get("duplicate_of") or "Original",
                            }
                            for inc in existing
                        ], use_container_width=True, hide_index=True)

                        snap_file = existing[0].get("snapshot_path")
                        if snap_file and Path(snap_file).is_file():
                            st.image(snap_file, caption=f"Filed Evidence Snapshot ({uploaded.name})", use_container_width=True)
                    btn_label = "🔄 Re-Analyze Image & Overwrite Prior Report"
                    btn_type = "secondary"
                else:
                    btn_label = "🔎 Analyze Image & File Road Report"
                    btn_type = "primary"

                if st.button(btn_label, type=btn_type, key="analyze_image_submit"):
                    if not incident_db.claim_submission(
                        source_hash,
                        uploaded.name,
                        "image",
                        {
                            "road_name": road_name,
                            "area": area,
                            "landmark": landmark,
                            "latitude": latitude,
                            "longitude": longitude,
                            "citizen_phone": citizen_phone.strip(),
                            "citizen_name": citizen_name.strip(),
                        },
                        force=True,
                    ):
                        st.warning("This image is currently being processed.")
                    else:
                        try:
                            analyzer = get_analyzer(model, plate_model, confidence, hazard_model)
                            frame = cv2.imdecode(np.frombuffer(file_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if frame is None:
                                raise ValueError("The uploaded image could not be decoded.")

                            with st.spinner("Analyzing image for road defects, vehicles, and safety issues…"):
                                result = analyzer.process_frame(frame)
                                new_incidents = record_image_hazard_incidents(
                                    raw_frame=frame,
                                    annotated_frame=result.annotated_frame,
                                    detections=result.detections,
                                    reports_dir="data/reports",
                                    metadata={
                                        "road_name": road_name,
                                        "area": area,
                                        "landmark": landmark,
                                        "source_name": uploaded.name,
                                        "latitude": latitude,
                                        "longitude": longitude,
                                        "geo_source": geo_source,
                                        "citizen_phone": citizen_phone.strip(),
                                        "citizen_name": citizen_name.strip(),
                                    },
                                    database=incident_db,
                                    source_hash=source_hash,
                                )
                            incident_db.complete_submission(source_hash)
                            st.session_state.image_result = {
                                "hash": analysis_key,
                                "result": result,
                                "incidents": new_incidents,
                                "name": uploaded.name,
                            }
                            st.rerun()
                        except Exception as exc:
                            incident_db.fail_submission(source_hash, error_message=str(exc))
                            st.error(f"Image analysis failed: {exc}")
                            st.warning("⚠️ Processing encountered an error. Incomplete records were cleaned up and the lock has been cleared — click above to retry.")

            saved_image = st.session_state.get("image_result")
            if saved_image and saved_image["hash"] == analysis_key:
                res = saved_image["result"]
                inc_list = saved_image["incidents"]

                img_col, data_col = st.columns([3, 2])
                with img_col:
                    st.image(
                        cv2.cvtColor(res.annotated_frame, cv2.COLOR_BGR2RGB),
                        caption=f"AI Annotated: {uploaded.name}",
                        use_container_width=True,
                    )

                with data_col:
                    v_cnt = sum(d.label in VEHICLES for d in res.detections)
                    p_cnt = sum(d.label in PEOPLE for d in res.detections)
                    h_cnt = sum(is_hazard_label(d.label) for d in res.detections)
                    pl_cnt = len(res.plate_detections)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(_metric_card("Vehicles", v_cnt, "metric-vehicle"), unsafe_allow_html=True)
                    m2.markdown(_metric_card("People", p_cnt, "metric-person"), unsafe_allow_html=True)
                    m3.markdown(_metric_card("Hazards", h_cnt, "metric-hazard"), unsafe_allow_html=True)
                    m4.markdown(_metric_card("Plates", pl_cnt, "metric-plate"), unsafe_allow_html=True)

                    if inc_list:
                        for inc in inc_list:
                            dup_txt = f"<br/><small style='color: #d29922;'>🔁 Possible repeat of: {inc.get('duplicate_of')}</small>" if inc.get("duplicate_of") else ""
                            sms_txt = f"<br/><small style='color: #58a6ff;'>📲 Live Two-Way SMS Tracking enabled for: <strong>{inc.get('citizen_phone')}</strong></small>" if inc.get("citizen_phone") else ""
                            st.markdown(f"""
                            <div class="receipt-card">
                                <h3>✅ Municipal Incident Ticket Generated</h3>
                                <p><strong>Ticket ID:</strong> <code>{inc['ticket_id']}</code> &nbsp;|&nbsp; <strong>Defect:</strong> {inc['hazard_type']}</p>
                                <p><strong>Severity:</strong> {_severity_badge(inc['severity'])} &nbsp;|&nbsp; <strong>Priority Score:</strong> {inc['priority_score']}/100</p>
                                <p><strong>Lane Position:</strong> {inc['lane_position']} Lane &nbsp;|&nbsp; <strong>Status:</strong> <em>{inc['status']}</em>{dup_txt}{sms_txt}</p>
                                <small style="color: #8b949e;">Your report has been queued for municipal public works triage. Track progress anytime in the Tracker above.</small>
                            </div>
                            """, unsafe_allow_html=True)
                    elif h_cnt > 0:
                        st.info("Road hazards were detected and annotated.")
                    else:
                        st.success("No road defects or hazards detected in this image.")

                    st.subheader("🔍 Detected Objects")
                    if res.detections:
                        st.dataframe([
                            {
                                "Category": "Vehicle" if d.label in VEHICLES else "Person" if d.label in PEOPLE else "Hazard" if is_hazard_label(d.label) else "Other",
                                "Class": d.label.replace("_", " ").title(),
                                "Confidence": f"{d.confidence:.1%}",
                            }
                            for d in res.detections
                        ], use_container_width=True, hide_index=True)

                    st.subheader("🛡️ Safety Rules")
                    _render_events(res.events, st) if res.events else st.success("No safety rules violated.")

                    if res.plate_texts:
                        st.subheader("🔢 Number Plates Read (OCR)")
                        st.write("Plates: " + ", ".join(f"`{t}`" for t in res.plate_texts))

        # ─── VIDEO SUBMISSION ──────────────────────────────────
        else:
            video_hash = hashlib.sha256(
                file_bytes + f"{model}|{hazard_model}|{plate_model}|{confidence}|{road_name}|{area}|{landmark}".encode()
            ).hexdigest()

            prior_sub = incident_db.submission(source_hash)
            prior_v_incidents = incident_db.incidents_for_submission(source_hash)
            is_v_completed = bool(prior_sub and prior_sub.get("status") == "COMPLETED")
            is_v_failed = bool(prior_sub and prior_sub.get("status") == "FAILED")
            is_stale_v = bool(prior_sub and prior_sub.get("status") == "PROCESSING")

            st.write(f"📁 Video Selected: **{uploaded.name}** ({len(file_bytes) / 1024 / 1024:.1f} MB)")

            if location_error:
                st.info("Please correct the GPS coordinates above before proceeding.")
            else:
                if is_v_failed:
                    err_msg = prior_sub.get("error_message") or "Interrupted before completion"
                    st.warning(f"⚠️ A previous processing attempt encountered an issue: {err_msg}. Incomplete data was cleaned up — ready to retry.")
                    v_btn_label = "🔄 Retry Dashcam Analysis & File Report"
                    v_btn_type = "primary"
                elif is_stale_v:
                    st.warning("⚠️ A previous processing attempt was interrupted or timed out. You can re-run analysis below.")
                    v_btn_label = "🔄 Retry Dashcam Analysis & File Report"
                    v_btn_type = "primary"
                elif is_v_completed:
                    st.info(f"ℹ️ Analysis was previously completed for this dashcam video ({len(prior_v_incidents)} hazard incident(s) registered). You can review results below or re-process with updated parameters.")
                    v_btn_label = "🔄 Re-Process Video & Overwrite Prior Report"
                    v_btn_type = "secondary"
                else:
                    v_btn_label = "🎬 Analyze Dashcam Video & File Report"
                    v_btn_type = "primary"

                if st.button(v_btn_label, type=v_btn_type, use_container_width=True, key="run_video_btn"):
                    if not incident_db.claim_submission(
                        source_hash,
                        uploaded.name,
                        "video",
                        {
                            "road_name": road_name,
                            "area": area,
                            "landmark": landmark,
                            "latitude": latitude,
                            "longitude": longitude,
                            "citizen_phone": citizen_phone.strip(),
                            "citizen_name": citizen_name.strip(),
                        },
                        force=True,
                    ):
                        st.warning("This video is currently being processed in another active session.")
                    else:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            source_path = Path(temp_dir) / uploaded.name
                            out_path = Path(temp_dir) / f"annotated_{Path(uploaded.name).stem}.mp4"
                            source_path.write_bytes(file_bytes)

                            try:
                                analyzer = get_analyzer(model, plate_model, confidence, hazard_model)
                                pbar = st.progress(0, text="Initializing YOLO & Tracker Pipeline…")
                                def on_prog(frac, msg):
                                    pbar.progress(min(frac, 1.0), text=msg)

                                summary = analyzer.process_video(
                                    input_path=source_path,
                                    output_path=out_path,
                                    progress_callback=on_prog,
                                    incident_metadata={
                                        "road_name": road_name,
                                        "area": area,
                                        "landmark": landmark,
                                        "latitude": latitude,
                                        "longitude": longitude,
                                        "geo_source": geo_source,
                                        "citizen_phone": citizen_phone.strip(),
                                        "citizen_name": citizen_name.strip(),
                                    },
                                    reports_dir="data/reports",
                                    source_hash=source_hash,
                                )
                                pbar.progress(1.0, text="Analysis Complete!")
                                annotated_bytes = out_path.read_bytes()
                                st.session_state.video_result = {
                                    "hash": video_hash,
                                    "source_hash": source_hash,
                                    "bytes": annotated_bytes,
                                    "name": out_path.name,
                                    "summary": summary,
                                }
                                incident_db.complete_submission(source_hash)
                                st.rerun()
                            except Exception as err:
                                incident_db.fail_submission(source_hash, error_message=str(err))
                                st.error(f"Error during video processing: {err}")
                                st.warning("⚠️ Processing was interrupted. Incomplete data has been rolled back and the lock has been cleared — click above to retry.")

            saved_v = st.session_state.get("video_result")
            if saved_v and saved_v["hash"] == video_hash:
                summary = saved_v["summary"]
                st.success(
                    f"🎉 Video Analysis Complete! Found **{len(summary.incidents)}** deduplicated road hazard incident(s) "
                    f"and tracked **{summary.unique_tracks}** unique traffic participants."
                )

                st.video(saved_v["bytes"])
                st.download_button(
                    "⬇️ Download Processed Annotated Video",
                    saved_v["bytes"],
                    file_name=saved_v["name"],
                    mime="video/mp4",
                    use_container_width=True,
                )

                st.subheader("📊 Video Analysis Summary")
                k1, k2, k3, k4, k5, k6 = st.columns(6)
                veh_tot = sum(c for l, c in summary.counts.items() if l in VEHICLES)
                haz_tot = sum(summary.hazard_detection_counts.values())
                k1.markdown(_metric_card("Frames", summary.frames_processed), unsafe_allow_html=True)
                k2.markdown(_metric_card("FPS", f"{summary.average_fps:.1f}"), unsafe_allow_html=True)
                k3.markdown(_metric_card("Unique Tracks", summary.unique_tracks, "metric-track"), unsafe_allow_html=True)
                k4.markdown(_metric_card("Vehicles", veh_tot, "metric-vehicle"), unsafe_allow_html=True)
                k5.markdown(_metric_card("Hazards", haz_tot, "metric-hazard"), unsafe_allow_html=True)
                k6.markdown(_metric_card("Risk Frames", summary.risk_frames, "metric-risk"), unsafe_allow_html=True)

                st.subheader("🧾 Deduplicated Hazard Tickets (Filed to PWD)")
                if summary.incidents:
                    st.caption("Each physical road hazard is clustered into a single ticket with its own evidence snapshot and 3-second clip.")
                    st.dataframe([
                        {
                            "Ticket ID": inc["ticket_id"],
                            "Hazard Type": inc["hazard_type"],
                            "Severity": inc["severity"],
                            "Priority Score": inc["priority_score"],
                            "Lane": inc["lane_position"],
                            "Timestamp": f"{inc['video_timestamp']:.2f}s",
                            "Observations": inc["observations"],
                            "Status": inc["status"],
                            "Citizen Phone": inc.get("citizen_phone") or "—",
                            "Repeat Flag": inc.get("duplicate_of") or "Original",
                        }
                        for inc in summary.incidents
                    ], use_container_width=True, hide_index=True)
                else:
                    st.info("No road defects or potholes met the confirmation threshold in this video.")

                if summary.plate_results:
                    st.subheader("🔢 Verified Vehicle License Plates (OCR Consensus)")
                    st.dataframe([
                        {
                            "Vehicle Track ID": pr["vehicle_track_id"],
                            "Consensus Plate": pr["plate_text"],
                            "Total OCR Reads": pr["read_count"],
                            "Confidence Agreement": f"{pr['consensus']:.0%}",
                        }
                        for pr in summary.plate_results
                    ], use_container_width=True, hide_index=True)

    else:
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🕳️ Automatic Road-Hazard Reporting")
            st.write("Identifies potholes, craters, road cracks, and surface failures. Avoids repetitive reports by clustering multi-frame sightings.")
        with c2:
            st.markdown("### 🎬 Evidence Clips & Snaps")
            st.write("Captures the sharpest snapshot and cuts a 3-second video clip around each hazard event for municipal review.")
        with c3:
            st.markdown("### 🔢 Zero-Duplicate Plate OCR")
            st.write("Tracks vehicles across time and achieves majority-vote OCR consensus on license plates without duplicate records.")

# ================================================================
# TAB 2: MUNICIPAL & PWD ACTION PORTAL
# ================================================================
with portal_tabs[1]:
    st.subheader("🏛️ Municipal Corporation & Public Works Department (PWD) Triage")
    st.caption("Restricted Staff-Only Portal. Authorized personnel can verify defects, assign contractors, issue work-orders, and sign-off on repairs.")

    municipal_actor = _municipal_login()
    if municipal_actor:
        _render_municipal_portal(incident_db, municipal_actor)
