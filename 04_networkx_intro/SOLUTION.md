# Solution: the same three graphs, in code

Every number below matches the Gephi solution for the same project. That is the check: if your script prints something different from the Gephi walkthrough, one of the two is wrong, and it is worth finding out which.

## What the scripts print

`social_network.py`

```
50 people, 160 friendships

Top 3 by betweenness:
   Priya Natarajan    0.486
   Miriam Feldman     0.307
   Nadia Petrov       0.231

Top 3 by in-degree:
   Priya Natarajan    6
   Sofia Marchetti    6
   Chloe Adebayo      6

Owen Gallagher to Walter Osei:
   Owen Gallagher -> Caleb Marsh -> Felix Baumann -> Gordon Hale -> Walter Osei

Communities found: 5
   10 people, from: Hiking club
   10 people, from: Bakery coworkers
   10 people, from: College roommates
   10 people, from: Soccer league
   10 people, from: Book club
```

The picture in `output/social_network.png` shows five clumps, one color each, with Priya labeled where the orange bakery cluster touches the others. Gephi's betweenness is unnormalized by default, so its numbers are bigger, but the order is the same.

`airport_flights.py`

```
20 airports, 144 routes

Nonstop from BOS: ATL, DEN, DFW, DTW, IAD, JFK, MSP, ORD, SFO
Nonstop BOS to SEA: False

BOS to SEA with one connection:
   via   BOS->X  X->SEA delay   layover
   ATL       20      15 Medium       45
   DEN        8      16 Low          55
   DFW       14      13 Medium       60
   JFK       29       8 High         85
   MSP        7       9 Low          90
   ORD       26      15 High         50
   SFO       12      23 High         70

Busiest airports (flights in and out per week):
   ORD 599
   LAX 533
   ATL 529
   DEN 473
   DFW 392
```

`output/airport_flights.png` is the map: red high-delay hubs at Chicago, Newark, Kennedy and San Francisco, green low-delay airports across the middle and northwest, edge width by flights. Newark and Kennedy overlap because they are 30 km apart on a map of the whole country. Gephi has the same problem; the Geo Layout plugin does not move labels either.

`citibike_stations.py` (the two long station lists are wrapped here; the script prints each on one line)

```
30 stations, 287 flows

Often full: 6 Ave & W 33 St, Broadway & W 41 St, Cleveland Pl & Spring St, Pershing Square North,
            Vesey Pl & River Terrace, W 33 St & 7 Ave, W 41 St & 8 Ave, W 45 St & 6 Ave
Often empty: 1 Ave & E 68 St, Broadway & E 14 St, Carmine St & 6 Ave, Christopher St & Greenwich St,
             E 17 St & Broadway, E 7 St & Avenue A, E 72 St & York Ave, Lafayette St & E 8 St,
             Lexington Ave & E 63 St

Most trips arriving: Pershing Square North, W 41 St & 8 Ave, W 33 St & 7 Ave
Most trips leaving: Pershing Square North, Broadway & W 41 St, Broadway & E 14 St

Truck route: take bikes from -> bring them to (km)
   6 Ave & W 33 St              -> E 17 St & Broadway           1.3
   Broadway & W 41 St           -> Lexington Ave & E 63 St      2.0
   Cleveland Pl & Spring St     -> Carmine St & 6 Ave           1.0
   Pershing Square North        -> Lexington Ave & E 63 St      1.7
   Vesey Pl & River Terrace     -> Carmine St & 6 Ave           2.0
   W 33 St & 7 Ave              -> E 17 St & Broadway           1.5
   W 41 St & 8 Ave              -> E 17 St & Broadway           2.1
   W 45 St & 6 Ave              -> Lexington Ave & E 63 St      1.6
```

`output/citibike_stations.png` is Manhattan with north at the top: dark blue docks in Midtown gaining bikes, dark red docks on the Upper East Side and around Union Square losing them, and only the flows of 10 or more trips drawn. The often-full and often-empty stations are labeled; the balanced ones are not, which keeps the map readable.

## Exercise answers

### social_network.py

**1. Maren to Victor.** Change `"P06", "P43"` to `"P01", "P36"`.

```
Maren Lindqvist -> Ingrid Solberg -> Zoë Fischer -> Kwame Mensah -> Victor Nakamura
```

Zoë is the hiker who also plays soccer. Four steps, same as Owen to Walter.

**2. Size by in-degree.** `node_size=[in_degree[n] * 40 + 20 for n in G]`. The `in_degree` dictionary is already built in block 4. Priya, Sofia Marchetti, Chloe Adebayo and Miriam Feldman get the largest circles, all at 6. The `+ 20` is there for Jamal Reed: nobody named him, his in-degree is 0, and without the constant his node has size zero and disappears from the picture. Gephi's Ranking has the same trap, which is why its size dialog has a minimum.

**3. Friendships that cross circles.**

```python
crossing = sum(1 for u, v in G.edges if G.nodes[u]["group"] != G.nodes[v]["group"])
print(crossing, "of", G.number_of_edges(), "friendships cross a circle")
```

18 of 160. Everything else is inside a circle, which is why the layout separates them so cleanly.

**4. Without Priya.** Put `G.remove_node("P11")` right after the graph is built.

```
Zoë Fischer        0.482
Sam Okafor         0.479
Michael Torres     0.456
```

The score does not drop. Zoë's number is about the same as Priya's was. With Priya gone, every path from the bakery to the soccer league or the book club has to go the long way round through the college roommates, and it passes through the remaining bridges: Zoë (hiking to soccer), Sam Okafor and Michael Torres (soccer to college). Betweenness measures how much of the traffic runs through you, and removing one bridge makes the others busier.

### airport_flights.py

**5. Nonstops to Seattle.** `sorted(G.predecessors("SEA"))` gives ten: ATL, DEN, DFW, JFK, LAX, MSP, ORD, PHX, SFO, SLC. Boston has nine outbound. Seven are on both lists, and those are the connections.

**6. Lowest delay rate in code.**

```python
connections = [x for x in G.successors("BOS") if G.has_edge(x, "SEA")]
best = min(connections, key=lambda x: G.nodes[x]["rate"])
print(best, G.nodes[best]["rate"])
```

MSP, 0.07. DEN is next at 0.12. The script prints the category (Low) rather than the rate; the rate is on the node as `rate`.

**7. Three hops apart.**

```python
for a in G:
    for b in G:
        if a != b and nx.shortest_path_length(G, a, b) == 3:
            print(a, "->", b)
```

Four pairs, two in each direction: EWR to MIA, MIA to EWR, MIA to MSP, MSP to MIA. Miami has only four routes (JFK, ATL, DFW, LAX) and none of them connects in one hop to Newark or Minneapolis.

**8. Color by food.** Change the two switch lines to `color_by = "food"` and `colors = colors_food`. Six green, six orange, eight red. Look at whether the red ones cluster anywhere. They do not, much.

A `state` dictionary needs 16 entries for 20 airports, and no reader can hold 16 colors apart. Categories with more than about eight values do not work as colors, in code or in Gephi. Group them first (regions, say) or size by something else.

### citibike_stations.py

**9. Cutoff of 5.** Change `>= 10` to `>= 5` in the `heavy` line. 246 of the 287 flows are drawn instead of 130, and the map turns into a thicket. That is the argument for the cutoff.

**10. Lost more than 20 bikes.**

```python
for s in G:
    if G.nodes[s]["net"] < -20:
        print(G.nodes[s]["name"], G.nodes[s]["net"])
```

Seven stations: Lexington Ave & E 63 St (-49), E 17 St & Broadway (-40), Christopher St & Greenwich St (-29), Broadway & E 14 St (-26), Broadway & W 41 St (-25), E 75 St & 3 Ave (-22), W 17 St & 8 Ave (-22). Five are in the often-empty list. Broadway & W 41 St is an often-full Midtown dock that still loses bikes over the week, the case project 3's solution discusses. W 17 St & 8 Ave and E 75 St & 3 Ave are losing bikes without ever quite running out.

**11. The heaviest flow.**

```python
u, v = max(G.edges, key=lambda uv: G[uv[0]][uv[1]]["weight"])
print(G.nodes[u]["name"], "->", G.nodes[v]["name"], G[u][v]["weight"])
```

Lexington Ave & E 63 St to W 41 St & 8 Ave, 26 trips. The morning commute from the Upper East Side to Midtown, in one edge.

**12. Fewest hops, then heaviest flows.** The ids are `6186.15` (E 75 St & 3 Ave) and `6881.14` (Broadway & Battery Pl); the script stores names on the nodes, so you can also look them up from `nodes`.

```python
print(nx.shortest_path(G, "6186.15", "6881.14"))
print(nx.shortest_path(G, "6186.15", "6881.14", weight=lambda u, v, d: 1 / d["weight"]))
```

Fewest hops, three: E 75 St & 3 Ave, 6 Ave & W 33 St, E 7 St & Avenue A, Broadway & Battery Pl. Its three legs carry 6, 5 and 4 trips a week, thin flows that a few people happen to ride.

Preferring heavy flows, five hops: E 75 St & 3 Ave, 1 Ave & E 68 St, 6 Ave & W 33 St, Broadway & E 14 St, Vesey Pl & River Terrace, Broadway & Battery Pl. Its legs carry 13, 12, 14, 16 and 10 trips. Longer, but every leg is a flow people ride every day. Which one is "shortest" depends on what you tell the algorithm a step costs. The same choice sits behind every route planner.

## Notes for the instructor

The scripts are deliberately flat: no functions except `km_apart`, no classes, no argument parsing. Students who have seen a for loop and a dictionary can read them. The temptation to tidy them into something more general is real and should be resisted until after the class.

`verify_all.py` at the top level runs all three scripts headless and checks that each writes its picture, so a change to the clean data that breaks a script shows up there.

If matplotlib opens no window (common over remote desktop), the picture is still saved to `output/`. Point students there.
