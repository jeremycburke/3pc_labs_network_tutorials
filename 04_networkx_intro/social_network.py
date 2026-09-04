"""
social_network.py

The friendship network from project 1, in code instead of Gephi.
Reads the two clean CSVs, asks three questions, draws the picture.

Run from anywhere:   python 04_networkx_intro/social_network.py
"""
from pathlib import Path

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent          # the 04_networkx_intro folder
DATA = HERE.parent / "01_social_network" / "clean"
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# 1. Read the two tables.
nodes = pd.read_csv(DATA / "nodes.csv")
edges = pd.read_csv(DATA / "edges.csv")

# 2. Build the graph. One node per row of nodes.csv, one arrow per row of edges.csv.
G = nx.DiGraph()
for row in nodes.itertuples():
    G.add_node(row.Id, name=row.Label, group=row.group, age=row.age,
               favorite_team=row.favorite_team, car=row.car, music=row.music)
for row in edges.itertuples():
    G.add_edge(row.Source, row.Target, weight=row.Weight, context=row.context)

print(G.number_of_nodes(), "people,", G.number_of_edges(), "friendships")

# 3. Who is the connector? Betweenness counts how many shortest paths pass through a person.
betweenness = nx.betweenness_centrality(G)
print("\nTop 3 by betweenness:")
for person in sorted(betweenness, key=betweenness.get, reverse=True)[:3]:
    print(f"   {G.nodes[person]['name']:<18} {betweenness[person]:.3f}")

# 4. Who gets named most? In-degree is the number of arrows pointing at a person.
in_degree = dict(G.in_degree())
print("\nTop 3 by in-degree:")
for person in sorted(in_degree, key=in_degree.get, reverse=True)[:3]:
    print(f"   {G.nodes[person]['name']:<18} {in_degree[person]}")

# 5. How do you get from a hiker to a book club member? Friendship runs both ways
#    for this question, so use the undirected copy of the graph.
U = G.to_undirected()
path = nx.shortest_path(U, "P06", "P43")
print("\nOwen Gallagher to Walter Osei:")
print("   " + " -> ".join(G.nodes[p]["name"] for p in path))

# 6. Find the communities and compare them with the real circles.
communities = nx.community.louvain_communities(U, weight="weight", seed=1)
print("\nCommunities found:", len(communities))
for members in communities:
    groups = sorted({G.nodes[m]["group"] for m in members})
    print(f"   {len(members)} people, from: {', '.join(groups)}")

# 7. Draw it. One dictionary per attribute maps each value to a color.
#    Edit the colors here. Every value the attribute takes needs an entry.

# color_by = "group"
colors_groups = {"Hiking club": "tab:green",
                 "Bakery coworkers": "tab:orange",
                 "College roommates": "tab:blue",
                 "Soccer league": "tab:red",
                 "Book club": "tab:purple"}
# color_by = "favorite_team"
colors_teams = {"Cubs": "tab:blue",
                "Bears": "tab:orange",
                "White Sox": "black",
                "Bulls": "tab:red",
                "Fire": "tab:green",
                "No team": "lightgray"}
# color_by = "car"
colors_cars = {"Subaru Outback": "tab:green",
               "Toyota Corolla": "tab:blue",
               "Honda Civic": "tab:orange",
               "Ford F-150": "tab:red",
               "Tesla Model 3": "tab:purple",
               "No car": "lightgray"}

# color_by = "music"
colors_music = {"Indie rock": "tab:green",
                "Country": "tab:brown",
                "Hip-hop": "tab:red",
                "Pop": "tab:pink",
                "Jazz": "tab:blue",
                "Classical": "tab:purple",
                "Electronic": "tab:cyan"}

# Change these two lines to recolor the picture. color_by is the attribute name
# carried on the nodes in block 2 (group, favorite_team, car or music), and
# colors is the dictionary that goes with it.
color_by = "car"
colors = colors_cars

pos = nx.spring_layout(U, seed=7)
plt.figure(figsize=(9, 7))

nx.draw(G, pos, node_color=[colors[G.nodes[n][color_by]] for n in G],
        node_size=90, arrows=False, width=0.5, edge_color="gray")

top = max(betweenness, key=betweenness.get)
nx.draw_networkx_labels(G, pos, labels={top: G.nodes[top]["name"]}, font_size=10)

# A legend built from the dictionary in use, so it always matches the picture.
for value, color in colors.items():
    plt.scatter([], [], c=color, label=value)
plt.legend(loc="lower left", fontsize=8, title=color_by)

plt.title(f"Who knows whom: colored by {color_by}")
plt.savefig(OUT / "social_network.png", dpi=120, bbox_inches="tight")
plt.show()
