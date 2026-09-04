# Cleaning the trip log and the dock readings

Three raw files go in. The station table is tidy and is the reference everything else joins to. The trip file is a log, one row per ride, and becomes the edges by counting. The snapshot file is a second log, one row per station per hour, and becomes two node attributes. This is the first project where node attributes come from a table that is not the one the edges came from, which is the normal case in practice.

## What is wrong with the raw files

`raw/citibike_trips_sample.csv`, 2,950 rows:

| Problem | How much | Fix |
|---|---|---|
| Station names in lowercase, with a trailing space, with two spaces, or with `and` instead of `&` | About 790 of the 5,855 name cells | Trim, collapse spaces, replace ` and ` with ` & `, capitalize each word |
| Exact duplicate rows | 30 | Remove duplicates on `ride_id` |
| Trip never ended at a dock | 45 rows with no end station and no end time | Delete. The bike was lost, stolen or dropped outside the system. |
| End time before start time | 6 rows | Delete |
| Trip longer than a day | 6 rows | Delete. Real ones are worth a call to the customer, not an edge. |
| Round trip, same dock at both ends | 12 rows | Delete for the graph. They are real rides but not a flow between stations. |
| Two styles of station id | 433 id cells use the old numeric ids like `382` | Ignore the id columns. Join on the cleaned name instead. |
| `docked_bike` as a bike type | 57 rows | It is the old name for a classic bike. Treat it as classic. |

`raw/station_status_snapshots.csv`, 5,040 rows (30 stations, 24 hours, 7 days):

| Problem | How much | Fix |
|---|---|---|
| Station names with the same variants as the trip file | About 14 percent of rows | Same fix |
| Blank capacity | 491 rows | Capacity is bikes plus docks |

`raw/station_information.csv` is clean. Its station ids look like decimal numbers (`6000.10`), which is a trap: a spreadsheet will read that as the number 6000.1 and drop the zero. Import every id column as text.

## The rules you apply

- A pair of stations becomes an edge when at least 3 trips went that way during the week. Pairs with 1 or 2 trips are dropped. A rebalancing plan is about regular flows, and 433 pairs on a map of 30 stations is unreadable. Change one number in the script to keep them all.
- Departures, arrivals and net flow count every valid trip, including the ones on pairs that were dropped from the edge table.
- A station is full when `docks_available` is 0 and empty when `bikes_available` is 0.
- A station is often full when it was full in at least 15 percent of the 168 readings, and often empty when it was empty in at least 15 percent. Both at once is "Swings both ways". Neither is "Balanced".

Fifteen percent is about 25 hours in a week, or five hours on each weekday. It is a judgment call. Move it and the categories move.

## Path A: spreadsheet

### Part 1: the station table

1. Open `station_information.csv` with Data > From Text/CSV. In the preview, set `station_id` to Text before loading, or the trailing zero in `6000.10` disappears.

### Part 2: the trip log

2. Open `citibike_trips_sample.csv` the same way, with `start_station_id` and `end_station_id` as Text (you will not use them, but it avoids surprises).
3. Add `start_clean` with `=PROPER(TRIM(SUBSTITUTE(E2, " and ", " & ")))` and `end_clean` with the same on the end station. `SUBSTITUTE` fixes `and`, `TRIM` fixes the spaces, `PROPER` fixes the case. Check a few: `w 41 st & 8 ave` should come out as `W 41 St & 8 Ave`.
4. Data > Remove Duplicates on `ride_id` only. 30 rows go. 2,920 left.
5. Filter `end_station_name` for blanks and delete those rows. 45 go. 2,875 left.
6. Add `duration_min` with `=(D2-C2)*1440`. Excel stores dates in days, so multiplying by 1440 gives minutes. Sort by it, delete rows at or below 0 and rows above 1440. 12 go. 2,863 left.
7. Add `=start_clean=end_clean`, filter for TRUE, delete. 12 go. 2,851 left. Copy the sheet as values now so the helper columns stop recalculating.
8. Add `Source` with `=XLOOKUP(start_clean, Stations!name, Stations!station_id, "CHECK")` and `Target` the same way on `end_clean`. Filter for `CHECK`. None should remain; if any do, the name cleaning in step 3 missed a variant.
9. Add `ebike` with `=IF(B2="electric_bike", 1, 0)`.
10. Pivot table. Rows: `Source`, then `Target`, tabular layout, no subtotals. Values: Count of `ride_id`, Average of `duration_min`, Average of `ebike`. 433 rows.
11. Copy the pivot as values. Delete rows where the count is below 3. 287 remain. Rename the columns `Source`, `Target`, `Weight`, `avg_duration_min`, `ebike_share`; round the last two to one and two decimals. Insert `Type` after `Target`, filled with `Directed`. Save as `edges.csv`, CSV UTF-8.
12. Two more small pivots on the 2,851 rows: Count of `ride_id` by `Source` (this is `departures`) and by `Target` (this is `arrivals`).

### Part 3: the dock readings

13. Open `station_status_snapshots.csv`. Clean `station_name` as in step 3 and look up `Id` as in step 8.
14. Add `capacity_clean` with `=IF(E2="", C2+D2, E2)`.
15. Add `full` with `=IF(D2=0, 1, 0)` and `empty` with `=IF(C2=0, 1, 0)`.
16. Pivot. Rows: `Id`. Values: Count of `snapshot_time` (should be 168 everywhere), Average of `full`, Average of `empty`. Copy as values, round to three decimals, rename to `pct_time_full` and `pct_time_empty`.

### Part 4: assemble the nodes table

17. Start from the station table. Use `XLOOKUP` on `station_id` to pull in `departures` and `arrivals` from step 12 (a station with no match gets 0) and the two shares from step 16.
18. Add `net_flow` as arrivals minus departures, and `status_pattern` with
    `=IF(AND(J2>=0.15, K2>=0.15), "Swings both ways", IF(J2>=0.15, "Often full", IF(K2>=0.15, "Often empty", "Balanced")))`.
19. Arrange the columns as `Id`, `Label` (the name), `neighborhood`, `latitude`, `longitude`, `capacity`, `departures`, `arrivals`, `net_flow`, `pct_time_full`, `pct_time_empty`, `status_pattern`. Save as `nodes.csv`, CSV UTF-8.

### Check your work

| Check | Expected |
|---|---|
| Rows in nodes.csv | 30 |
| Rows in edges.csv | 287 |
| Sum of `Weight` | 2,671 |
| Sum of `departures`, sum of `arrivals` | 2,851 each |
| Sum of `net_flow` | 0 |
| Stations by pattern | Often full 8, Often empty 9, Swings both ways 1, Balanced 12 |
| Readings per station in the snapshot pivot | 168 |
| Smallest and largest `Weight` | 3 and 26 |

Sample rows:

```
Id,Label,neighborhood,latitude,longitude,capacity,departures,arrivals,net_flow,pct_time_full,pct_time_empty,status_pattern
6419.19,W 41 St & 8 Ave,Midtown,40.7562,-73.9901,55,136,179,43,0.214,0.06,Often full
5307.10,E 17 St & Broadway,Village,40.7371,-73.9902,40,91,51,-40,0.048,0.208,Often empty

Source,Target,Type,Weight,avg_duration_min,ebike_share
5160.04,5307.10,Directed,3,11.8,0.67
5160.04,6088.11,Directed,10,5.0,0.7
```

## Path B: Python

```bash
python 03_citibike_stations/scripts/clean.py
```

Needs pandas and networkx; install with `pip install -r requirements.txt` from the top folder, inside a virtual environment if you set one up (the top-level README explains both).

What each block does:

- **`fix_station()`** at the top is the name cleaner: collapse whitespace, swap ` and ` for ` & `, `title()` the result. It is applied to the station table too, so the join key is built the same way on both sides.
- **Step 2** maps every name in both logs to a station id through a dictionary. Two assertions confirm that nothing failed to match.
- **Step 3** is `drop_duplicates` on `ride_id`, a filter on blank end stations, then durations from the two timestamps and a filter on the impossible ones.
- **Step 4** drops the round trips.
- **Step 5** is one `groupby` with a count and two means, then the `MIN_TRIPS` filter.
- **Step 6** is two `groupby().size()` calls on the full trip table for departures and arrivals.
- **Step 7** fills the blank capacities, flags full and empty readings, and takes the mean per station. The `pattern()` function is the same rule as the spreadsheet formula.
- **Step 8 and 9** merge everything onto the station table, run the checks, and write both files.
- The GEXF block projects latitude and longitude onto a flat plane so the file opens as a map.

## Why this shape

Every bike-share, transit and logistics dataset is two logs: what moved, and what state the places were in. The moves make the edges. The states make the node attributes. Neither log knows about the other, and the station table is what ties them together. Real Citi Bike data has exactly this shape: a trip history file with these column names, a live station status feed, and a station information feed with ids and coordinates.
