"""
airport_flights.py

The airport network from project 2, in code instead of Gephi.
Reads the two clean CSVs, lists the Boston to Seattle connections, draws a map.

Run from anywhere:   python 04_networkx_intro/airport_flights.py
"""
from pathlib import Path

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "02_airport_flights" / "clean"
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# 1. Read the two tables.
nodes = pd.read_csv(DATA / "nodes.csv")
edges = pd.read_csv(DATA / "edges.csv")

# 2. Build the graph. Airport attributes ride along on the nodes.
G = nx.DiGraph()
for row in nodes.itertuples():
    G.add_node(row.Id, lat=row.latitude, lon=row.longitude, departures=row.departures_per_week,
               delay=row.delay_category, rate=row.delay_rate, food=row.food_category,
               layover=row.avg_layover_min)
for row in edges.itertuples():
    G.add_edge(row.Source, row.Target, weight=row.Weight)

print(G.number_of_nodes(), "airports,", G.number_of_edges(), "routes")

# 3. Where can you fly nonstop from Boston? successors() follows the arrows out.
from_bos = sorted(G.successors("BOS"))
print("\nNonstop from BOS:", ", ".join(from_bos))
print("Nonstop BOS to SEA:", G.has_edge("BOS", "SEA"))

# 4. Every one-connection route from Boston to Seattle, with what each connection costs.
print("\nBOS to SEA with one connection:")
print(f"   {'via':<4} {'BOS->X':>7} {'X->SEA':>7} {'delay':<7} {'layover':>7}")
for x in from_bos:
    if G.has_edge(x, "SEA"):
        print(f"   {x:<4} {G['BOS'][x]['weight']:>7} {G[x]['SEA']['weight']:>7} "
              f"{G.nodes[x]['delay']:<7} {G.nodes[x]['layover']:>7}")

# 5. The hubs. Weighted degree adds up the flights on every route in and out.
weighted = dict(G.degree(weight="weight"))
print("\nBusiest airports (flights in and out per week):")
for code in sorted(weighted, key=weighted.get, reverse=True)[:5]:
    print(f"   {code} {weighted[code]}")

# 6. Draw it as a map. Longitude is x, latitude is y. No layout algorithm needed.
#    One dictionary per attribute maps each value to a color. Edit the colors
#    here. Every value the attribute takes needs an entry.

# color_by = "delay"
colors_delay = {"Low": "tab:green",
                "Medium": "tab:orange",
                "High": "tab:red"}

# color_by = "food"
colors_food = {"Healthy": "tab:green",
               "Mixed": "tab:orange",
               "Unhealthy": "tab:red"}

# Change these two lines to recolor the map. color_by is the attribute name
# carried on the nodes in block 2 (delay or food), and colors is the
# dictionary that goes with it.
color_by = "delay"
colors = colors_delay

pos = {code: (G.nodes[code]["lon"], G.nodes[code]["lat"]) for code in G}
plt.figure(figsize=(11, 6))
nx.draw_networkx_edges(G, pos, arrows=False, edge_color="lightgray",
                       width=[G[u][v]["weight"] / 10 for u, v in G.edges])
nx.draw_networkx_nodes(G, pos, node_color=[colors[G.nodes[c][color_by]] for c in G],
                       node_size=[G.nodes[c]["departures"] * 2 for c in G])
nx.draw_networkx_labels(G, pos, font_size=8)

# A legend built from the dictionary in use, so it always matches the map.
for value, color in colors.items():
    plt.scatter([], [], c=color, label=value)
plt.legend(loc="lower left", fontsize=8, title=color_by)

plt.title(f"Flights per week (edge width), departures (node size), colored by {color_by}")
plt.axis("off")
plt.savefig(OUT / "airport_flights.png", dpi=120, bbox_inches="tight")
plt.show()
