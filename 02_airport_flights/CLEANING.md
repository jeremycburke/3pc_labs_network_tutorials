# Cleaning the flight log

Project 1 reshaped a wide file into a long one. This project does the other common transformation: a log with one row per event becomes a graph by counting. The flight log has 2,569 rows. The edge table that comes out of it has 144. The delay rate on each airport comes from the same log, and the food category comes from a third file.

## What is wrong with the raw files

`raw/flight_log_week.csv`, one row per departure:

| Problem | How much | Fix |
|---|---|---|
| Airport codes in lowercase or with stray spaces | About 480 of the 5,138 code cells | Trim and uppercase |
| Airport name written instead of the code | 12 cells, such as `Chicago O'Hare International` | Look the name up in the airport table and use its code |
| Exact duplicate rows | 25 | Remove duplicates |
| Origin equals destination | 3 rows | Delete them; a flight cannot go nowhere |
| Two date formats | 2,046 rows as `2026-08-18`, 523 as `8/18/2026` | Parse both, or ignore the column since the graph does not need it |
| Delay blank | 51 rows | The flight was cancelled. Not delayed, not on time; leave it out of the rate. |
| Delay written `n/a` | 16 rows | Same as blank |
| Negative delay | 704 rows | The flight left early. This is not an error. Count it as not delayed. |

`raw/airport_info.csv`, one row per airport:

| Problem | Fix |
|---|---|
| Codes `mia`, `phx` in lowercase and `DTW ` with a trailing space | Trim and uppercase |
| `location` holds city and state together: `Atlanta, GA` | Split on the comma |
| `coordinates` holds latitude and longitude together: `33.6407, -84.4277` | Split on the comma and make sure both are numbers |
| `typical_layover` written six ways: `45m`, `70 min`, `50`, `1h00m`, `1h05m`, `1 hr` | Convert to minutes |

`raw/airport_food.csv`, one row per vendor:

| Problem | Fix |
|---|---|
| Codes in lowercase on 5 rows | Trim and uppercase |
| Rating in mixed case: `healthy`, `HEALTHY`, `Unhealthy` | Capitalize |
| Two vendors with no rating | Drop them. Do not guess. |

## The rules you apply

- A departure is delayed when `delay_min` is 15 or more. Airlines and the US Department of Transportation use the same cutoff.
- Delay rate is delayed departures divided by departures that actually flew. Cancelled flights are excluded from both numbers.
- Delay category: Low under 0.17, High at 0.27 and above, Medium in between.
- Healthy share is Healthy vendors divided by rated vendors.
- Food category: Healthy at 0.60 and above, Mixed from 0.40 to 0.59, Unhealthy under 0.40.

The thresholds are arbitrary. They are chosen so each bucket has several airports. Part of the exercise is noticing that the categories depend on where you draw the line.

## Path A: spreadsheet

### Part 1: the airport table

1. Open `airport_info.csv`. Add `Id` with `=UPPER(TRIM(A2))`.
2. Select the `location` column, Data > Text to Columns, delimiter comma. You get `city` and `state`. Add `=TRIM()` on the state, since it has a leading space.
3. Do the same for `coordinates`. You get `latitude` and `longitude`. Check that both columns are right-aligned, which means Excel read them as numbers. If not, wrap them in `VALUE()`.
4. Add `avg_layover_min`. There are 20 rows, so type the minutes by hand: `45m` is 45, `1h05m` is 65, `1 hr` is 60. This is a legitimate way to clean 20 rows. A formula would take longer to write than the typing and would be easier to get wrong.

### Part 2: the flight log

5. Open `flight_log_week.csv`. Add `origin_clean` with `=UPPER(TRIM(D2))` and `dest_clean` with `=UPPER(TRIM(E2))`.
6. Add a helper `=LEN(origin_clean)>3` and filter for TRUE. These cells hold an airport name. Replace each with the code, either by hand or with `=XLOOKUP(TRIM(D2), Airports!airport_name, Airports!Id, origin_clean)`. Do the same for `dest_clean`. The names are in the airport table exactly as written.
7. Copy the sheet's values to a new sheet so the helper columns become plain text. Data > Remove Duplicates on all columns. 25 rows go, 2,544 stay.
8. Add `=origin_clean=dest_clean`, filter for TRUE, delete the 3 rows. 2,541 stay.
9. Add `delayed` with `=IF(ISNUMBER(H2), IF(H2>=15, 1, 0), "")`. Blank and `n/a` delays give a blank, which averages ignore. A negative delay gives 0.
10. Insert a pivot table. Rows: `origin_clean`, then `dest_clean`. Values: Count of `flight_no`, and Average of `air_time_min`. Set the layout to tabular with no subtotals, so every row shows both codes. This is the edge table: 144 rows.
11. Copy the pivot to a new sheet as values. Rename the columns `Source`, `Target`, `Weight`, `avg_flight_min`. Round `avg_flight_min` to whole minutes. Insert a `Type` column after `Target` filled with `Directed`. Save as `edges.csv`, CSV UTF-8.
12. Insert a second pivot. Rows: `origin_clean`. Values: Count of `flight_no` (departures per week) and Average of `delayed` (the delay rate). Copy as values, round the rate to three decimals, and add `delay_category` with `=IF(C2<0.17, "Low", IF(C2>=0.27, "High", "Medium"))`.

### Part 3: food

13. Open `airport_food.csv`. Add `airport_clean` with `=UPPER(TRIM(A2))` and `rating_clean` with `=PROPER(TRIM(C2))`. Delete the two rows where the rating is blank.
14. Pivot: rows `airport_clean`, columns `rating_clean`, values Count of `vendor`. Copy as values. Add `healthy_share` with `=Healthy/(Healthy+Unhealthy)` rounded to two decimals, and `food_category` with `=IF(D2>=0.6, "Healthy", IF(D2>=0.4, "Mixed", "Unhealthy"))`.

### Part 4: assemble the nodes table

15. Start from the airport table (20 rows). Use `XLOOKUP` on `Id` to pull in `departures_per_week`, `delay_rate` and `delay_category` from the departures pivot, and `healthy_share` and `food_category` from the food pivot.
16. Arrange the columns as `Id`, `Label` (the airport name), `city`, `state`, `latitude`, `longitude`, `departures_per_week`, `delay_rate`, `delay_category`, `healthy_share`, `food_category`, `avg_layover_min`. Save as `nodes.csv`, CSV UTF-8.

### Check your work

| Check | Expected |
|---|---|
| Rows in nodes.csv | 20 |
| Rows in edges.csv | 144 |
| Sum of `Weight` across all edges | 2,541, the number of cleaned log rows |
| Smallest and largest `Weight` | 7 and 35 |
| Airports in each delay category | Low 7, Medium 9, High 4 |
| Airports in each food category | Healthy 6, Mixed 6, Unhealthy 8 |
| An edge from BOS to SEA | none |
| Every `Source` and `Target` is one of the 20 codes | yes |

Sample rows:

```
Id,Label,city,state,latitude,longitude,departures_per_week,delay_rate,delay_category,healthy_share,food_category,avg_layover_min
ORD,Chicago O'Hare International,Chicago,IL,41.9742,-87.9073,302,0.332,High,0.17,Unhealthy,50
MSP,Minneapolis-Saint Paul International,Minneapolis,MN,44.8848,-93.2223,74,0.07,Low,0.8,Healthy,90

Source,Target,Type,Weight,avg_flight_min
ATL,BOS,Directed,19,151
ATL,CLT,Directed,21,57
```

## Path B: Python

```bash
python 02_airport_flights/scripts/clean.py
```

Needs pandas and networkx; install with `pip install -r requirements.txt` from the top folder, inside a virtual environment if you set one up (the top-level README explains both).

What each block does:

- **Step 2** cleans the airport table: uppercase codes, `str.split` on the two packed columns, and a small `layover_minutes()` function with one regular expression per format.
- **Step 3** builds a dictionary from airport name to code and applies it to both airport columns after trimming. An assertion stops the script if any code is still unrecognized.
- **Step 4** is `drop_duplicates()` and a filter on origin equal to dest.
- **Step 5** parses the dates with `format="mixed"` and turns the delay column into numbers with `errors="coerce"`, which makes blank and `n/a` into NaN. Cancelled is then simply "delay is NaN".
- **Step 6** is one `groupby` on origin and dest with a count and a mean. That is the whole edge table.
- **Step 7 and 8** are two more groupbys, one on the log for the delay rate and one `pivot_table` on the food file for vendor counts, each followed by a small bucketing function.
- **Step 9 and 10** merge everything onto the airport table, run the checks in the table above, and write both files.
- The GEXF block adds a position to each node from its coordinates using a plain equirectangular projection, so the file opens as a map without the plugin.

## Why this shape

Almost every real network dataset starts as a log: transactions, messages, trips, citations, flights. The graph is a summary of the log, and the summary throws information away on purpose. Here it throws away dates, times, carriers and individual delays to keep one number per route and a few per airport. The choices about what to keep (flights per week, delay rate at 15 minutes) are analysis decisions, and different choices give a different graph from the same log.
