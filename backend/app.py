import io
import json
from pathlib import Path
import geopandas as gpd
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from alerts import dispatch
from cap import build_cap
from messages import alert_text
from risk import RiskModel, level_from_rain, LEVELS
from routing import Router
from shapely.geometry import Point
from shapely.prepared import prep

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
app = FastAPI()
model = RiskModel(DATA / "slope.tif", scale=45.0)
router = Router(DATA / "boundary.geojson", DATA)
boundary = gpd.read_file(DATA / "boundary.geojson").to_crs(4326)
geom = boundary.geometry.union_all()
if geom.geom_type == "MultiPolygon":
    geom = max(geom.geoms, key=lambda g: g.area)
cap_poly = geom.simplify(0.0005)
_zones = None

# Demo resident's home. Leave as None to auto-pick a road junction near the middle of the area.
HOME_LAT, HOME_LON = 11.539677, 76.117043
_pg = prep(geom)
_nodes = [(n, d["x"], d["y"]) for n, d in router.G.nodes(data=True)]
_inside = [t for t in _nodes if _pg.contains(Point(t[1], t[2]))] or _nodes
if HOME_LAT is not None and _pg.contains(Point(HOME_LON, HOME_LAT)):
    _tx, _ty = HOME_LON, HOME_LAT
else:
    _rp = geom.representative_point()
    _tx, _ty = _rp.x, _rp.y
_, _hx, _hy = min(_inside, key=lambda t: (t[1] - _tx) ** 2 + (t[2] - _ty) ** 2)
HOME = {"name": "Arun", "lat": _hy, "lon": _hx}

@app.get("/api/status")
def status(rain24: float = 0, rain15: float = 0):
    lvl = level_from_rain(rain24, rain15)
    s, w, n, e = model.bounds
    return {"level": lvl, "name": LEVELS[lvl], "bounds": [[s, w], [n, e]]}

@app.get("/api/zones")
def zones():
    global _zones
    if _zones is None:
        _zones = model.zones()
    return _zones

@app.get("/api/risk.png")
def risk_png(rain24: float = 0, rain15: float = 0):
    risk, _ = model.risk(rain24, rain15)
    buf = io.BytesIO()
    model.to_png(risk).save(buf, "PNG")
    return Response(buf.getvalue(), media_type="image/png")

@app.get("/api/boundary")
def get_boundary():
    return json.loads(boundary.to_json())

@app.get("/api/shelters")
def get_shelters():
    return json.loads(router.shelters.to_json())

@app.get("/api/route")
def route(lat: float, lon: float, rain24: float = 0, rain15: float = 0):
    risk, _ = model.risk(rain24, rain15)
    res = router.route(lat, lon, lambda lo, la: model.risk_at(lo, la, risk))
    return res or {"error": "No reachable shelter from this point"}

class AlertReq(BaseModel):
    rain24: float
    rain15: float

@app.post("/api/alert")
def alert(req: AlertReq):
    lvl = level_from_rain(req.rain24, req.rain15)
    if lvl == 0:
        return {"level": 0, "message": "Below alert threshold - nothing sent."}
    cap = build_cap(lvl, "Meppadi, Wayanad (demo area)", cap_poly, req.rain24, req.rain15)
    entry = dispatch(DATA / "alerts_log.jsonl", lvl, cap, alert_text(lvl))
    return {"level": lvl, "cap": cap, "log": entry}
@app.get("/api/home")
def home():
    return HOME
app.mount("/", StaticFiles(directory=BASE.parent / "frontend", html=True), name="ui")