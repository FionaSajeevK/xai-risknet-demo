import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox

class Router:
    def __init__(self, boundary_path, data_dir):
        b = gpd.read_file(boundary_path).to_crs(4326)
        poly = b.geometry.union_all().buffer(0.01)
        gpath = data_dir / "graph.graphml"
        if gpath.exists():
            self.G = ox.load_graphml(str(gpath))
        else:
            self.G = ox.graph_from_polygon(poly, network_type="drive")
            ox.save_graphml(self.G, str(gpath))
        spath = data_dir / "shelters.geojson"
        if spath.exists():
            sh = gpd.read_file(spath)
        else:
            sh = ox.features_from_polygon(poly, tags={"amenity": ["school", "hospital", "community_centre"]})
            sh = sh.reset_index(drop=True)
            for c in ("name", "amenity"):
                if c not in sh:
                    sh[c] = None
            sh = sh[["name", "amenity", "geometry"]]
            sh["geometry"] = sh.geometry.representative_point()
            sh.to_file(spath, driver="GeoJSON")
        self.shelters = sh.to_crs(4326).reset_index(drop=True)
        self.sh_nodes = ox.distance.nearest_nodes(
            self.G, self.shelters.geometry.x.values, self.shelters.geometry.y.values)
        self.edges = list(self.G.edges(keys=True, data=True))
        N = self.G.nodes
        self.mid_lon = np.array([(N[u]["x"] + N[v]["x"]) / 2 for u, v, k, d in self.edges])
        self.mid_lat = np.array([(N[u]["y"] + N[v]["y"]) / 2 for u, v, k, d in self.edges])

    def _info(self, path):
        coords, length, exposure = [], 0.0, 0.0
        for u, v in zip(path[:-1], path[1:]):
            d = min(self.G.get_edge_data(u, v).values(), key=lambda e: e["length"])
            g = d.get("geometry")
            pts = list(g.coords) if g is not None else [
                (self.G.nodes[u]["x"], self.G.nodes[u]["y"]), (self.G.nodes[v]["x"], self.G.nodes[v]["y"])]
            coords.extend(pts)
            length += d["length"]
            exposure += d["length"] * d.get("risk", 0)
        return {"coords": coords, "length_m": round(length),
                "mean_risk": round(exposure / length, 3) if length else 0}

    def route(self, lat, lon, risk_fn, penalty=4.0):
        r = risk_fn(self.mid_lon, self.mid_lat)
        for (u, v, k, d), rv in zip(self.edges, r):
            d["risk"] = float(rv)
            d["rweight"] = d["length"] * (1 + penalty * float(rv))  # penalty is a placeholder
        o = ox.distance.nearest_nodes(self.G, lon, lat)
        dist, paths = nx.single_source_dijkstra(self.G, o, weight="rweight")
        cands = [(dist[n], i) for i, n in enumerate(self.sh_nodes) if n in dist]
        if not cands:
            return None
        _, i = min(cands)
        dest = self.sh_nodes[i]
        shortest = nx.shortest_path(self.G, o, dest, weight="length")
        row = self.shelters.iloc[i]
        return {"shelter": {"name": row["name"] or "Unnamed", "type": row["amenity"],
                            "lat": row.geometry.y, "lon": row.geometry.x},
                "shortest": self._info(shortest), "safest": self._info(paths[dest])}