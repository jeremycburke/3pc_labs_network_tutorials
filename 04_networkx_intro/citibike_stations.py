"""
citibike_stations.py

The Citi Bike station network from project 3, in code instead of Gephi.
Reads the two clean CSVs, finds the full and empty docks, pairs them up, draws a map.

Run from anywhere:   python 04_networkx_intro/citibike_stations.py
"""
import math
from pathlib import Path

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "03_citibike_stations" / "clean"
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# 1. Read the two tables. Station ids look like numbers, so read them as text.
nodes = pd.read_csv(DATA / "nodes.csv", dtype={"Id": str})
edges = pd.read_csv(DATA / "edges.csv", dtype={"Source": str, "Target": str})

# 2. Build the graph.
G = nx.DiGraph()
for row in nodes.itertuples():
    G.add_node(row.Id, name=row.Label, lat=row.latitude, lon=row.longitude,
               capacity=row.capacity, net=row.net_flow, pattern=row.status_pattern,
               neighborhood=row.neighborhood)
for row in edges.itertuples():
    G.add_edge(row.Source, row.Target, weight=row.Weight)

print(G.number_of_nodes(), "stations,", G.number_of_edges(), "flows")

# 3. Which docks run full, which run empty? Read it straight off the node attribute.
full = [s for s in G if G.nodes[s]["pattern"] == "Often full"]
empty = [s for s in G if G.nodes[s]["pattern"] == "Often empty"]
print("\nOften full:", ", ".join(G.nodes[s]["name"] for s in full))
print("Often empty:", ", ".join(G.nodes[s]["name"] for s in empty))

# 4. Where do bikes come from and go to? In and out weighted degree, separately.
arriving = dict(G.in_degree(weight="weight"))
leaving = dict(G.out_degree(weight="weight"))
print("\nMost trips arriving:", ", ".join(G.nodes[s]["name"] for s in sorted(arriving, key=arriving.get, reverse=True)[:3]))
print("Most trips leaving:", ", ".join(G.nodes[s]["name"] for s in sorted(leaving, key=leaving.get, reverse=True)[:3]))


# 5. The plan: for each often-full dock, the nearest often-empty dock.
def km_apart(a, b):
    """Straight-line distance between two stations. One degree of latitude is 111 km;
    a degree of longitude is shorter this far north, hence the cosine."""
    dy = (G.nodes[b]["lat"] - G.nodes[a]["lat"]) * 111
    dx = (G.nodes[b]["lon"] - G.nodes[a]["lon"]) * 111 * math.cos(math.radians(40.74))
    return math.hypot(dx, dy)


print("\nTruck route: take bikes from -> bring them to (km)")
for f in full:
    nearest = min(empty, key=lambda e: km_apart(f, e))
    print(f"   {G.nodes[f]['name']:<28} -> {G.nodes[nearest]['name']:<28} {km_apart(f, nearest):.1f}")

# 6. Draw the map. Only the flows with 10 or more trips, or the picture is a thicket.
#    One dictionary per category attribute maps each value to a color. Edit the
#    colors here. Every value the attribute takes needs an entry.

# color_by = "pattern"
colors_patterns = {"Often full": "tab:blue",
                   "Often empty": "tab:red",
                   "Swings both ways": "tab:purple",
                   "Balanced": "lightgray"}

# color_by = "neighborhood"
colors_neighborhoods = {"Midtown": "tab:blue",
                        "Chelsea": "tab:orange",
                        "Village": "tab:green",
                        "Lower Manhattan": "tab:purple",
                        "Upper East Side": "tab:red"}

# color_by = "net"
# Net flow is a number, not a category, so there is no dictionary for it. It is
# drawn on a blue-to-red scale with a colorbar instead, and colors is ignored.

# Change these two lines to recolor the map. color_by is the attribute name
# carried on the nodes in block 2 (pattern, neighborhood or net), and colors is
# the dictionary that goes with it.
color_by = "net"
colors = colors_patterns

pos = {s: (G.nodes[s]["lon"], G.nodes[s]["lat"]) for s in G}
heavy = [(u, v) for u, v in G.edges if G[u][v]["weight"] >= 10]
plt.figure(figsize=(8, 10))
nx.draw_networkx_edges(G, pos, edgelist=heavy, arrows=False, edge_color="lightgray",
                       width=[G[u][v]["weight"] / 8 for u, v in heavy])
sizes = [G.nodes[s]["capacity"] * 6 for s in G]

if color_by == "net":
    drawn = nx.draw_networkx_nodes(G, pos, node_color=[G.nodes[s]["net"] for s in G],
                                   cmap="RdBu", vmin=-50, vmax=50, node_size=sizes)
    plt.colorbar(drawn, label="net flow over the week (bikes gained)")
else:
    nx.draw_networkx_nodes(G, pos, node_color=[colors[G.nodes[s][color_by]] for s in G],
                           node_size=sizes)
    for value, color in colors.items():
        plt.scatter([], [], c=color, label=value)
    plt.legend(loc="lower right", fontsize=8, title=color_by)

nx.draw_networkx_labels(G, pos, labels={s: G.nodes[s]["name"] for s in full + empty}, font_size=6)
plt.title(f"Flows of 10 or more trips, colored by {color_by}")
plt.axis("off")
plt.savefig(OUT / "citibike_stations.png", dpi=120, bbox_inches="tight")
plt.show()
