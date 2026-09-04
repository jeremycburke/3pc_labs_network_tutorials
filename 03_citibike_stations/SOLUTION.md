# Solution: where the bikes pile up

Panel names are from Gephi 0.11. Start from `solution/citibike_stations.gexf` or from your own import of the clean CSVs.

## Gephi walkthrough

### The base map

1. Layout, **Geo Layout**, `latitude` and `longitude`, Mercator, Run.
2. Appearance, Nodes, size, Ranking, `capacity`, min 10, max 40. Apply.
3. Appearance, Nodes, color, Partition, `neighborhood`. Apply.

Midtown at the top center, the Upper East Side above and to the right, Chelsea to the left, the Village below, Lower Manhattan at the bottom.

### Full and empty

4. Color by Partition, `status_pattern`.

| Pattern | Stations |
|---|---|
| Often full (8) | W 41 St & 8 Ave, 6 Ave & W 33 St, W 33 St & 7 Ave, Broadway & W 41 St, Pershing Square North, W 45 St & 6 Ave (all Midtown); Vesey Pl & River Terrace, Cleveland Pl & Spring St (Lower Manhattan) |
| Often empty (9) | Broadway & E 14 St, Carmine St & 6 Ave, Christopher St & Greenwich St, E 17 St & Broadway, Lafayette St & E 8 St, E 7 St & Avenue A (Village); Lexington Ave & E 63 St, 1 Ave & E 68 St, E 72 St & York Ave (Upper East Side) |
| Swings both ways (1) | University Pl & E 14 St |
| Balanced (12) | All six Chelsea stations, three in Lower Manhattan, two in Midtown, E 75 St & 3 Ave |

The split is by neighborhood, and it is the commute. Office districts fill, residential districts empty, and Chelsea in between does neither. University Pl & E 14 St is the exception: it sits on Union Square, empties through the working day like the rest of the Village, and then fills in the evening and stays full overnight as people ride in to the square and leave the bikes there. It was full 18 percent of the readings and empty 18 percent.

By neighborhood, the mean share of readings full and empty:

| Neighborhood | Full | Empty | Net flow, all stations |
|---|---|---|---|
| Midtown | 0.17 | 0.03 | +185 |
| Lower Manhattan | 0.12 | 0.03 | +51 |
| Chelsea | 0.00 | 0.02 | -29 |
| Upper East Side | 0.03 | 0.16 | -91 |
| Village | 0.10 | 0.19 | -116 |

### Net flow

5. Appearance, Nodes, color, Ranking, `net_flow`. Pick a two-color gradient, say blue for negative and orange for positive. Apply.

Biggest gains: E 43 St & Vanderbilt Ave +52, W 41 St & 8 Ave +43, Pershing Square North +34. Biggest losses: Lexington Ave & E 63 St -49, E 17 St & Broadway -40, Christopher St & Greenwich St -29.

Now the two cases exercise 3 asks about.

- **Broadway & W 41 St** is often full (18 percent of readings) yet lost 25 bikes over the week. It fills in the morning rush and then keeps losing bikes through the afternoon and evening, because it is where people pick up a bike to go home or to dinner. Full is a state at a moment. Net flow is a total over the week. A station can have both.
- **E 43 St & Vanderbilt Ave** gained the most bikes of any station, 52, but was full only 12.5 percent of the readings, under the line. Its arrivals bunch in the morning rush the same way W 41 St's do, but it spends fewer hours each weekday at the limit. Net flow adds up over the week; time at the limit counts hours. The truck should still visit it, and the category missed it because a threshold is a blunt tool.

### Flows

6. Filters, **Edges > Edge Weight**, 10 to 26. Filter. 130 of the 287 edges remain.

Heaviest flows:

| From | To | Trips | Minutes |
|---|---|---|---|
| Lexington Ave & E 63 St | W 41 St & 8 Ave | 26 | 14.2 |
| Broadway & W 41 St | W 41 St & 8 Ave | 25 | 4.3 |
| Pershing Square North | E 43 St & Vanderbilt Ave | 24 | 3.0 |
| Broadway & W 41 St | W 33 St & 7 Ave | 22 | 6.0 |
| Lexington Ave & E 63 St | E 43 St & Vanderbilt Ave | 21 | 10.8 |
| Cleveland Pl & Spring St | Lafayette St & E 8 St | 21 | 8.3 |

Two kinds of heavy flow: the long commute from the Upper East Side into Midtown, and short hops between Midtown docks a few blocks apart (people docking at the nearest free slot to where they are going). Coloring edges by `ebike_share` is worth doing once to see what an attribute with no pattern looks like: the share sits near 0.3 on short and long flows alike. In this data the choice of bike is random. In real Citi Bike data it is not, and the same coloring would show something.

### In-degree and out-degree

7. Statistics, **Average Degree** and **Avg. Weighted Degree**. Size by Weighted In-Degree, then by Weighted Out-Degree.

Weighted in-degree leaders (trips arriving, counting only the 287 kept flows): Pershing Square North 193, W 41 St & 8 Ave 173, W 33 St & 7 Ave 159. Weighted out-degree leaders: Pershing Square North 163, Broadway & W 41 St 154, Broadway & E 14 St 147.

Pershing Square North, outside Grand Central, leads both lists. It is the busiest dock in the network in both directions, which is why it is often full and still only +34 for the week. The Village stations show up on the out side and not the in side. That asymmetry is the whole story of the network in two numbers.

### An ego network

8. Filters, **Topology > Ego Network**, Node ID `6419.19` (W 41 St & 8 Ave), depth 1. Filter.

Its bikes come from Lexington Ave & E 63 St (26), Broadway & W 41 St (25), Lafayette St & E 8 St (20), Pershing Square North (18) and E 17 St & Broadway (15), then a ring of smaller Midtown neighbors. Three of its five biggest sources are often-empty stations a mile or two away. The dock fills with bikes that came from exactly the places that run dry.

### The plan

9. For each often-full station, the nearest often-empty one by straight-line distance. `scripts/clean.py` prints this table.

| Take bikes from | Bring them to | km |
|---|---|---|
| Cleveland Pl & Spring St | Carmine St & 6 Ave | 1.0 |
| 6 Ave & W 33 St | E 17 St & Broadway | 1.3 |
| W 33 St & 7 Ave | E 17 St & Broadway | 1.5 |
| W 45 St & 6 Ave | Lexington Ave & E 63 St | 1.6 |
| Pershing Square North | Lexington Ave & E 63 St | 1.7 |
| Broadway & W 41 St | Lexington Ave & E 63 St | 2.0 |
| Vesey Pl & River Terrace | Carmine St & 6 Ave | 2.0 |
| W 41 St & 8 Ave | E 17 St & Broadway | 2.1 |

A better plan groups these: one truck loads at the three Midtown docks on 33rd and 41st and unloads at E 17 St & Broadway and Broadway & E 14 St; a second loads at Pershing Square and W 45 St and runs up to Lexington Ave & E 63 St; a third handles Lower Manhattan to the west Village. Ask the class whether the truck should also visit E 43 St & Vanderbilt Ave, which is not on the list.

## Findings in one place

| Measure | Value |
|---|---|
| Stations, flows | 30, 287 (of 433 pairs seen) |
| Trips kept, trips in kept flows | 2,851, 2,671 |
| Often full, often empty, swings, balanced | 8, 9, 1, 12 |
| Largest net gain | E 43 St & Vanderbilt Ave, +52 |
| Largest net loss | Lexington Ave & E 63 St, -49 |
| Heaviest flow | Lexington Ave & E 63 St to W 41 St & 8 Ave, 26 trips |
| Busiest dock both ways | Pershing Square North |
| Flows with 10 or more trips | 130 |

## Notes for the instructor

The 15 percent threshold and the 3-trip cutoff are both in the first twenty lines of `scripts/clean.py`. Changing either and rerunning is a two-minute demonstration of how much a categorical attribute depends on the rule that made it. At 20 percent only five stations qualify as often full or often empty; at 10 percent, most of Midtown and the Village do.

Gephi's weighted degree only counts the 287 kept flows, so it is smaller than `departures` and `arrivals` on the nodes, which count all 2,851 trips. Students who compare the two will notice, and the explanation is the cutoff.
