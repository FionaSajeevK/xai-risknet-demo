from rasterio.features import shapes
from scipy.ndimage import uniform_filter
from shapely.geometry import shape, mapping
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image

LEVELS = ["No alert", "Watch", "Warning", "Evacuate"]
FACTORS = [0.15, 0.40, 0.70, 1.00]  # PLACEHOLDER rainfall multipliers
CLASS_EDGES = [0.33, 0.55, 0.75]   # PLACEHOLDER: roughly 15, 25 and 34 degrees of slope
CLASS_NAMES = {2: "Moderate risk", 3: "High risk", 4: "Very high risk"}
def level_from_rain(rain24, rain15):
    """24 h classes follow IMD (mm): heavy 64.5-115.5, very heavy 115.6-204.4, extremely heavy >204.4.
    The 15-day rule (300 mm) is a PLACEHOLDER to calibrate later with CHIRPS + the inventory."""
    if rain24 > 204.4: lvl = 3
    elif rain24 >= 115.6: lvl = 2
    elif rain24 >= 64.5: lvl = 1
    else: lvl = 0
    if rain15 >= 300 and lvl < 3:
        lvl += 1
    return lvl

class RiskModel:
    """PLACEHOLDER: slope-based susceptibility x rainfall factor. Swap for the trained model's raster later."""
    def __init__(self, path, scale=45.0):
        with rasterio.open(path) as src:
            tr, w, h = calculate_default_transform(src.crs, "EPSG:4326", src.width, src.height, *src.bounds)
            arr = np.full((h, w), np.nan, dtype="float32")
            reproject(source=rasterio.band(src, 1), destination=arr,
                      src_transform=src.transform, src_crs=src.crs, src_nodata=src.nodata,
                      dst_transform=tr, dst_crs="EPSG:4326", dst_nodata=np.nan,
                      resampling=Resampling.bilinear)
        self.transform, self.h, self.w = tr, h, w
        self.base = np.clip(arr / scale, 0, 1)
        west, north = tr * (0, 0)
        east, south = tr * (w, h)
        self.bounds = [south, west, north, east]

    def risk(self, rain24, rain15):
        lvl = level_from_rain(rain24, rain15)
        return self.base * FACTORS[lvl], lvl

    def to_png(self, risk):
        r = np.nan_to_num(risk)
        rgba = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        rgba[..., 0] = np.clip(r * 2, 0, 1) * 255
        rgba[..., 1] = np.clip(2 - 2 * r, 0, 1) * 255
        rgba[..., 3] = np.where(np.isnan(risk), 0, 170)
        return Image.fromarray(rgba, "RGBA")

    def risk_at(self, lons, lats, risk):
        cols, rows = (~self.transform) * (np.asarray(lons), np.asarray(lats))
        cols, rows = np.floor(cols).astype(int), np.floor(rows).astype(int)
        inside = (rows >= 0) & (rows < self.h) & (cols >= 0) & (cols < self.w)
        out = np.zeros(len(cols), dtype="float32")
        out[inside] = np.nan_to_num(risk[rows[inside], cols[inside]])
        return out
        def zones(self, min_cells=40):
         """Static susceptibility zones as polygons (placeholder: slope classes)."""
        valid = ~np.isnan(self.base)
        smooth = uniform_filter(np.where(valid, self.base, 0).astype("float32"), size=5)
        cls = (np.digitize(smooth, CLASS_EDGES) + 1).astype("uint8")   # 1 low ... 4 very high
        cls[~valid] = 0
        min_area = min_cells * abs(self.transform.a * self.transform.e)
        feats = []
        for geom, val in shapes(cls, mask=cls >= 2, transform=self.transform):
            poly = shape(geom)
            if poly.area < min_area:
                continue
            poly = poly.simplify(0.00005)
            if poly.is_empty:
                continue
            c = int(val)
            feats.append({"type": "Feature", "geometry": mapping(poly),
                          "properties": {"cls": c, "name": CLASS_NAMES[c]}})
        return {"type": "FeatureCollection", "features": feats}