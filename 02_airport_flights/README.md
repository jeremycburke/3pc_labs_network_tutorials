# Project 2: getting from Boston to Seattle

Twenty airports, from Boston and Miami to Seattle and San Francisco, and one week of departures between them. A directed edge from one airport to another is a route, and its weight is the number of flights that week. Each airport carries a delay rate (the share of departures that left 15 or more minutes late), a delay category, a food category (how much of the terminal's food is healthy), and a typical connection time.

The exercise: there is no nonstop from Boston to Seattle in this network. Seven airports connect the two. Which connection is best depends on what you care about: the most flights to choose from, the smallest chance of a delay, or the shortest layover. The graph shows all three at once.

Airport codes, names and coordinates are real. Flights, delays, layovers and food are invented. The carriers (AU, BW, SK, PR) do not exist.

## What you practice here

- Turn a log with one row per event into an edge list by counting rows per pair.
- Compute a node attribute from the same log and bucket it into a category.
- Split packed columns ("Atlanta, GA") and parse values written several ways ("1h05m").
- Lay nodes out on a map with the Geo Layout plugin.
- Filter by node attribute and by edge weight to narrow down a route.

## Files

| Path | What it is |
|---|---|
| `raw/flight_log_week.csv` | One row per departure, 2,569 rows including duplicates. Messy. |
| `raw/airport_info.csv` | One row per airport with location and coordinates packed into single columns. |
| `raw/airport_food.csv` | One row per food vendor per airport, rated Healthy or Unhealthy. |
| `clean/nodes.csv` | One row per airport with attributes. Import first. |
| `clean/edges.csv` | One row per route with flights per week. Import second. |
| `solution/airport_flights.gexf` | The finished graph with nodes already placed on a map. |
| `scripts/clean.py` | Python answer key. |
| `scripts/make_raw.py` | Instructor script that generates the raw files. |
| `CLEANING.md` | The cleaning tutorial. |
| `SOLUTION.md` | Gephi walkthrough and expected findings. |

## Column dictionary

`clean/nodes.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Id` | String | Three-letter airport code, ATL to SLC |
| `Label` | String | Airport name |
| `city`, `state` | String | |
| `latitude`, `longitude` | Double | Decimal degrees. Longitude is negative. |
| `departures_per_week` | Integer | 44 to 302 |
| `delay_rate` | Double | 0.07 to 0.34. Share of departures delayed 15 minutes or more. |
| `delay_category` | String | Low (under 0.17), Medium, High (0.27 and up) |
| `healthy_share` | Double | Share of the airport's food vendors rated Healthy |
| `food_category` | String | Healthy (0.60 and up), Mixed (0.40 to 0.59), Unhealthy (under 0.40) |
| `avg_layover_min` | Integer | Typical connection time, 45 to 90 |

`clean/edges.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Source` | String | Origin airport code |
| `Target` | String | Destination airport code |
| `Type` | String | Always `Directed` |
| `Weight` | Double | Flights that week, 7 to 35 |
| `avg_flight_min` | Integer | Average time in the air, 53 to 368 |

Every route exists in both directions, as two separate edges with slightly different counts.

## Importing into Gephi

1. File > New Project.
2. File > Import spreadsheet, `clean/nodes.csv`, Import as **Nodes table**. Next.
3. Set `latitude`, `longitude`, `delay_rate` and `healthy_share` to **Double**, and `departures_per_week` and `avg_layover_min` to **Integer**. Finish. Report: 20 nodes. OK.
4. File > Import spreadsheet, `clean/edges.csv`, Import as **Edges table**. Next.
5. `Weight` **Double**, `avg_flight_min` **Integer**. Finish. Report: Graph Type Directed, 144 edges. Choose **Append to existing workspace**. OK.

## Putting the airports on a map

Install the Geo Layout plugin first (Tools > Plugins > Available Plugins, search `GeoLayout`; see the top-level README). Then in the Layout panel choose **Geo Layout**, set Latitude to `latitude` and Longitude to `longitude`, pick the Mercator projection, and click Run. Boston should be top right, Seattle top left, Miami bottom right. If the graph is tiny or enormous, scroll to zoom, or run the **Expansion** or **Contraction** layout once.

If you skipped the plugin, open `solution/airport_flights.gexf` instead. It carries map positions.

## Exercises

1. Map layout. Size nodes by `departures_per_week` and color them by `delay_category`. Where are the delays?
2. Color by `food_category`. Is there a regional pattern, or none?
3. Filters, Topology > Ego Network on BOS with depth 1. Which airports have a nonstop from Boston? Do the same for SEA. Which airports are in both lists?
4. For each airport in both lists, write down the flights on each leg, the delay category, and the layover. Pick the connection you would recommend to a nervous flyer, and the one for someone who wants the most flights to choose from.
5. Filters, Edges > Edge Weight, keep 20 and up. Which routes remain? Which airports lose every edge?
6. Statistics > Avg. Weighted Degree. Size nodes by Weighted Degree. Compare with plain Degree. Which airports have few routes but a lot of flights?
7. Statistics > Network Diameter reports 3. Find a pair of airports that needs two connections. Miami is a good place to start.

Answers in `SOLUTION.md`.
