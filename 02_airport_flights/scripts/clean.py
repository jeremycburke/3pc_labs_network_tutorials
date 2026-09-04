"""
clean.py  (the Python answer key)

Turns the raw flight log and airport tables into two Gephi-ready tables,
writes a solution GEXF with map positions, and prints the numbers quoted in
SOLUTION.md.

  raw/flight_log_week.csv + raw/airport_info.csv + raw/airport_food.csv
      -> clean/nodes.csv
      -> clean/edges.csv
      -> solution/airport_flights.gexf

Run from anywhere:   python 02_airport_flights/scripts/clean.py
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

DELAY_THRESHOLD_MIN = 15      # a departure counts as delayed at 15 minutes or more
LOW_DELAY, HIGH_DELAY = 0.17, 0.27
HEALTHY_SHARE, MIXED_SHARE = 0.60, 0.40


def tidy(text):
    return re.sub(r"\s+", " ", str(text)).strip()


# ---------------------------------------------------------------------------
# Step 1. Load the three raw files as text.
# ---------------------------------------------------------------------------
log = pd.read_csv(RAW / "flight_log_week.csv", dtype=str, keep_default_na=False)
info = pd.read_csv(RAW / "airport_info.csv", dtype=str, keep_default_na=False)
food = pd.read_csv(RAW / "airport_food.csv", dtype=str, keep_default_na=False)
print("log rows loaded:", len(log))

# ---------------------------------------------------------------------------
# Step 2. Airport table: fix codes, split the packed columns, parse layover.
# ---------------------------------------------------------------------------
info["Id"] = info["code"].map(tidy).str.upper()
info[["city", "state"]] = info["location"].str.split(",", expand=True)
info["city"] = info["city"].map(tidy)
info["state"] = info["state"].map(tidy)
info[["latitude", "longitude"]] = info["coordinates"].str.split(",", expand=True).astype(float)


def layover_minutes(text):
    """Accepts 75, '75 min', '1 hr', '1h15m'."""
    t = tidy(text).lower()
    m = re.fullmatch(r"(\d+)h(\d+)m", t)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.fullmatch(r"(\d+)\s*hr", t)
    if m:
        return int(m.group(1)) * 60
    return int(re.sub(r"[^0-9]", "", t))


info["avg_layover_min"] = info["typical_layover"].map(layover_minutes)
assert info["Id"].is_unique and len(info) == 20
name_to_code = dict(zip(info["airport_name"], info["Id"]))

# ---------------------------------------------------------------------------
# Step 3. Flight log: standardize the airport columns.
#         Trim, uppercase, and swap any airport names for their codes.
# ---------------------------------------------------------------------------
def to_code(text):
    t = tidy(text)
    if t in name_to_code:
        return name_to_code[t]
    return t.upper()


log["origin"] = log["origin"].map(to_code)
log["dest"] = log["dest"].map(to_code)
unknown = sorted((set(log["origin"]) | set(log["dest"])) - set(info["Id"]))
assert not unknown, f"unrecognised airports: {unknown}"

# ---------------------------------------------------------------------------
# Step 4. Remove exact duplicate rows and rows where origin equals dest.
# ---------------------------------------------------------------------------
before = len(log)
log = log.drop_duplicates()
print("duplicate rows removed:", before - len(log))
loops = int((log["origin"] == log["dest"]).sum())
log = log[log["origin"] != log["dest"]]
print("origin-equals-dest rows removed:", loops)

# ---------------------------------------------------------------------------
# Step 5. Parse the two date formats and the delay column.
#         Blank or n/a delay means the flight was cancelled.
# ---------------------------------------------------------------------------
log["date"] = pd.to_datetime(log["date"], format="mixed")
print("date range:", log["date"].min().date(), "to", log["date"].max().date())
log["delay_min"] = pd.to_numeric(log["delay_min"], errors="coerce")
log["cancelled"] = log["delay_min"].isna()
log["delayed"] = log["delay_min"] >= DELAY_THRESHOLD_MIN
log["air_time_min"] = log["air_time_min"].astype(int)
print("cancelled flights:", int(log["cancelled"].sum()))

# ---------------------------------------------------------------------------
# Step 6. Edges: count flights per origin-dest pair, average the air time.
# ---------------------------------------------------------------------------
edges = (log.groupby(["origin", "dest"])
            .agg(Weight=("flight_no", "size"), avg_flight_min=("air_time_min", "mean"))
            .reset_index()
            .rename(columns={"origin": "Source", "dest": "Target"}))
edges["avg_flight_min"] = edges["avg_flight_min"].round().astype(int)
edges.insert(2, "Type", "Directed")
edges = edges.sort_values(["Source", "Target"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 7. Node metric from the log: share of departures delayed, then bucket.
# ---------------------------------------------------------------------------
flown = log[~log["cancelled"]]
delay = (flown.groupby("origin")["delayed"].mean().rename("delay_rate").round(3))
departures = log.groupby("origin").size().rename("departures_per_week")


def delay_bucket(rate):
    if rate < LOW_DELAY:
        return "Low"
    if rate >= HIGH_DELAY:
        return "High"
    return "Medium"


# ---------------------------------------------------------------------------
# Step 8. Node metric from the food table: share of healthy vendors, then bucket.
# ---------------------------------------------------------------------------
food["airport"] = food["airport"].map(tidy).str.upper()
food["rating"] = food["rating"].map(tidy).str.capitalize()
unrated = int((food["rating"] == "").sum())
food = food[food["rating"] != ""]
assert set(food["rating"]) == {"Healthy", "Unhealthy"}
counts = food.pivot_table(index="airport", columns="rating", values="vendor",
                          aggfunc="count", fill_value=0)
counts["healthy_share"] = (counts["Healthy"] / (counts["Healthy"] + counts["Unhealthy"])).round(2)
print("unrated vendors dropped:", unrated)


def food_bucket(share):
    if share >= HEALTHY_SHARE:
        return "Healthy"
    if share >= MIXED_SHARE:
        return "Mixed"
    return "Unhealthy"


# ---------------------------------------------------------------------------
# Step 9. Assemble the nodes table.
# ---------------------------------------------------------------------------
nodes = (info[["Id", "airport_name", "city", "state", "latitude", "longitude", "avg_layover_min"]]
         .rename(columns={"airport_name": "Label"})
         .merge(delay, left_on="Id", right_index=True, how="left")
         .merge(departures, left_on="Id", right_index=True, how="left")
         .merge(counts[["healthy_share"]], left_on="Id", right_index=True, how="left"))
nodes["delay_category"] = nodes["delay_rate"].map(delay_bucket)
nodes["food_category"] = nodes["healthy_share"].map(food_bucket)
nodes = nodes[["Id", "Label", "city", "state", "latitude", "longitude",
               "departures_per_week", "delay_rate", "delay_category",
               "healthy_share", "food_category", "avg_layover_min"]]
nodes = nodes.sort_values("Id").reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 10. Checks, then write.
# ---------------------------------------------------------------------------
assert nodes["Id"].is_unique
assert not nodes.isna().any().any()
assert set(edges["Source"]) | set(edges["Target"]) <= set(nodes["Id"])
assert (edges["Source"] != edges["Target"]).all()
assert (edges["Weight"] > 0).all()
assert not edges.duplicated(subset=["Source", "Target"]).any()
assert not ((edges["Source"] == "BOS") & (edges["Target"] == "SEA")).any()

nodes.to_csv(CLEAN / "nodes.csv", index=False, encoding="utf-8")
edges.to_csv(CLEAN / "edges.csv", index=False, encoding="utf-8")
print(f"wrote clean/nodes.csv ({len(nodes)} rows) and clean/edges.csv ({len(edges)} rows)")

# ---------------------------------------------------------------------------
# Solution GEXF with map positions (simple equirectangular projection).
# ---------------------------------------------------------------------------
G = nx.DiGraph()
for r in nodes.itertuples(index=False):
    G.add_node(r.Id, label=r.Label, city=r.city, state=r.state,
               latitude=float(r.latitude), longitude=float(r.longitude),
               departures_per_week=int(r.departures_per_week),
               delay_rate=float(r.delay_rate), delay_category=r.delay_category,
               healthy_share=float(r.healthy_share), food_category=r.food_category,
               avg_layover_min=int(r.avg_layover_min))
    x = (float(r.longitude) + 97.0) * 20.0 * math.cos(math.radians(37.0))
    y = (float(r.latitude) - 37.0) * 20.0
    G.nodes[r.Id]["viz"] = {"position": {"x": x, "y": y, "z": 0.0}}
for r in edges.itertuples(index=False):
    G.add_edge(r.Source, r.Target, weight=float(r.Weight), avg_flight_min=int(r.avg_flight_min))
nx.write_gexf(G, SOLUTION / "airport_flights.gexf")
print("wrote solution/airport_flights.gexf")

# ---------------------------------------------------------------------------
# Findings quoted in SOLUTION.md
# ---------------------------------------------------------------------------
print("\n=== findings ===")
print("nodes", G.number_of_nodes(), "edges", G.number_of_edges())
print("\ndelay categories:")
for cat in ["Low", "Medium", "High"]:
    sub = nodes[nodes["delay_category"] == cat].sort_values("delay_rate")
    print(f"   {cat:<7}", ", ".join(f"{r.Id} {r.delay_rate:.2f}" for r in sub.itertuples()))
print("\nfood categories:")
for cat in ["Healthy", "Mixed", "Unhealthy"]:
    sub = nodes[nodes["food_category"] == cat]
    print(f"   {cat:<10}", ", ".join(f"{r.Id} {r.healthy_share:.2f}" for r in sub.itertuples()))

wdeg = dict(G.degree(weight="weight"))
print("\nbusiest airports (weighted degree, flights in + out per week):")
for n in sorted(wdeg, key=wdeg.get, reverse=True)[:6]:
    print(f"   {n} {wdeg[n]:.0f}  (routes: {G.degree(n) // 2})")
print("\nquietest airports:")
for n in sorted(wdeg, key=wdeg.get)[:4]:
    print(f"   {n} {wdeg[n]:.0f}  (routes: {G.degree(n) // 2})")

print("\nheaviest routes (one direction):")
top = edges.sort_values("Weight", ascending=False).head(6)
for r in top.itertuples():
    print(f"   {r.Source} -> {r.Target}  {r.Weight} flights/week, {r.avg_flight_min} min")

print("\nBOS to SEA, one connection:")
print(f"   {'via':<4} {'BOS->X':>7} {'X->SEA':>7} {'delay':>7} {'cat':<7} {'layover':>7}")
rows = []
for x in G.successors("BOS"):
    if G.has_edge(x, "SEA"):
        rows.append((x, G["BOS"][x]["weight"], G[x]["SEA"]["weight"],
                     G.nodes[x]["delay_rate"], G.nodes[x]["delay_category"],
                     G.nodes[x]["avg_layover_min"]))
for x, w1, w2, d, cat, lay in sorted(rows, key=lambda t: -min(t[1], t[2])):
    print(f"   {x:<4} {w1:>7.0f} {w2:>7.0f} {d:>7.2f} {cat:<7} {lay:>7}")
print("   shortest path by hops:", nx.shortest_path(G, "BOS", "SEA"))
print("   avg path length (directed):", round(nx.average_shortest_path_length(G), 3))
print("   diameter (directed):", nx.diameter(G))
