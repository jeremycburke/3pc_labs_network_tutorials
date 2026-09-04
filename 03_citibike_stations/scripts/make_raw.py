"""
make_raw.py  (instructor use only)

Builds the raw files for the Citi Bike station tutorial:

  raw/station_information.csv      tidy station table (id, name, coordinates, capacity)
  raw/citibike_trips_sample.csv    one row per trip for one week, messy, in the
                                   column layout Citi Bike publishes
  raw/station_status_snapshots.csv one row per station per hour for the week

Station names are real Citi Bike station names. Coordinates are approximate.
Every trip and every snapshot is synthetic.

The output is deterministic. Same seed, same files.
Run from anywhere:   python 03_citibike_stations/scripts/make_raw.py
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
# 1. Stations. (name, neighborhood, lat, lon, capacity)
#    Midtown and Lower Manhattan are office areas. The Village and the Upper
#    East Side are residential. Chelsea is in between.
# ---------------------------------------------------------------------------
STATIONS = [
    ("W 41 St & 8 Ave", "Midtown", 40.7562, -73.9901, 55),
    ("Pershing Square North", "Midtown", 40.7518, -73.9778, 60),
    ("E 47 St & Park Ave", "Midtown", 40.7550, -73.9750, 40),
    ("Broadway & W 41 St", "Midtown", 40.7553, -73.9868, 45),
    ("W 33 St & 7 Ave", "Midtown", 40.7502, -73.9908, 50),
    ("6 Ave & W 33 St", "Midtown", 40.7490, -73.9880, 35),
    ("E 43 St & Vanderbilt Ave", "Midtown", 40.7530, -73.9774, 40),
    ("W 45 St & 6 Ave", "Midtown", 40.7566, -73.9826, 35),
    ("W 21 St & 6 Ave", "Chelsea", 40.7417, -73.9942, 45),
    ("8 Ave & W 31 St", "Chelsea", 40.7505, -73.9947, 50),
    ("W 20 St & 11 Ave", "Chelsea", 40.7465, -74.0077, 30),
    ("W 26 St & 8 Ave", "Chelsea", 40.7472, -73.9973, 35),
    ("W 17 St & 8 Ave", "Chelsea", 40.7418, -74.0015, 40),
    ("9 Ave & W 22 St", "Chelsea", 40.7455, -74.0019, 30),
    ("Broadway & E 14 St", "Village", 40.7345, -73.9906, 50),
    ("Lafayette St & E 8 St", "Village", 40.7302, -73.9911, 45),
    ("E 17 St & Broadway", "Village", 40.7371, -73.9902, 40),
    ("University Pl & E 14 St", "Village", 40.7349, -73.9922, 35),
    ("Carmine St & 6 Ave", "Village", 40.7303, -74.0022, 30),
    ("Christopher St & Greenwich St", "Village", 40.7329, -74.0071, 30),
    ("E 7 St & Avenue A", "Village", 40.7263, -73.9838, 35),
    ("West St & Chambers St", "Lower Manhattan", 40.7175, -74.0132, 45),
    ("South End Ave & Liberty St", "Lower Manhattan", 40.7112, -74.0158, 35),
    ("Vesey Pl & River Terrace", "Lower Manhattan", 40.7153, -74.0163, 40),
    ("Cleveland Pl & Spring St", "Lower Manhattan", 40.7220, -73.9973, 35),
    ("Broadway & Battery Pl", "Lower Manhattan", 40.7045, -74.0136, 40),
    ("1 Ave & E 68 St", "Upper East Side", 40.7651, -73.9582, 40),
    ("E 72 St & York Ave", "Upper East Side", 40.7660, -73.9535, 35),
    ("Lexington Ave & E 63 St", "Upper East Side", 40.7642, -73.9660, 35),
    ("E 75 St & 3 Ave", "Upper East Side", 40.7714, -73.9573, 30),
]
stations = pd.DataFrame(STATIONS, columns=["name", "neighborhood", "lat", "lon", "capacity"])
stations["station_id"] = [f"{int(a)}.{int(b):02d}" for a, b in
                          zip(rng.integers(5000, 7000, len(stations)), rng.integers(1, 20, len(stations)))]
assert stations["station_id"].is_unique
stations["legacy_id"] = [str(v) for v in rng.choice(np.arange(200, 600), len(stations), replace=False)]
stations["role"] = stations["neighborhood"].map({
    "Midtown": "office", "Lower Manhattan": "office",
    "Village": "home", "Upper East Side": "home", "Chelsea": "mixed"})

stations[["station_id", "name", "neighborhood", "lat", "lon", "capacity"]].rename(
    columns={"lat": "latitude", "lon": "longitude"}
).to_csv(RAW / "station_information.csv", index=False, encoding="utf-8")

N = len(stations)
lat = stations["lat"].to_numpy()
lon = stations["lon"].to_numpy()
cap = stations["capacity"].to_numpy()
role = stations["role"].to_numpy()

# Distance matrix in km.
dist = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        dy = (lat[j] - lat[i]) * 111.0
        dx = (lon[j] - lon[i]) * 111.0 * math.cos(math.radians(40.74))
        dist[i, j] = math.hypot(dx, dy)

# ---------------------------------------------------------------------------
# 2. Trips. Commuters ride home -> office in the morning and back in the evening.
# ---------------------------------------------------------------------------
DAYS = pd.date_range("2026-08-17", periods=7, freq="D")   # Monday to Sunday
WEEKDAY_PROFILE = np.array([2, 1, 1, 1, 1, 3, 12, 38, 50, 30, 12, 12, 16, 14, 12, 16, 22, 34, 30, 18, 12, 8, 5, 3], float)
WEEKEND_PROFILE = np.array([4, 3, 2, 1, 1, 1, 3, 6, 10, 16, 22, 26, 28, 28, 28, 26, 24, 22, 18, 14, 10, 8, 6, 4], float)
WEEKDAY_TRIPS, WEEKEND_TRIPS = 480, 260

# (origin weight, destination weight) by station role and time of day.
# The evening ride home is weaker than the morning ride in: plenty of people
# bike downtown and take the subway back. That is what leaves office docks
# full and home docks empty by the end of the week.
ROLE_WEIGHT = {
    "morning": {"home": (3.0, 0.3), "office": (0.3, 3.0), "mixed": (0.8, 0.8)},
    "evening": {"home": (0.4, 1.6), "office": (2.2, 0.4), "mixed": (0.8, 0.8)},
    "other": {"home": (1.0, 1.0), "office": (1.0, 1.0), "mixed": (1.1, 1.1)},
}
DECAY_KM = 2.2

# Every station has a handful of partner stations it exchanges most bikes
# with: a few neighbours, and for home stations a few office stations that
# people commute to. Other pairs still happen, just rarely. This keeps the
# flow graph readable instead of connecting every station to every other.
affinity = np.full((N, N), 0.05)
office_idx = np.flatnonzero(role == "office")
for s in range(N):
    p = np.exp(-dist[s] / 1.2)
    p[s] = 0
    partners = rng.choice(N, size=5, replace=False, p=p / p.sum())
    affinity[s, partners] = 1.0
    affinity[partners, s] = 1.0
    if role[s] == "home":
        p = np.exp(-dist[s, office_idx] / 3.0)
        commute = rng.choice(office_idx, size=3, replace=False, p=p / p.sum())
        affinity[s, commute] = 1.0
        affinity[commute, s] = 1.0
kernel = np.exp(-dist / DECAY_KM) * affinity
np.fill_diagonal(kernel, 0.02)               # a few round trips


def period(hour, weekend):
    if weekend:
        return "other"
    if 6 <= hour <= 9:
        return "morning"
    if 16 <= hour <= 19:
        return "evening"
    return "other"


trips = []
expected = {}       # per hour: expected departures and arrivals at each station
ride_no = 0
for day in DAYS:
    weekend = day.weekday() >= 5
    profile = WEEKEND_PROFILE if weekend else WEEKDAY_PROFILE
    total = WEEKEND_TRIPS if weekend else WEEKDAY_TRIPS
    per_hour = rng.multinomial(total, profile / profile.sum())
    for hour, count in enumerate(per_hour):
        p = period(hour, weekend)
        ow = np.array([ROLE_WEIGHT[p][r][0] for r in role]) * cap
        dw = np.array([ROLE_WEIGHT[p][r][1] for r in role]) * cap
        W = np.outer(ow, dw) * kernel
        P = W / W.sum()
        expected[day + pd.Timedelta(hours=hour)] = (count * P.sum(axis=1), count * P.sum(axis=0))
        picks = rng.choice(N * N, size=int(count), p=P.ravel())
        for pick in picks:
            s, e = int(pick // N), int(pick % N)
            electric = rng.random() < 0.3
            speed = rng.normal(13.5 if electric else 10.5, 1.5)
            minutes = dist[s, e] / max(speed, 4) * 60 + abs(rng.normal(2.5, 1.5))
            start = day + pd.Timedelta(hours=hour, minutes=int(rng.integers(0, 60)),
                                       seconds=int(rng.integers(0, 60)))
            end = start + pd.Timedelta(seconds=int(minutes * 60))
            ride_no += 1
            trips.append(dict(ride_id=f"R{SEED % 1000}{ride_no:05d}",
                              rideable_type="electric_bike" if electric else "classic_bike",
                              started_at=start, ended_at=end, s=s, e=e,
                              member_casual="member" if rng.random() < 0.75 else "casual"))
trips = pd.DataFrame(trips)
print("trips generated:", len(trips))

# ---------------------------------------------------------------------------
# 3. Station status snapshots, one per station per hour. Bikes pile up where
#    trips end and drain where they start. The trip file is a sample of all
#    riding, so the effect on the docks is scaled up. Docks are reset toward
#    half full at 03:00 each night by the rebalancing crew.
# ---------------------------------------------------------------------------
SCALE = 6.0
bikes = np.round(cap * 0.5).astype(float)
snapshots = []
for day in DAYS:
    for hour in range(24):
        slot = day + pd.Timedelta(hours=hour)
        if hour == 3:
            bikes = np.round(cap * rng.uniform(0.4, 0.6, size=N))
        exp_out, exp_in = expected[slot]
        bikes = np.clip(bikes + (exp_in - exp_out) * SCALE + rng.normal(0, 0.7, size=N), 0, cap)
        for i in range(N):
            b = int(round(bikes[i]))
            snapshots.append(dict(station_name=stations.at[i, "name"],
                                  snapshot_time=(slot + pd.Timedelta(minutes=59)).strftime("%Y-%m-%dT%H:%M:%S"),
                                  bikes_available=b, docks_available=int(cap[i]) - b,
                                  capacity=int(cap[i])))
snap = pd.DataFrame(snapshots)
print("snapshots generated:", len(snap))

# ---------------------------------------------------------------------------
# 4. Mess.
# ---------------------------------------------------------------------------
def messy_station(name):
    r = rng.random()
    if r < 0.86:
        return name
    if r < 0.92:
        return name.lower()
    if r < 0.96:
        return name + " "
    if r < 0.98:
        return name.replace(" & ", " and ")
    return name.replace(" ", "  ", 1)


trip_rows = pd.DataFrame({
    "ride_id": trips["ride_id"],
    "rideable_type": trips["rideable_type"],
    "started_at": trips["started_at"].dt.strftime("%Y-%m-%d %H:%M:%S"),
    "ended_at": trips["ended_at"].dt.strftime("%Y-%m-%d %H:%M:%S"),
    "start_station_name": [messy_station(stations.at[i, "name"]) for i in trips["s"]],
    "start_station_id": [stations.at[i, "station_id"] for i in trips["s"]],
    "end_station_name": [messy_station(stations.at[i, "name"]) for i in trips["e"]],
    "end_station_id": [stations.at[i, "station_id"] for i in trips["e"]],
    "start_lat": [f"{lat[i]:.4f}" for i in trips["s"]],
    "start_lng": [f"{lon[i]:.4f}" for i in trips["s"]],
    "end_lat": [f"{lat[i]:.4f}" for i in trips["e"]],
    "end_lng": [f"{lon[i]:.4f}" for i in trips["e"]],
    "member_casual": trips["member_casual"],
})
n = len(trip_rows)

# Some rows still carry the old numeric station ids.
legacy = rng.random(n) < 0.08
trip_rows.loc[legacy, "start_station_id"] = [stations.at[i, "legacy_id"] for i in trips.loc[legacy, "s"]]
legacy = rng.random(n) < 0.08
trip_rows.loc[legacy, "end_station_id"] = [stations.at[i, "legacy_id"] for i in trips.loc[legacy, "e"]]

# A few old rows say docked_bike, which is what classic bikes used to be called.
old = rng.random(n) < 0.03
trip_rows.loc[old & (trip_rows["rideable_type"] == "classic_bike"), "rideable_type"] = "docked_bike"

# Trips that never ended at a dock: no end station, no end time.
lost = rng.choice(trip_rows.index, size=45, replace=False)
trip_rows.loc[lost, ["ended_at", "end_station_name", "end_station_id", "end_lat", "end_lng"]] = ""

# Impossible durations: the clock ran backwards, or the bike was out for days.
backwards = rng.choice(trip_rows.index.difference(lost), size=6, replace=False)
for idx in backwards:
    trip_rows.at[idx, "ended_at"] = (pd.Timestamp(trip_rows.at[idx, "started_at"]) - pd.Timedelta(minutes=int(rng.integers(5, 40)))).strftime("%Y-%m-%d %H:%M:%S")
long_ones = rng.choice(trip_rows.index.difference(lost).difference(backwards), size=6, replace=False)
for idx in long_ones:
    trip_rows.at[idx, "ended_at"] = (pd.Timestamp(trip_rows.at[idx, "started_at"]) + pd.Timedelta(hours=int(rng.integers(26, 70)))).strftime("%Y-%m-%d %H:%M:%S")

# Exact duplicate rows.
dupes = trip_rows.sample(n=30, random_state=int(SEED % 1000))
trip_rows = pd.concat([trip_rows, dupes]).sort_values("started_at", kind="stable").reset_index(drop=True)
trip_rows.to_csv(RAW / "citibike_trips_sample.csv", index=False, encoding="utf-8")
print("trip rows written (with duplicates):", len(trip_rows))

snap["station_name"] = snap["station_name"].map(messy_station)
snap["capacity"] = snap["capacity"].astype(object)
blank = rng.random(len(snap)) < 0.10
snap.loc[blank, "capacity"] = ""
snap.to_csv(RAW / "station_status_snapshots.csv", index=False, encoding="utf-8")
print("snapshot rows written:", len(snap))
