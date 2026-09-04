"""
clean.py  (the Python answer key)

Turns the raw trip log and station snapshots into two Gephi-ready tables,
writes a solution GEXF with map positions, and prints the numbers quoted in
SOLUTION.md.

  raw/station_information.csv + raw/citibike_trips_sample.csv
      + raw/station_status_snapshots.csv
      -> clean/nodes.csv
      -> clean/edges.csv
      -> solution/citibike_stations.gexf

Run from anywhere:   python 03_citibike_stations/scripts/clean.py
Each numbered block below matches a step in CLEANING.md.
"""
import math
import re
from pathlib import Path

import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, SOLUTION = ROOT / "raw", ROOT / "clean", ROOT / "solution"
CLEAN.mkdir(exist_ok=True)
SOLUTION.mkdir(exist_ok=True)

MAX_TRIP_HOURS = 24
MIN_TRIPS = 3                             # a pair needs this many trips to count as a flow
FULL_SHARE, EMPTY_SHARE = 0.15, 0.15      # share of hours full or empty that counts as "often"


def fix_station(text):
    """Trim, collapse spaces, write 'and' as '&', and match the official casing."""
    t = re.sub(r"\s+", " ", str(text)).strip()
    t = re.sub(r"\s+and\s+", " & ", t, flags=re.IGNORECASE)
    return t.title()


# ---------------------------------------------------------------------------
# Step 1. Load the three raw files as text.
# ---------------------------------------------------------------------------
stations = pd.read_csv(RAW / "station_information.csv", dtype=str)
trips = pd.read_csv(RAW / "citibike_trips_sample.csv", dtype=str, keep_default_na=False)
snap = pd.read_csv(RAW / "station_status_snapshots.csv", dtype=str, keep_default_na=False)
print("trip rows loaded:", len(trips), "| snapshot rows loaded:", len(snap))

stations["key"] = stations["name"].map(fix_station)
assert stations["key"].is_unique
key_to_id = dict(zip(stations["key"], stations["station_id"]))

# ---------------------------------------------------------------------------
# Step 2. Standardize station names in both logs and look up the station id.
#         The id columns in the trip file mix old and new id styles, so the
#         name is the reliable key.
# ---------------------------------------------------------------------------
trips["Source"] = trips["start_station_name"].map(fix_station).map(key_to_id)
trips["Target"] = trips["end_station_name"].map(fix_station).map(key_to_id)
snap["Id"] = snap["station_name"].map(fix_station).map(key_to_id)
assert snap["Id"].notna().all(), "snapshot station names that did not match"
assert trips["Source"].notna().all(), "start station names that did not match"

# ---------------------------------------------------------------------------
# Step 3. Remove duplicate rows, trips with no end, and impossible durations.
# ---------------------------------------------------------------------------
before = len(trips)
trips = trips.drop_duplicates(subset="ride_id")
print("duplicate rides removed:", before - len(trips))

no_end = trips["end_station_name"].str.strip() == ""
print("trips with no end station removed:", int(no_end.sum()))
trips = trips[~no_end]
assert trips["Target"].notna().all(), "end station names that did not match"

trips["started_at"] = pd.to_datetime(trips["started_at"])
trips["ended_at"] = pd.to_datetime(trips["ended_at"])
trips["duration_min"] = (trips["ended_at"] - trips["started_at"]).dt.total_seconds() / 60
bad = (trips["duration_min"] <= 0) | (trips["duration_min"] > MAX_TRIP_HOURS * 60)
print("impossible durations removed:", int(bad.sum()))
trips = trips[~bad]

# ---------------------------------------------------------------------------
# Step 4. Round trips start and end at the same dock. They are real rides but
#         they are not a flow between stations, so drop them for the graph.
# ---------------------------------------------------------------------------
loops = trips["Source"] == trips["Target"]
print("round trips removed:", int(loops.sum()))
trips = trips[~loops]
trips["ebike"] = trips["rideable_type"].eq("electric_bike")

# ---------------------------------------------------------------------------
# Step 5. Edges: one row per start-end pair with the trip count. Pairs with
#         only one or two trips all week are noise for a rebalancing plan, so
#         they are left out. Set MIN_TRIPS to 1 to keep every pair.
# ---------------------------------------------------------------------------
edges = (trips.groupby(["Source", "Target"])
              .agg(Weight=("ride_id", "size"),
                   avg_duration_min=("duration_min", "mean"),
                   ebike_share=("ebike", "mean"))
              .reset_index())
thin = edges["Weight"] < MIN_TRIPS
print(f"station pairs seen: {len(edges)} | kept with {MIN_TRIPS}+ trips: {int((~thin).sum())}"
      f" | trips in kept pairs: {int(edges.loc[~thin, 'Weight'].sum())} of {int(edges['Weight'].sum())}")
edges = edges[~thin]
edges["avg_duration_min"] = edges["avg_duration_min"].round(1)
edges["ebike_share"] = edges["ebike_share"].round(2)
edges.insert(2, "Type", "Directed")
edges = edges.sort_values(["Source", "Target"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 6. Node metrics from the trips: departures, arrivals, net flow.
# ---------------------------------------------------------------------------
departures = trips.groupby("Source").size().rename("departures")
arrivals = trips.groupby("Target").size().rename("arrivals")

# ---------------------------------------------------------------------------
# Step 7. Node metrics from the snapshots: share of hours full and empty.
#         Blank capacity is bikes + docks.
# ---------------------------------------------------------------------------
for col in ["bikes_available", "docks_available"]:
    snap[col] = snap[col].astype(int)
snap["capacity"] = pd.to_numeric(snap["capacity"], errors="coerce")
filled = int(snap["capacity"].isna().sum())
snap["capacity"] = snap["capacity"].fillna(snap["bikes_available"] + snap["docks_available"]).astype(int)
print("blank capacities filled in:", filled)
snap["full"] = snap["docks_available"] == 0
snap["empty"] = snap["bikes_available"] == 0
status = (snap.groupby("Id")
              .agg(pct_time_full=("full", "mean"), pct_time_empty=("empty", "mean"),
                   snapshots=("full", "size"))
              .round(3))
assert (status["snapshots"] == 7 * 24).all()


def pattern(row):
    full = row["pct_time_full"] >= FULL_SHARE
    empty = row["pct_time_empty"] >= EMPTY_SHARE
    if full and empty:
        return "Swings both ways"
    if full:
        return "Often full"
    if empty:
        return "Often empty"
    return "Balanced"


# ---------------------------------------------------------------------------
# Step 8. Assemble the nodes table.
# ---------------------------------------------------------------------------
nodes = (stations[["station_id", "name", "neighborhood", "latitude", "longitude", "capacity"]]
         .rename(columns={"station_id": "Id", "name": "Label"})
         .merge(departures, left_on="Id", right_index=True, how="left")
         .merge(arrivals, left_on="Id", right_index=True, how="left")
         .merge(status[["pct_time_full", "pct_time_empty"]], left_on="Id", right_index=True, how="left"))
nodes["latitude"] = nodes["latitude"].astype(float)
nodes["longitude"] = nodes["longitude"].astype(float)
nodes["capacity"] = nodes["capacity"].astype(int)
nodes[["departures", "arrivals"]] = nodes[["departures", "arrivals"]].fillna(0).astype(int)
nodes["net_flow"] = nodes["arrivals"] - nodes["departures"]
nodes["status_pattern"] = nodes.apply(pattern, axis=1)
nodes = nodes[["Id", "Label", "neighborhood", "latitude", "longitude", "capacity",
               "departures", "arrivals", "net_flow", "pct_time_full", "pct_time_empty",
               "status_pattern"]]
nodes = nodes.sort_values("Label").reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 9. Checks, then write.
# ---------------------------------------------------------------------------
assert nodes["Id"].is_unique
assert not nodes.isna().any().any()
assert set(edges["Source"]) | set(edges["Target"]) <= set(nodes["Id"])
assert (edges["Source"] != edges["Target"]).all()
assert (edges["Weight"] > 0).all()
assert not edges.duplicated(subset=["Source", "Target"]).any()

nodes.to_csv(CLEAN / "nodes.csv", index=False, encoding="utf-8")
edges.to_csv(CLEAN / "edges.csv", index=False, encoding="utf-8")
print(f"wrote clean/nodes.csv ({len(nodes)} rows) and clean/edges.csv ({len(edges)} rows)")

# ---------------------------------------------------------------------------
# Solution GEXF with map positions.
# ---------------------------------------------------------------------------
G = nx.DiGraph()
for r in nodes.itertuples(index=False):
    G.add_node(r.Id, label=r.Label, neighborhood=r.neighborhood,
               latitude=float(r.latitude), longitude=float(r.longitude),
               capacity=int(r.capacity), departures=int(r.departures), arrivals=int(r.arrivals),
               net_flow=int(r.net_flow), pct_time_full=float(r.pct_time_full),
               pct_time_empty=float(r.pct_time_empty), status_pattern=r.status_pattern)
    x = (float(r.longitude) + 74.0) * 15000.0 * math.cos(math.radians(40.74))
    y = (float(r.latitude) - 40.74) * 15000.0
    G.nodes[r.Id]["viz"] = {"position": {"x": x, "y": y, "z": 0.0}}
for r in edges.itertuples(index=False):
    G.add_edge(r.Source, r.Target, weight=float(r.Weight),
               avg_duration_min=float(r.avg_duration_min), ebike_share=float(r.ebike_share))
nx.write_gexf(G, SOLUTION / "citibike_stations.gexf")
print("wrote solution/citibike_stations.gexf")

# ---------------------------------------------------------------------------
# Findings quoted in SOLUTION.md
# ---------------------------------------------------------------------------
print("\n=== findings ===")
print("nodes", G.number_of_nodes(), "edges", G.number_of_edges(), "trips kept", len(trips))
print("status pattern counts:", nodes["status_pattern"].value_counts().to_dict())
print("\nby neighborhood:")
print(nodes.groupby("neighborhood").agg(stations=("Id", "size"), net_flow=("net_flow", "sum"),
                                         full=("pct_time_full", "mean"),
                                         empty=("pct_time_empty", "mean")).round(2).to_string())

print("\noften full (top 5 by share of hours full):")
for r in nodes.sort_values("pct_time_full", ascending=False).head(5).itertuples():
    print(f"   {r.Label:<32} {r.neighborhood:<16} full {r.pct_time_full:.2f}  net {r.net_flow:+d}")
print("\noften empty (top 5 by share of hours empty):")
for r in nodes.sort_values("pct_time_empty", ascending=False).head(5).itertuples():
    print(f"   {r.Label:<32} {r.neighborhood:<16} empty {r.pct_time_empty:.2f}  net {r.net_flow:+d}")
print("\nbiggest net inflow / outflow:")
for r in nodes.sort_values("net_flow", ascending=False).head(3).itertuples():
    print(f"   {r.Label:<32} net {r.net_flow:+d}  ({r.status_pattern})")
for r in nodes.sort_values("net_flow").head(3).itertuples():
    print(f"   {r.Label:<32} net {r.net_flow:+d}  ({r.status_pattern})")

label = dict(zip(nodes["Id"], nodes["Label"]))
print("\nheaviest flows:")
for r in edges.sort_values("Weight", ascending=False).head(6).itertuples():
    print(f"   {label[r.Source]:<28} -> {label[r.Target]:<28} {r.Weight} trips, {r.avg_duration_min} min")
indeg = dict(G.in_degree(weight="weight"))
outdeg = dict(G.out_degree(weight="weight"))
print("\nweighted in-degree leaders:", [f"{label[n]} {indeg[n]:.0f}" for n in sorted(indeg, key=indeg.get, reverse=True)[:3]])
print("weighted out-degree leaders:", [f"{label[n]} {outdeg[n]:.0f}" for n in sorted(outdeg, key=outdeg.get, reverse=True)[:3]])
print("edges with weight >= 10:", int((edges['Weight'] >= 10).sum()), "| >= 5:", int((edges['Weight'] >= 5).sum()))

# Rebalancing suggestion: for each often-full station, the nearest often-empty one.
full_ids = nodes[nodes["status_pattern"] == "Often full"]
empty_ids = nodes[nodes["status_pattern"] == "Often empty"]
print("\nrebalancing pairs (often full -> nearest often empty, km):")
for f in full_ids.itertuples():
    best, best_d = None, 1e9
    for e in empty_ids.itertuples():
        d = math.hypot((e.latitude - f.latitude) * 111.0,
                       (e.longitude - f.longitude) * 111.0 * math.cos(math.radians(40.74)))
        if d < best_d:
            best, best_d = e, d
    if best is not None:
        print(f"   {f.Label:<32} -> {best.Label:<32} {best_d:.1f}")
