# Project 4: the same three graphs, in code

Gephi is for looking. Code is for repeating. Once you know what you want to see, a script that reads the data, computes the answer and draws the picture is thirty lines, and it will do the same thing next week on next week's data. This project reopens the three clean datasets from projects 1 to 3 in Python with networkx and answers the same questions the Gephi solutions answer.

Nothing here needs to be cleaned. The scripts read `clean/nodes.csv` and `clean/edges.csv` from the other three folders. If you have not done those projects, that is fine; the clean files ship with the repo.

## Files

| Path | What it is |
|---|---|
| `social_network.py` | Project 1: who is the connector, who gets named most, the path from a hiker to a reader, the communities. |
| `airport_flights.py` | Project 2: the Boston to Seattle connections, the hubs, a map. |
| `citibike_stations.py` | Project 3: the full and empty docks, where bikes arrive and leave, the truck route, a map. |
| `output/` | The pictures the scripts draw. |
| `SOLUTION.md` | What each script prints, and answers to the exercises. |

## Setup

Python 3.10 or newer. Open a terminal in the top folder of the repo (the one with `requirements.txt` in it).

If you are using a virtual environment, create it once and activate it. Windows, in PowerShell:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

The prompt starts with `(.venv)` when it is active. You need the activate command again in every new terminal. If you are not using a virtual environment, skip this; the top-level README explains when it is worth it.

Either way, install the three packages once:

```bash
pip install -r requirements.txt
```

That installs pandas (reads CSVs), networkx (the graph), and matplotlib (the drawing). Then run a script:

```bash
python 04_networkx_intro/social_network.py
```

Each script prints a few lines, opens a window with the picture, and saves the same picture to `output/`. Close the window to end the script.

If it fails with `No module named pandas`, the packages went into a different Python than the one running the script. Usually the virtual environment is not active in this terminal.

If no window opens, the picture is still saved in `output/`. Some terminals and remote desktops cannot show one.

## The pattern

All three scripts have the same five parts. Once you can read one, you can read the others.

1. **Read the two tables** with `pd.read_csv`. Same files Gephi imported.
2. **Build the graph.** `nx.DiGraph()` makes an empty directed graph. One loop adds a node per row of `nodes.csv`, carrying the attributes you care about. A second loop adds an edge per row of `edges.csv`, carrying the weight. This is the import wizard in six lines.
3. **Ask questions.** Each is one call: `nx.betweenness_centrality(G)`, `nx.shortest_path(G, a, b)`, `G.in_degree()`, `G.successors(node)`. The result is a dictionary or a list, and the rest of the block is just printing it.
4. **Position the nodes.** Project 1 uses `nx.spring_layout`, which is the same family of algorithm as ForceAtlas 2. Projects 2 and 3 skip the algorithm and use longitude as x and latitude as y, which is what the Geo Layout plugin does.
5. **Draw.** `nx.draw` or its three pieces (`draw_networkx_edges`, `draw_networkx_nodes`, `draw_networkx_labels`) take lists of colors and sizes, one per node or edge. Building those lists is where the Appearance panel's Partition and Ranking live: a dictionary from category to color, or an attribute multiplied by a number.

## Walking through the first script

Open `social_network.py` next to this page.

**Lines 1 to 20.** Imports and paths. `HERE` is the folder the script lives in, so `HERE.parent / "01_social_network" / "clean"` finds the data no matter where you run the script from.

**Build the graph.** `row.Id`, `row.Label` and so on are the columns of the CSV. `G.add_node(row.Id, name=row.Label, group=row.group)` stores the name and group on the node so you can get them back later with `G.nodes[id]["name"]`. Note that the node's identity is the id, not the name, exactly as in Gephi.

**Betweenness.** `nx.betweenness_centrality(G)` returns a dictionary from id to score. `sorted(betweenness, key=betweenness.get, reverse=True)` sorts the ids by their score, highest first. `[:3]` keeps three.

**In-degree.** `G.in_degree()` gives pairs of (id, count). `dict()` turns it into the same shape as the betweenness dictionary so the same sorting line works.

**Shortest path.** `G.to_undirected()` makes a copy where the arrows have no direction. Friendship counts both ways for this question. The path comes back as a list of ids; the print turns each id into a name.

**Communities.** `nx.community.louvain_communities` is the same algorithm as Gephi's Modularity. `seed=1` makes it give the same answer every run. Gephi randomizes; this does not have to.

**Drawing.** There are four dictionaries, one per attribute: `colors_groups`, `colors_teams`, `colors_cars` and `colors_music`. Each maps every value of that attribute to a color name. Two lines below them choose which one is in use: `color_by = "group"` names the attribute, and `colors = colors_groups` names the dictionary. To recolor by music, change those to `"music"` and `colors_music`. To change a color, edit the dictionary. The list comprehension `[colors[G.nodes[n][color_by]] for n in G]` walks the nodes in order and looks up each one's color, which is what `nx.draw` needs. The legend is built from the same dictionary, so it cannot disagree with the picture. `draw_networkx_labels` with a one-entry dictionary labels only the connector.

Color names are matplotlib's: `tab:blue`, `tab:orange` and the other eight `tab:` colors, plain names like `black` or `lightgray`, or a hex code like `"#1f77b4"`.

## What is different in the other two

`airport_flights.py` builds the position dictionary from coordinates: `pos = {code: (lon, lat) for code in G}`. Edge width is a list, `weight / 10` per edge. Node size is `departures * 2`. The three drawing calls are separate so each can have its own styling. The color switch works as in the first script, with two dictionaries: `colors_delay` (`color_by = "delay"`) and `colors_food` (`color_by = "food"`).

`citibike_stations.py` reads the id columns as text (`dtype={"Id": str}`) because ids like `6000.10` would otherwise lose their zero. It draws only the edges with 10 or more trips, by building a list `heavy` and passing it as `edgelist`. Its color switch has three settings. `"pattern"` and `"neighborhood"` are categories and use dictionaries like the other scripts. `"net"` is a number, so it goes through a blue-to-red colormap with a colorbar instead of a dictionary; that is the Ranking mode of the Appearance panel, and the `if` around the node-drawing call is what tells the two apart. The small `km_apart` function is the only arithmetic in the project.

Above every dictionary is a comment stating the `color_by` value that goes with it, so switching is a matter of copying that value into the `color_by` line and the dictionary's name into the `colors` line.

## Exercises

Each one is a change of a line or two. Answers are in `SOLUTION.md`.

`social_network.py`

1. Change the path to run from Maren Lindqvist (P01) to Victor Nakamura (P36). Who is in the middle?
2. Size the nodes by in-degree: replace `node_size=90` with a list, `[in_degree[n] * 40 + 20 for n in G]`. Who gets big? Why the `+ 20`?
3. Count the friendships that cross circles. One line: a `sum` over `G.edges` comparing the two endpoints' groups.
4. Remove Priya with `G.remove_node("P11")` before the betweenness block. Who is the connector now? Does the top score drop?

`airport_flights.py`

5. List the airports with a nonstop to Seattle. Same as the Boston line, but `predecessors` instead of `successors`.
6. Of the seven connections, find the one with the lowest delay rate in code, using the `rate` attribute and `min` with a `key`.
7. `nx.diameter(G)` is 3. Which pairs of airports are three hops apart? Loop over pairs with `nx.shortest_path_length`.
8. Color the airports by `food` instead of `delay`, using the two switch lines. Then add a third dictionary for `state` and see why it is a bad idea.

`citibike_stations.py`

9. Change the drawing cutoff from 10 trips to 5. How many flows are drawn now?
10. List the stations that lost more than 20 bikes over the week (`net` below -20).
11. Find the single heaviest flow with `max` over `G.edges`.
12. Find the fewest-hops route from E 75 St & 3 Ave to Broadway & Battery Pl with `nx.shortest_path`. Then rerun it with `weight=lambda u, v, d: 1 / d["weight"]` so heavy flows count as short, and compare.

## The calls used, in one place

| Call | What it gives you |
|---|---|
| `nx.DiGraph()` | An empty directed graph |
| `G.add_node(id, key=value, ...)` | A node with attributes |
| `G.add_edge(a, b, weight=w)` | An edge with attributes |
| `G.nodes[id]["key"]` | A node attribute back |
| `G[a][b]["weight"]` | An edge attribute back |
| `G.successors(a)`, `G.predecessors(a)` | Arrows out of, into, a node |
| `G.has_edge(a, b)` | True or False |
| `G.in_degree()`, `G.out_degree()`, `G.degree(weight="weight")` | Degree per node, weighted or not |
| `G.to_undirected()` | A copy with no arrow directions |
| `nx.betweenness_centrality(G)` | Score per node |
| `nx.shortest_path(G, a, b)` | List of nodes |
| `nx.diameter(G)`, `nx.average_shortest_path_length(G)` | One number each |
| `nx.community.louvain_communities(G, seed=1)` | List of sets of nodes |
| `nx.spring_layout(G, seed=7)` | Position per node |
| `nx.draw(G, pos, node_color=..., node_size=...)` | The picture |
