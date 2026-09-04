"""
make_raw.py  (instructor use only)

Builds the raw files for the airport flight network tutorial:

  raw/flight_log_week.csv   one row per departure for one week, messy
  raw/airport_info.csv      one row per airport, with packed columns
  raw/airport_food.csv      one row per (airport, food vendor)

The output is deterministic. Same seed, same files.
Run from anywhere:   python 02_airport_flights/scripts/make_raw.py
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260904
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Airports.
#    code, name, city, state, lat, lon, target delay rate, layover minutes, food target
#    Coordinates are approximate. Delay rates and food ratings are invented.
# ---------------------------------------------------------------------------
AIRPORTS = [
    ("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta", "GA", 33.6407, -84.4277, 0.21, 45, "Mixed"),
    ("BOS", "Boston Logan International", "Boston", "MA", 42.3656, -71.0096, 0.22, 70, "Healthy"),
    ("CLT", "Charlotte Douglas International", "Charlotte", "NC", 35.2144, -80.9473, 0.13, 50, "Unhealthy"),
    ("DEN", "Denver International", "Denver", "CO", 39.8561, -104.6737, 0.12, 55, "Healthy"),
    ("DFW", "Dallas/Fort Worth International", "Dallas", "TX", 32.8998, -97.0403, 0.22, 60, "Unhealthy"),
    ("DTW", "Detroit Metropolitan Wayne County", "Detroit", "MI", 42.2162, -83.3554, 0.13, 50, "Mixed"),
    ("EWR", "Newark Liberty International", "Newark", "NJ", 40.6895, -74.1745, 0.35, 80, "Unhealthy"),
    ("IAD", "Washington Dulles International", "Dulles", "VA", 38.9531, -77.4565, 0.21, 70, "Mixed"),
    ("IAH", "George Bush Intercontinental", "Houston", "TX", 29.9902, -95.3368, 0.20, 55, "Unhealthy"),
    ("JFK", "John F. Kennedy International", "New York", "NY", 40.6413, -73.7781, 0.31, 85, "Mixed"),
    ("LAS", "Harry Reid International", "Las Vegas", "NV", 36.0840, -115.1537, 0.20, 60, "Unhealthy"),
    ("LAX", "Los Angeles International", "Los Angeles", "CA", 33.9416, -118.4085, 0.23, 75, "Mixed"),
    ("MIA", "Miami International", "Miami", "FL", 25.7959, -80.2870, 0.23, 75, "Unhealthy"),
    ("MSP", "Minneapolis-Saint Paul International", "Minneapolis", "MN", 44.8848, -93.2223, 0.10, 90, "Healthy"),
    ("ORD", "Chicago O'Hare International", "Chicago", "IL", 41.9742, -87.9073, 0.33, 50, "Unhealthy"),
    ("PHL", "Philadelphia International", "Philadelphia", "PA", 39.8729, -75.2437, 0.24, 65, "Mixed"),
    ("PHX", "Phoenix Sky Harbor International", "Phoenix", "AZ", 33.4373, -112.0078, 0.12, 60, "Unhealthy"),
    ("SEA", "Seattle-Tacoma International", "Seattle", "WA", 47.4502, -122.3088, 0.13, 60, "Healthy"),
    ("SFO", "San Francisco International", "San Francisco", "CA", 37.6213, -122.3790, 0.32, 70, "Healthy"),
    ("SLC", "Salt Lake City International", "Salt Lake City", "UT", 40.7899, -111.9791, 0.09, 65, "Healthy"),
]
airports = pd.DataFrame(AIRPORTS, columns=[
    "code", "name", "city", "state", "lat", "lon", "delay_target", "layover", "food_target"])
info = airports.set_index("code")

# ---------------------------------------------------------------------------
# 2. Routes and a base number of weekly flights per direction.
#    There is deliberately no BOS-SEA nonstop; that is the planning exercise.
# ---------------------------------------------------------------------------
ROUTES = {
    "BOS": {"JFK": 28, "IAD": 17, "ATL": 21, "ORD": 24, "DTW": 10, "MSP": 7, "DEN": 10, "DFW": 14, "SFO": 10},
    "JFK": {"LAX": 35, "SFO": 24, "MIA": 28, "ATL": 21, "ORD": 21, "SEA": 10},
    "EWR": {"ORD": 21, "SFO": 17, "DEN": 10, "IAH": 14},
    "PHL": {"ORD": 17, "ATL": 17, "CLT": 14},
    "IAD": {"DEN": 10, "ATL": 17},
    "ATL": {"ORD": 24, "DFW": 28, "MIA": 28, "CLT": 21, "DEN": 21, "LAX": 24, "SEA": 14, "IAH": 17, "PHX": 14},
    "CLT": {"ORD": 14, "DFW": 14},
    "MIA": {"DFW": 14, "LAX": 14},
    "ORD": {"DEN": 28, "SEA": 17, "SFO": 21, "LAX": 24, "MSP": 21, "DTW": 17, "DFW": 24, "LAS": 17, "SLC": 10},
    "DTW": {"MSP": 10, "LAX": 10},
    "MSP": {"DEN": 14, "SEA": 10, "SLC": 7},
    "DFW": {"DEN": 21, "LAX": 24, "SEA": 14, "PHX": 17, "LAS": 17, "SLC": 10},
    "IAH": {"DEN": 14, "LAX": 14},
    "DEN": {"SLC": 17, "PHX": 17, "LAS": 17, "LAX": 24, "SFO": 21, "SEA": 17},
    "SLC": {"SEA": 10},
    "PHX": {"LAX": 21, "SEA": 10},
    "LAS": {"LAX": 21},
    "LAX": {"SFO": 31, "SEA": 21},
    "SFO": {"SEA": 21},
}
pairs = [(a, b, n) for a, targets in ROUTES.items() for b, n in targets.items()]
assert all(a != b for a, b, _ in pairs)
assert ("BOS", "SEA") not in {(a, b) for a, b, _ in pairs}
assert ("SEA", "BOS") not in {(a, b) for a, b, _ in pairs}
print("route pairs:", len(pairs))


def miles(a, b):
    """Great-circle distance between two airport codes."""
    la1, lo1 = math.radians(info.at[a, "lat"]), math.radians(info.at[a, "lon"])
    la2, lo2 = math.radians(info.at[b, "lat"]), math.radians(info.at[b, "lon"])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3959 * 2 * math.asin(math.sqrt(h))


# ---------------------------------------------------------------------------
# 3. The flight log. One row per departure, one week, both directions.
# ---------------------------------------------------------------------------
CARRIERS = ["AU", "BW", "SK", "PR"]      # Aurora Air, Bluewater, Skyline, Prairie Air
DAYS = pd.date_range("2026-08-17", periods=7, freq="D")
rows = []
flight_counter = {c: 100 for c in CARRIERS}


def one_flight(origin, dest, day):
    carrier = str(rng.choice(CARRIERS))
    flight_counter[carrier] += 1
    dep_hour = int(rng.integers(5, 22))
    dep_min = int(rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]))
    air = 30 + miles(origin, dest) / 8.0 + rng.normal(0, 6)
    return {
        "flight_no": f"{carrier}{flight_counter[carrier]}",
        "carrier": carrier,
        "date": day,
        "origin": origin,
        "dest": dest,
        "sched_dep": f"{dep_hour:02d}:{dep_min:02d}",
        "air_time_min": int(round(air)),
        "delay_min": 0,
    }


for a, b, base in pairs:
    for origin, dest in ((a, b), (b, a)):
        n = max(7, base + int(rng.integers(-2, 3)))
        for k in range(n):
            rows.append(one_flight(origin, dest, DAYS[k % 7]))

log = pd.DataFrame(rows)
print("flights generated:", len(log))

# Delays. Each airport gets its target share of delayed departures, chosen at
# random, so the realised delay rate lands close to the target.
log["delay_min"] = [int(v) for v in rng.integers(-8, 15, size=len(log))]
for origin, group in log.groupby("origin"):
    k = int(round(len(group) * info.at[origin, "delay_target"]))
    delayed_idx = rng.choice(group.index, size=k, replace=False)
    log.loc[delayed_idx, "delay_min"] = [int(15 + v) for v in rng.exponential(30, size=k)]

# ---------------------------------------------------------------------------
# 4. Mess.
# ---------------------------------------------------------------------------
log["delay_min"] = log["delay_min"].astype(object)
log["date"] = log["date"].astype(object)

# Cancelled flights have no delay; a few were logged as n/a.
cancelled = rng.random(len(log)) < 0.02
log.loc[cancelled, "delay_min"] = ""
na = (rng.random(len(log)) < 0.01) & ~cancelled
log.loc[na, "delay_min"] = "n/a"

# Two date formats.
us_style = rng.random(len(log)) < 0.2
log["date"] = [
    (f"{d.month}/{d.day}/{d.year}" if us else d.strftime("%Y-%m-%d"))
    for d, us in zip(log["date"], us_style)
]

# Codes with the wrong case or stray spaces.
def mess_code(code):
    r = rng.random()
    if r < 0.90:
        return code
    if r < 0.94:
        return code.lower()
    if r < 0.97:
        return code + " "
    return " " + code.title()


log["origin"] = log["origin"].map(mess_code)
log["dest"] = log["dest"].map(mess_code)

# A handful of rows use the airport name instead of the code.
name_of = dict(zip(airports["code"], airports["name"]))
for idx in rng.choice(log.index, size=12, replace=False):
    col = "origin" if rng.random() < 0.5 else "dest"
    log.at[idx, col] = name_of[log.at[idx, col].strip().upper()]

# Rows where origin equals destination (a logging error).
for idx in rng.choice(log.index, size=3, replace=False):
    log.at[idx, "dest"] = log.at[idx, "origin"]

# Exact duplicate rows.
dupes = log.sample(n=25, random_state=int(SEED % 1000))
log = pd.concat([log, dupes]).sample(frac=1, random_state=int(SEED % 1000)).reset_index(drop=True)

log.to_csv(RAW / "flight_log_week.csv", index=False, encoding="utf-8")
print("flight log rows written (with duplicates):", len(log))

# ---------------------------------------------------------------------------
# 5. Airport info, with location and coordinates packed into single columns
#    and layover written several ways.
# ---------------------------------------------------------------------------
def layover_text(minutes, i):
    style = i % 5
    if style == 0:
        return f"{minutes // 60}h{minutes % 60:02d}m" if minutes >= 60 else f"{minutes}m"
    if style == 1:
        return f"{minutes} min"
    if style == 2 and minutes % 60 == 0:
        return f"{minutes // 60} hr"
    return str(minutes)


info_rows = []
for i, r in airports.iterrows():
    code = r["code"]
    if code in ("PHX", "MIA"):
        code = code.lower()
    if code == "DTW":
        code = "DTW "
    info_rows.append({
        "code": code,
        "airport_name": r["name"],
        "location": f"{r['city']}, {r['state']}",
        "coordinates": f"{r['lat']:.4f}, {r['lon']:.4f}",
        "typical_layover": layover_text(int(r["layover"]), i),
    })
pd.DataFrame(info_rows).to_csv(RAW / "airport_info.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 6. Food vendors. Counts chosen so each airport lands in its target bucket:
#    healthy share >= 0.6 Healthy, 0.4 to 0.6 Mixed, < 0.4 Unhealthy.
# ---------------------------------------------------------------------------
HEALTHY = ["Green Bowl Salads", "Fresh Fruit Cart", "Juice Press Bar", "Poke Point",
           "Harvest Grain Kitchen", "Sushi Sky", "Mediterranean Wrap Co", "Soup and Greens",
           "Yogurt Stand", "Veggie Burrito Bar"]
UNHEALTHY = ["Burger Barn", "Pretzel Stop", "Pizza Corner", "Wing Hut", "Donut Depot",
             "Fried Chicken Shack", "Nacho Cantina", "Hot Dog Stand", "Cinnamon Roll Co",
             "Milkshake Bar", "Candy Kiosk"]
COUNTS = {   # (healthy vendors, unhealthy vendors) options per target
    "Healthy": [(4, 1), (5, 1), (4, 2)],       # shares 0.80, 0.83, 0.67
    "Mixed": [(3, 3), (2, 2), (2, 3)],         # shares 0.50, 0.50, 0.40
    "Unhealthy": [(1, 4), (1, 5), (2, 4)],     # shares 0.20, 0.17, 0.33
}
RATING_TEXT = {"Healthy": ["Healthy", "healthy", "Healthy", "HEALTHY"],
               "Unhealthy": ["Unhealthy", "unhealthy", "Unhealthy", "UNHEALTHY"]}
food_rows = []
for _, r in airports.iterrows():
    h, u = COUNTS[r["food_target"]][int(rng.integers(0, 3))]
    picks = [(v, "Healthy") for v in rng.choice(HEALTHY, size=h, replace=False)]
    picks += [(v, "Unhealthy") for v in rng.choice(UNHEALTHY, size=u, replace=False)]
    code = r["code"] if rng.random() < 0.85 else r["code"].lower()
    for vendor, rating in picks:
        food_rows.append({"airport": code, "vendor": vendor,
                          "rating": str(rng.choice(RATING_TEXT[rating]))})
# Two extra vendors that were never rated. They should be dropped, not guessed.
food_rows.append({"airport": "DEN", "vendor": "Noodle Counter", "rating": ""})
food_rows.append({"airport": "MIA", "vendor": "Cuban Coffee Window", "rating": ""})
food = pd.DataFrame(food_rows).sample(frac=1, random_state=int(SEED % 1000)).reset_index(drop=True)
food.to_csv(RAW / "airport_food.csv", index=False, encoding="utf-8")
print("food rows:", len(food))
