"""
verify_all.py

Reloads every clean CSV pair and every solution GEXF and checks that they are
sound for Gephi. Run from the top folder:

    python verify_all.py

Exits with a non-zero code if any check fails.
"""
import sys
from pathlib import Path

import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parent
PROJECTS = {
    "01_social_network": "social_network.gexf",
    "02_airport_flights": "airport_flights.gexf",
    "03_citibike_stations": "citibike_stations.gexf",
}
NUMERIC = {
    "01_social_network": ["age"],
    "02_airport_flights": ["latitude", "longitude", "departures_per_week", "delay_rate",
                           "healthy_share", "avg_layover_min"],
    "03_citibike_stations": ["latitude", "longitude", "capacity", "departures", "arrivals",
                             "net_flow", "pct_time_full", "pct_time_empty"],
}

failures = 0


def check(condition, message):
    global failures
    print(("  ok   " if condition else "  FAIL ") + message)
    if not condition:
        failures += 1


for folder, gexf_name in PROJECTS.items():
    print(f"\n{folder}")
    nodes = pd.read_csv(ROOT / folder / "clean" / "nodes.csv", keep_default_na=False)
    edges = pd.read_csv(ROOT / folder / "clean" / "edges.csv", keep_default_na=False)

    check(list(nodes.columns[:2]) == ["Id", "Label"], "nodes start with Id, Label")
    check(list(edges.columns[:4]) == ["Source", "Target", "Type", "Weight"],
          "edges start with Source, Target, Type, Weight")
    check(nodes["Id"].is_unique, f"{len(nodes)} node ids, all unique")
    check("Type" not in nodes.columns, "nodes table has no reserved Type column")
    check((edges["Type"] == "Directed").all(), "every edge Type is Directed")
    ids = set(nodes["Id"].astype(str))
    check(set(edges["Source"].astype(str)) | set(edges["Target"].astype(str)) <= ids,
          "every edge endpoint is a node")
    check((edges["Source"] != edges["Target"]).all(), "no self-loops")
    check(not edges.duplicated(subset=["Source", "Target"]).any(), "no repeated Source-Target pairs")
    weights = pd.to_numeric(edges["Weight"], errors="coerce")
    check(weights.notna().all() and (weights > 0).all(), f"{len(edges)} edges, all weights numeric and positive")
    for col in NUMERIC[folder]:
        series = nodes[col].replace("", pd.NA)
        parsed = pd.to_numeric(series, errors="coerce")
        blanks = int(series.isna().sum())
        check(parsed.notna().sum() + blanks == len(nodes),
              f"column {col} is numeric ({blanks} blank)")

    raw_bytes = (ROOT / folder / "clean" / "nodes.csv").read_bytes()
    check(not raw_bytes.startswith(b"\xef\xbb\xbf"), "nodes.csv has no byte-order mark")
    raw_bytes.decode("utf-8")

    gexf_path = ROOT / folder / "solution" / gexf_name
    G = nx.read_gexf(gexf_path)
    check(G.is_directed(), f"{gexf_name} is directed")
    check(G.number_of_nodes() == len(nodes) and G.number_of_edges() == len(edges),
          f"{gexf_name} has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges, matching the CSVs")
    attrs = set()
    for _, data in G.nodes(data=True):
        attrs |= set(data)
    expected = set(nodes.columns) - {"Id", "Label"}
    check(expected <= attrs, f"{gexf_name} carries node attributes: {', '.join(sorted(expected))}")
    has_position = all("viz" in d and "position" in d["viz"] for _, d in G.nodes(data=True))
    check(has_position, f"{gexf_name} carries a position for every node")
    check(nx.is_weakly_connected(G), "graph is one connected piece")

print("\n04_networkx_intro")
import os
import subprocess

for script in ["social_network.py", "airport_flights.py", "citibike_stations.py"]:
    path = ROOT / "04_networkx_intro" / script
    picture = ROOT / "04_networkx_intro" / "output" / script.replace(".py", ".png")
    env = dict(os.environ, MPLBACKEND="Agg")       # draw to a file, do not open a window
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, env=env)
    check(result.returncode == 0, f"{script} runs without error")
    if result.returncode != 0:
        print(result.stderr.strip().splitlines()[-1])
    check(picture.exists() and picture.stat().st_size > 10_000, f"{script} wrote output/{picture.name}")

print()
if failures:
    print(f"{failures} check(s) failed")
    sys.exit(1)
print("all checks passed")
