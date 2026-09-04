"""
make_raw.py  (instructor use only)

Builds the raw files for the social network tutorial:

  raw/participant_roster.csv        tidy list of the 50 participants
  raw/friendship_survey_export.csv  messy, wide-format survey export

The output is deterministic. Same seed, same files.
Run from anywhere:   python 01_social_network/scripts/make_raw.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx

SEED = 20260904
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. The people. (first, last, group, gender, age)
#    Attributes that should correlate with the group (team, car, music) are
#    drawn from a per-group profile further down.
# ---------------------------------------------------------------------------
PEOPLE = [
    # Hiking club
    ("Maren", "Lindqvist", "Hiking club", "Female", 44),
    ("Tobias", "Reinholt", "Hiking club", "Male", 51),
    ("Ingrid", "Solberg", "Hiking club", "Female", 38),
    ("Caleb", "Marsh", "Hiking club", "Male", 33),
    ("Zoë", "Fischer", "Hiking club", "Female", 29),
    ("Owen", "Gallagher", "Hiking club", "Male", 57),
    ("Harriet", "Boone", "Hiking club", "Female", 46),
    ("Desmond", "Achebe", "Hiking club", "Male", 41),
    ("Lena", "Vogt", "Hiking club", "Female", 35),
    ("Rafael", "Ortiz", "Hiking club", "Male", 48),
    # Bakery coworkers
    ("Priya", "Natarajan", "Bakery coworkers", "Female", 31),
    ("Marcus", "Bell", "Bakery coworkers", "Male", 24),
    ("Elizabeth", "Chen", "Bakery coworkers", "Female", 27),
    ("Jamal", "Reed", "Bakery coworkers", "Male", 22),
    ("Sofia", "Marchetti", "Bakery coworkers", "Female", 36),
    ("Hank", "Dooley", "Bakery coworkers", "Male", 45),
    ("Tessa", "Nguyen", "Bakery coworkers", "Female", 20),
    ("Rowan", "Blake", "Bakery coworkers", "Nonbinary", 26),
    ("Gloria", "Pemberton", "Bakery coworkers", "Female", 39),
    ("Andre", "Silva", "Bakery coworkers", "Male", 29),
    # College roommates
    ("Michael", "Torres", "College roommates", "Male", 24),
    ("Aisha", "Rahman", "College roommates", "Female", 23),
    ("Kevin", "Park", "College roommates", "Male", 25),
    ("Brianna", "Cole", "College roommates", "Female", 24),
    ("Diego", "Fuentes", "College roommates", "Male", 26),
    ("Noor", "Haddad", "College roommates", "Female", 22),
    ("Tyler", "Brooks", "College roommates", "Male", 25),
    ("Mei", "Tanaka", "College roommates", "Female", 23),
    ("Jordan", "Vance", "College roommates", "Nonbinary", 24),
    ("Chloe", "Adebayo", "College roommates", "Female", 22),
    # Soccer league
    ("Sam", "Okafor", "Soccer league", "Male", 27),
    ("Lucas", "Ferreira", "Soccer league", "Male", 31),
    ("Nadia", "Petrov", "Soccer league", "Female", 29),
    ("Ethan", "Walsh", "Soccer league", "Male", 34),
    ("Camila", "Reyes", "Soccer league", "Female", 25),
    ("Victor", "Nakamura", "Soccer league", "Male", 38),
    ("Bea", "Lindgren", "Soccer league", "Female", 22),
    ("José", "Ramírez", "Soccer league", "Male", 33),
    ("Kwame", "Mensah", "Soccer league", "Male", 30),
    ("Hannah", "Kowalski", "Soccer league", "Female", 26),
    # Book club
    ("Sam", "Whitfield", "Book club", "Male", 58),
    ("Renée", "Dubois", "Book club", "Female", 62),
    ("Walter", "Osei", "Book club", "Male", 67),
    ("Miriam", "Feldman", "Book club", "Female", 55),
    ("Gordon", "Hale", "Book club", "Male", 49),
    ("Yuki", "Sato", "Book club", "Female", 41),
    ("Patricia", "Lowe", "Book club", "Female", 60),
    ("Anthony", "Russo", "Book club", "Male", 52),
    ("Beatrice", "Ng", "Book club", "Female", 45),
    ("Felix", "Baumann", "Book club", "Male", 36),
]

# Per-group tendencies. Values and probabilities.
PROFILE = {
    "Hiking club": dict(
        team=(["Cubs", "Bears", "None"], [0.5, 0.3, 0.2]),
        car=(["Subaru Outback", "Toyota Corolla", "Ford F-150"], [0.6, 0.2, 0.2]),
        music=(["Indie rock", "Country", "Jazz"], [0.5, 0.35, 0.15]),
        freq=(["weekly", "every other week", "once a month"], [0.5, 0.3, 0.2]),
        context=(["club", "neighborhood", "family"], [0.75, 0.15, 0.10]),
    ),
    "Bakery coworkers": dict(
        team=(["White Sox", "Cubs", "None"], [0.5, 0.2, 0.3]),
        car=(["Toyota Corolla", "Honda Civic", "No car"], [0.4, 0.3, 0.3]),
        music=(["Pop", "Hip-hop", "Country"], [0.45, 0.35, 0.2]),
        freq=(["every day", "a few times a week", "weekly"], [0.5, 0.3, 0.2]),
        context=(["work", "neighborhood", "family"], [0.8, 0.1, 0.1]),
    ),
    "College roommates": dict(
        team=(["Bulls", "Bears", "None"], [0.5, 0.2, 0.3]),
        car=(["Honda Civic", "Tesla Model 3", "No car"], [0.4, 0.3, 0.3]),
        music=(["Hip-hop", "Electronic", "Pop"], [0.45, 0.35, 0.2]),
        freq=(["a few times a week", "weekly", "every other week"], [0.45, 0.35, 0.2]),
        context=(["school", "neighborhood", "family"], [0.85, 0.1, 0.05]),
    ),
    "Soccer league": dict(
        team=(["Fire", "Bears", "White Sox"], [0.6, 0.25, 0.15]),
        car=(["Ford F-150", "Honda Civic", "Toyota Corolla"], [0.4, 0.35, 0.25]),
        music=(["Hip-hop", "Country", "Pop"], [0.4, 0.3, 0.3]),
        freq=(["weekly", "every other week", "a few times a week"], [0.6, 0.25, 0.15]),
        context=(["club", "neighborhood", "family"], [0.7, 0.2, 0.1]),
    ),
    "Book club": dict(
        team=(["None", "Cubs", "Bulls"], [0.55, 0.3, 0.15]),
        car=(["Toyota Corolla", "No car", "Subaru Outback"], [0.45, 0.35, 0.2]),
        music=(["Jazz", "Classical", "Indie rock"], [0.45, 0.4, 0.15]),
        freq=(["once a month", "every other week", "weekly"], [0.6, 0.3, 0.1]),
        context=(["club", "neighborhood", "family"], [0.7, 0.2, 0.1]),
    ),
}


def pick(options_and_probs):
    options, probs = options_and_probs
    return str(rng.choice(options, p=probs))


people = pd.DataFrame(PEOPLE, columns=["first", "last", "group", "gender", "age"])
people["name"] = people["first"] + " " + people["last"]
people["team"] = [pick(PROFILE[g]["team"]) for g in people["group"]]
people["car"] = [pick(PROFILE[g]["car"]) for g in people["group"]]
people["music"] = [pick(PROFILE[g]["music"]) for g in people["group"]]
people["participant_id"] = [f"P{i:02d}" for i in range(1, len(people) + 1)]
assert people["name"].is_unique

# ---------------------------------------------------------------------------
# 2. The true friendship edges: (source name, target name, frequency, context)
# ---------------------------------------------------------------------------
# Edges that cross groups. Priya is the deliberate connector; Zoë, Rowan and
# Felix each belong to a second circle; Sam Okafor and Michael Torres are neighbors.
BRIDGES = [
    ("Priya Natarajan", "Nadia Petrov", "weekly", "club"),
    ("Priya Natarajan", "Kwame Mensah", "every other week", "club"),
    ("Priya Natarajan", "Miriam Feldman", "once a month", "club"),
    ("Priya Natarajan", "Aisha Rahman", "every other week", "neighborhood"),
    ("Nadia Petrov", "Priya Natarajan", "weekly", "club"),
    ("Miriam Feldman", "Priya Natarajan", "once a month", "club"),
    ("Aisha Rahman", "Priya Natarajan", "every other week", "neighborhood"),
    ("Zoë Fischer", "Nadia Petrov", "weekly", "club"),
    ("Zoë Fischer", "Kwame Mensah", "every other week", "club"),
    ("Nadia Petrov", "Zoë Fischer", "weekly", "club"),
    ("Rowan Blake", "Jordan Vance", "weekly", "school"),
    ("Rowan Blake", "Kevin Park", "every other week", "school"),
    ("Jordan Vance", "Rowan Blake", "weekly", "school"),
    ("Felix Baumann", "Caleb Marsh", "every other week", "club"),
    ("Felix Baumann", "Lena Vogt", "once a month", "club"),
    ("Caleb Marsh", "Felix Baumann", "every other week", "club"),
    ("Sam Okafor", "Michael Torres", "every other week", "neighborhood"),
    ("Michael Torres", "Sam Okafor", "once a month", "neighborhood"),
]

# In-group edges that the planted data problems depend on.
FORCED = [
    ("Sofia Marchetti", "Priya Natarajan"),   # will be misspelled in the export
    ("Marcus Bell", "Elizabeth Chen"),         # will be written as "Liz Chen"
    ("Aisha Rahman", "Michael Torres"),        # will be written as "Mike Torres"
    ("Renée Dubois", "Sam Whitfield"),         # will be written as "Sam W"
    ("Tyler Brooks", "Kevin Park"),            # will be listed twice
    ("Priya Natarajan", "Elizabeth Chen"),
]

# People who get an extra, planted row in the export (a self-listing, a friend
# listed twice) need a free survey slot, so hold one back for them.
RESERVED_SLOTS = {"Hank Dooley": 1, "Tyler Brooks": 1}

edges = []
seen = set()


def add_edge(src, dst, freq, ctx):
    if src == dst or (src, dst) in seen:
        return
    seen.add((src, dst))
    edges.append((src, dst, freq, ctx))


for src, dst, freq, ctx in BRIDGES:
    add_edge(src, dst, freq, ctx)

group_of = dict(zip(people["name"], people["group"]))
members = people.groupby("group")["name"].apply(list).to_dict()

for src, dst in FORCED:
    prof = PROFILE[group_of[src]]
    add_edge(src, dst, pick(prof["freq"]), pick(prof["context"]))

for name in people["name"]:
    grp = group_of[name]
    prof = PROFILE[grp]
    already = sum(1 for e in edges if e[0] == name)
    room = 5 - already - RESERVED_SLOTS.get(name, 0)   # five friend slots
    want = int(rng.integers(2, 5))          # 2, 3 or 4 in-group friends
    want = max(1, min(want, room)) if room > 0 else 0
    pool = [m for m in members[grp] if m != name and (name, m) not in seen]
    chosen = rng.choice(pool, size=min(want, len(pool)), replace=False)
    for dst in chosen:
        add_edge(name, str(dst), pick(prof["freq"]), pick(prof["context"]))

truth = pd.DataFrame(edges, columns=["source", "target", "freq", "context"])

# Sanity check on the design: one component, Priya on top for betweenness.
G = nx.DiGraph()
G.add_edges_from(truth[["source", "target"]].itertuples(index=False))
assert nx.is_weakly_connected(G), "graph should be one piece"
bc = nx.betweenness_centrality(G)
top = sorted(bc, key=bc.get, reverse=True)[:5]
print("true edges:", len(truth))
print("top betweenness:", top)
assert top[0] == "Priya Natarajan", "Priya should be the connector"

# ---------------------------------------------------------------------------
# 3. Roster file (tidy)
# ---------------------------------------------------------------------------
roster = people[["participant_id", "first", "last", "group"]].rename(
    columns={"first": "first_name", "last": "last_name", "group": "primary_group"}
)
roster.to_csv(RAW / "participant_roster.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4. Survey export (messy, wide)
# ---------------------------------------------------------------------------
GENDER_VARIANTS = {
    "Female": ["Female", "female", "F", "woman", "f"],
    "Male": ["Male", "male", "M", "man", "m"],
    "Nonbinary": ["Non-binary", "nonbinary", "NB"],
}
TEAM_VARIANTS = {
    "Cubs": ["Cubs", "cubs", "Chicago Cubs"],
    "Bears": ["Bears", "bears", "Da Bears", "Chicago Bears"],
    "White Sox": ["White Sox", "Sox", "white sox"],
    "Bulls": ["Bulls", "bulls", "Chicago Bulls"],
    "Fire": ["Fire", "Chicago Fire", "fire"],
    "None": ["none", "None", "n/a", ""],
}
CAR_VARIANTS = {
    "Subaru Outback": ["Subaru Outback", "subaru outback", "Outback", "Subaru"],
    "Toyota Corolla": ["Toyota Corolla", "corolla", "Toyota corolla", "toyota Corolla"],
    "Honda Civic": ["Honda Civic", "civic", "honda civic"],
    "Ford F-150": ["Ford F-150", "F150", "ford f150", "F-150"],
    "Tesla Model 3": ["Tesla Model 3", "Tesla", "model 3"],
    "No car": ["No car", "none", "no car", "don't drive", ""],
}
MUSIC_VARIANTS = {
    "Indie rock": ["Indie rock", "indie", "Indie", "indie rock"],
    "Country": ["Country", "country", "country music"],
    "Hip-hop": ["Hip-hop", "hiphop", "Hip Hop", "hip-hop", "rap"],
    "Pop": ["Pop", "pop"],
    "Jazz": ["Jazz", "jazz"],
    "Classical": ["Classical", "classical"],
    "Electronic": ["Electronic", "EDM", "electronic/dance"],
}
FREQ_VARIANTS = {
    "every day": ["every day", "daily", "everyday", "Every day"],
    "a few times a week": ["a few times a week", "few times/week", "3x a week", "couple times a week"],
    "weekly": ["weekly", "Weekly", "once a week", "weekly "],
    "every other week": ["every other week", "2x a month", "every 2 weeks", "twice a month"],
    "once a month": ["once a month", "monthly", "1x month", "Monthly"],
}
CONTEXT_VARIANTS = {
    "work": ["work", "Work", "at work", "coworkers"],
    "school": ["school", "college", "College", "class"],
    "club": ["club", "the club", "hiking club", "soccer", "book club", "Club"],
    "neighborhood": ["neighborhood", "neighbors", "next door", "Neighborhood"],
    "family": ["family", "cousin", "Family", "in-laws"],
}


def messy(value, table):
    return str(rng.choice(table[value]))


def messy_name(name):
    r = rng.random()
    if r < 0.60:
        return name
    if r < 0.80:
        return name.lower()
    if r < 0.90:
        return name + " "
    return name.replace(" ", "  ")


def messy_age(age):
    r = rng.random()
    if r < 0.85:
        return str(age)
    return f"{age} years"


# Specific, named problems for the tutorial.
NICKNAMES = {
    ("Marcus Bell", "Elizabeth Chen"): "Liz Chen",
    ("Aisha Rahman", "Michael Torres"): "Mike Torres",
    ("Renée Dubois", "Sam Whitfield"): "Sam W",
    ("Sofia Marchetti", "Priya Natarajan"): "Priya Natarajen",
}
WORD_AGE = {"Ethan Walsh": "thirty-four"}
BLANK_AGE = {"Gordon Hale"}
SELF_LOOP = "Hank Dooley"
DOUBLE_LISTED = ("Tyler Brooks", "Kevin Park")
DUPLICATE_SUBMITTERS = ["Marcus Bell", "Ingrid Solberg", "Yuki Sato"]

base = pd.Timestamp("2026-08-24 09:00:00")


def stamp(offset_minutes):
    t = base + pd.Timedelta(minutes=int(offset_minutes))
    return f"{t.month}/{t.day}/{t.year} {t.hour}:{t.minute:02d}:{t.second:02d}"


def friend_slots(name, friends):
    """Return five (friend, freq, context) triples in messy form."""
    slots = []
    for _, row in friends.iterrows():
        label = NICKNAMES.get((name, row.target), row.target)
        if label == row.target:
            label = messy_name(label)
        slots.append((label, messy(row.freq, FREQ_VARIANTS), messy(row.context, CONTEXT_VARIANTS)))
    if name == SELF_LOOP:
        slots.append((name, "weekly", "work"))
    if name == DOUBLE_LISTED[0]:
        slots.append((DOUBLE_LISTED[1], "weekly", "school"))
    slots = slots[:5]
    while len(slots) < 5:
        slots.append(("", "", ""))
    return slots


def survey_row(person, friends, offset_minutes, age_override=None):
    name = person["name"]
    if name in BLANK_AGE:
        age = ""
    elif name in WORD_AGE:
        age = WORD_AGE[name]
    else:
        age = messy_age(person["age"]) if age_override is None else age_override
    row = {
        "Timestamp": stamp(offset_minutes),
        "Your name": messy_name(name),
        "Your age": age,
        "Gender": messy(person["gender"], GENDER_VARIANTS),
        "Favorite sports team": messy(person["team"], TEAM_VARIANTS),
        "What car do you drive?": messy(person["car"], CAR_VARIANTS),
        "Favorite music": messy(person["music"], MUSIC_VARIANTS),
    }
    for i, (f, fr, ctx) in enumerate(friend_slots(name, friends), start=1):
        row[f"Friend #{i} name"] = f
        row[f"How often do you see friend #{i}?"] = fr
        row[f"How did you meet friend #{i}?"] = ctx
    return row


rows = []
offsets = rng.integers(0, 5 * 24 * 60, size=len(people))
for (_, person), off in zip(people.iterrows(), offsets):
    friends = truth[truth["source"] == person["name"]]
    rows.append(survey_row(person, friends, off))
    if person["name"] in DUPLICATE_SUBMITTERS:
        # An earlier, incomplete submission from the same person.
        earlier = friends.head(1)
        rows.append(survey_row(person, earlier, off - 1800, age_override=f"{person['age']} yrs"))

survey = pd.DataFrame(rows)
survey["_t"] = pd.to_datetime(survey["Timestamp"], format="%m/%d/%Y %H:%M:%S")
survey = survey.sort_values("_t").drop(columns="_t").reset_index(drop=True)
survey.to_csv(RAW / "friendship_survey_export.csv", index=False, encoding="utf-8")

print("roster rows:", len(roster))
print("survey rows:", len(survey))
