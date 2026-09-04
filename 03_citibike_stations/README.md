# Project 3: where the bikes pile up

Thirty Citi Bike stations in Manhattan, from the Upper East Side down to Battery Park, and one week of rides between them. A directed edge from one station to another is a flow: the number of trips that started at the first dock and ended at the second. Each station carries its capacity, how many trips left and arrived, the difference between those two numbers, and how much of the week it spent completely full or completely empty.

The exercise is the one the rebalancing crew faces every night. Bikes ride downtown in the morning and only some of them ride back. By afternoon the Midtown docks have no free slots and the Village docks have no bikes. Which stations need a truck, and where should the truck take the bikes?

The station names are real Citi Bike stations. The coordinates are approximate. Every trip and every dock reading is invented, and the trip file copies the column layout Citi Bike publishes so the cleaning steps carry over to the real thing.

## What you practice here

- Aggregate a trip log into flows and drop the noise.
- Compute node attributes from two different tables and join them.
- Distinguish a net imbalance over a week from hours spent at the limit.
- Use in-degree and out-degree separately, because in a flow network they mean different things.
- Turn a graph into an operational plan.

## Files

| Path | What it is |
|---|---|
| `raw/station_information.csv` | The tidy station table: id, name, neighborhood, coordinates, capacity. 30 rows. |
| `raw/citibike_trips_sample.csv` | One row per trip in Citi Bike's public column layout. 2,950 rows including duplicates. Messy. |
| `raw/station_status_snapshots.csv` | One row per station per hour: bikes docked, docks free, capacity. 5,040 rows. |
| `clean/nodes.csv` | One row per station with attributes. Import first. |
| `clean/edges.csv` | One row per flow with the trip count. Import second. |
| `solution/citibike_stations.gexf` | The finished graph with stations placed on a map. |
| `scripts/clean.py` | Python answer key. |
| `scripts/make_raw.py` | Instructor script that generates the raw files. |
| `CLEANING.md` | The cleaning tutorial. |
| `SOLUTION.md` | Gephi walkthrough and expected findings. |

## Column dictionary

`clean/nodes.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Id` | String | Citi Bike style station id, such as `6419.19`. Keep it as text. |
| `Label` | String | Station name |
| `neighborhood` | String | Midtown, Chelsea, Village, Lower Manhattan, Upper East Side |
| `latitude`, `longitude` | Double | Decimal degrees |
| `capacity` | Integer | Docks at the station, 30 to 60 |
| `departures` | Integer | Trips that started here during the week |
| `arrivals` | Integer | Trips that ended here |
| `net_flow` | Integer | Arrivals minus departures. Positive means bikes accumulate. |
| `pct_time_full` | Double | Share of the 168 hourly readings with no free dock |
| `pct_time_empty` | Double | Share with no bike |
| `status_pattern` | String | Often full, Often empty, Swings both ways, Balanced |

`clean/edges.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Source` | String | Station where the trip started |
| `Target` | String | Station where it ended |
| `Type` | String | Always `Directed` |
| `Weight` | Double | Trips that week, 3 to 26. Pairs with fewer than 3 trips are left out. |
| `avg_duration_min` | Double | Mean ride length, 3 to 34 minutes |
| `ebike_share` | Double | Share of those trips on an electric bike |

## Importing into Gephi

1. File > New Project.
2. File > Import spreadsheet, `clean/nodes.csv`, Import as **Nodes table**. Next.
3. Leave `Id` as String. Set `latitude`, `longitude`, `pct_time_full` and `pct_time_empty` to **Double**; `capacity`, `departures`, `arrivals` and `net_flow` to **Integer**. Finish. Report: 30 nodes. OK.
4. File > Import spreadsheet, `clean/edges.csv`, Import as **Edges table**. Next.
5. `Weight`, `avg_duration_min` and `ebike_share` **Double**. Finish. Report: Directed, 287 edges. Choose **Append to existing workspace**. OK.

Map layout: Layout panel, **Geo Layout**, latitude and longitude columns, Mercator, Run. The Upper East Side should be at the top right and Battery Park at the bottom left. Or open the GEXF, which is already placed.

## Exercises

1. Map layout. Size nodes by `capacity`, color by `neighborhood`. This is the base map; every other exercise is a recoloring of it.
2. Color by `status_pattern`. Where are the often-full stations, and where are the often-empty ones? What is different about the one that swings both ways?
3. Color by `net_flow` using a Ranking with a two-color gradient. Compare with exercise 2. Find a station that is often full but loses bikes over the week, and one that gains the most bikes yet is not often full. Explain both.
4. Filters, Edges > Edge Weight, 10 and up. Which flows dominate? Which neighborhoods do they connect?
5. Statistics > Average Degree. Size by In-Degree, then by Out-Degree. In a flow network these are different: which stations are destinations, which are origins, and which are both?
6. Pick one often-full station and use Topology > Ego Network, depth 1. Where do its bikes come from?
7. The plan. List the often-full stations and, for each, the nearest often-empty station. That is the truck's route. Which pair is the shortest hop?

Answers in `SOLUTION.md`.
