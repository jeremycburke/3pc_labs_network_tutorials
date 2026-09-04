# Solution: getting from Boston to Seattle

Panel names are from Gephi 0.11. Start from `solution/airport_flights.gexf` (File > Open) or from your own import of the clean CSVs.

## Gephi walkthrough

### Map layout

1. Layout panel, **Geo Layout**. Latitude `latitude`, Longitude `longitude`, projection Mercator. Run. (The GEXF is already laid out this way.)
2. Appearance, Nodes, size, Ranking, `departures_per_week`, min 10, max 60. Apply.
3. Appearance, Nodes, color, Partition, `delay_category`. Apply. Pick red for High, amber for Medium, green for Low by clicking the color swatches.

What the map shows. The four High airports are the three big coastal hubs plus Chicago: EWR 0.34, ORD 0.33, JFK 0.31, SFO 0.30. Low delays are in the middle of the country and the northwest: MSP 0.07, SLC 0.10, DEN 0.12, PHX 0.12, CLT 0.12, SEA 0.13, DTW 0.14. Everything else is Medium, between 0.19 and 0.24.

4. Color by `food_category`. Healthy: BOS, DEN, MSP, SEA (0.80 each), SFO, SLC (0.67). Mixed: ATL, DTW, LAX, PHL (0.50), IAD, JFK (0.40). Unhealthy: CLT, DFW, IAH, MIA (0.20), EWR, LAS (0.33), ORD, PHX (0.17). There is a loose pattern, west and north healthier, but it is loose, and students should say so rather than invent a story.

### Ego networks

5. Filters, Library, **Topology > Ego Network**. Drag it into the query, Node ID `BOS`, Depth 1. Filter. Nine airports light up: JFK, IAD, ATL, ORD, DTW, MSP, DEN, DFW, SFO.
6. Change the Node ID to `SEA`. Ten: JFK, ATL, ORD, MSP, DFW, DEN, SLC, PHX, LAX, SFO.

In both lists: JFK, ATL, ORD, MSP, DFW, DEN, SFO. Those seven are the possible connections.

### Choosing a connection

7. Data Laboratory, Edges tab. Filter or sort to find the two legs for each connection. Or hover an edge in the Overview to read its weight.

| Via | BOS to X | X to SEA | Delay rate at X | Category | Layover (min) |
|---|---|---|---|---|---|
| ORD | 26 | 15 | 0.33 | High | 50 |
| JFK | 29 | 8 | 0.31 | High | 85 |
| ATL | 20 | 15 | 0.21 | Medium | 45 |
| DFW | 14 | 13 | 0.22 | Medium | 60 |
| SFO | 12 | 23 | 0.30 | High | 70 |
| DEN | 8 | 16 | 0.12 | Low | 55 |
| MSP | 7 | 9 | 0.07 | Low | 90 |

There is no single right answer, which is the point.

- Most flights to choose from: ORD, then JFK. Both are High delay. If your first leg is late, the many onward flights are what save you.
- Fewest delays: MSP, then DEN. MSP has the longest layover and only one flight a day on each leg, so missing one costs a day. DEN has twice the flights and a 55-minute connection.
- The balanced pick: ATL. Medium delay, the shortest layover in the table, and a healthy number of flights on both legs. Gephi's shortest path tool also picks ATL, because it counts hops and all connections are two hops.

A reasonable recommendation for a nervous flyer is DEN. For someone who wants options, ORD.

### Edge weight

8. Filters, **Edges > Edge Weight**, range 20 to 35. Filter.

55 of the 144 edges remain: the New York to Los Angeles, San Francisco and Miami runs, the Chicago spokes, Atlanta's eight busiest routes, and the West Coast corridor. The heaviest edges in one direction are LAX to JFK (35), JFK to LAX (34), LAX to SFO (32), JFK to BOS (30), MIA to JFK (30). At this threshold five airports lose every edge: DTW, IAD, IAH, PHL and SLC.

### Hubs

9. Statistics, **Average Degree** and **Avg. Weighted Degree**. Size by Weighted Degree, then by Degree.

| Airport | Routes | Flights in and out per week |
|---|---|---|
| ORD | 15 | 599 |
| LAX | 12 | 533 |
| ATL | 13 | 529 |
| DEN | 14 | 473 |
| DFW | 11 | 392 |
| JFK | 7 | 333 |

JFK is the answer to "few routes, many flights": seven routes, but the seventh busiest airport by flights. The quiet end: IAD (3 routes, 86 flights), PHL (3, 93), DTW (4, 95), SLC (5, 114).

### Diameter

10. Statistics, **Network Diameter**, Directed. It reports 3, with an average path length of 1.63. Almost every pair is one or two hops apart. Only two pairs need two connections, and both involve Miami: EWR to MIA (Newark has no Miami flight and no flight to any of Miami's four partners except through Chicago or Houston) and MIA to MSP. Use the Shortest Path tool on EWR and MIA to see the three-hop route.

## Findings in one place

| Measure | Value |
|---|---|
| Airports, routes | 20, 144 (72 pairs, both directions) |
| Flights in the cleaned week | 2,541 |
| Cancelled | 67 |
| Delay categories | Low 7, Medium 9, High 4 |
| Food categories | Healthy 6, Mixed 6, Unhealthy 8 |
| Connections from BOS to SEA | 7 |
| Busiest airport | ORD, 599 flights in and out |
| Heaviest route | LAX to JFK, 35 flights |
| Average path length, diameter | 1.63, 3 |

## Notes for the instructor

The delay categories are the part students will argue about, which is useful. IAD sits at 0.21 and LAS at 0.19, so a threshold of 0.20 instead of 0.17 would move LAS into Low. Ask what a threshold is for before asking where it should go.

Each route appears as two edges. Gephi draws them as two curved arrows between the same pair. If the class finds that noisy, import the same edge file as Undirected with the Sum merge strategy, and the pairs collapse into one edge whose weight is flights in both directions. The delay-by-origin logic still works, because it lives on the nodes.
