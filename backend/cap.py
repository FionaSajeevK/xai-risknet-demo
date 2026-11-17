import uuid
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET

NS = "urn:oasis:names:tc:emergency:cap:1.2"
IST = timezone(timedelta(hours=5, minutes=30))
CAP_LEVELS = {  # severity, urgency, certainty, headline, instruction
    1: ("Minor", "Future", "Possible", "Landslide watch",
        "Be prepared. Avoid steep slopes and stream banks."),
    2: ("Moderate", "Expected", "Likely", "Landslide warning",
        "Move away from slopes and drainage lines. Keep your phone charged."),
    3: ("Severe", "Immediate", "Likely", "Landslide evacuation advisory",
        "Evacuate now to the nearest shelter using the safest route."),
}

def _el(parent, tag, text=None):
    e = ET.SubElement(parent, f"{{{NS}}}{tag}")
    if text is not None:
        e.text = text
    return e

def build_cap(level, area_desc, polygon, rain24, rain15):
    ET.register_namespace("", NS)
    sev, urg, cert, headline, instruction = CAP_LEVELS[level]
    now = datetime.now(IST).replace(microsecond=0)
    root = ET.Element(f"{{{NS}}}alert")
    _el(root, "identifier", f"XAI-RISKNET-DEMO-{uuid.uuid4().hex[:12]}")
    _el(root, "sender", "xai-risknet-demo@example.org")
    _el(root, "sent", now.isoformat())
    _el(root, "status", "Exercise")
    _el(root, "msgType", "Alert")
    _el(root, "scope", "Public")
    _el(root, "note", "Prototype demonstration. Placeholder risk model and sample rainfall inputs.")
    info = _el(root, "info")
    _el(info, "language", "en-IN")
    _el(info, "category", "Geo")
    _el(info, "event", "Landslide")
    _el(info, "urgency", urg)
    _el(info, "severity", sev)
    _el(info, "certainty", cert)
    _el(info, "expires", (now + timedelta(hours=6)).isoformat())
    _el(info, "senderName", "XAI-RiskNet (prototype)")
    _el(info, "headline", headline)
    _el(info, "description", f"24 h rainfall {rain24:.0f} mm; 15-day rainfall {rain15:.0f} mm (sample inputs).")
    _el(info, "instruction", instruction)
    area = _el(info, "area")
    _el(area, "areaDesc", area_desc)
    _el(area, "polygon", " ".join(f"{y:.5f},{x:.5f}" for x, y in polygon.exterior.coords))
    ET.indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")