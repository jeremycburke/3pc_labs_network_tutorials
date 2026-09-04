"""
clean.py  (the Python answer key)

Turns the messy survey export into two Gephi-ready tables, then writes a
solution GEXF and prints the numbers quoted in SOLUTION.md.

  raw/friendship_survey_export.csv + raw/participant_roster.csv
      -> clean/nodes.csv
      -> clean/edges.csv
      -> solution/social_network.gexf

Run from anywhere:   python 01_social_network/scripts/clean.py
Each numbered block below matches a step in CLEANING.md.
"""
import re
from pathlib import Path

import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, SOLUTION = ROOT / "raw", ROOT / "clean", ROOT / "solution"
CLEAN.mkdir(exist_ok=True)
SOLUTION.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Lookup tables. These are the same tables CLEANING.md asks you to build in a
# spreadsheet. Left side: what people typed. Right side: the value we keep.
# ---------------------------------------------------------------------------
NAME_FIXES = {
    "liz chen": "Elizabeth Chen",
    "mike torres": "Michael Torres",
    "sam w": "Sam Whitfield",
    "priya natarajen": "Priya Natarajan",
}
GENDER = {
    "female": "Female", "f": "Female", "woman": "Female",
    "male": "Male", "m": "Male", "man": "Male",
    "non-binary": "Nonbinary", "nonbinary": "Nonbinary", "nb": "Nonbinary",
}
TEAM = {
    "cubs": "Cubs", "chicago cubs": "Cubs",
    "bears": "Bears", "da bears": "Bears", "chicago bears": "Bears",
    "white sox": "White Sox", "sox": "White Sox",
    "bulls": "Bulls", "chicago bulls": "Bulls",
    "fire": "Fire", "chicago fire": "Fire",
    "none": "No team", "n/a": "No team", "": "No team",
}
CAR = {
    "subaru outback": "Subaru Outback", "outback": "Subaru Outback", "subaru": "Subaru Outback",
    "toyota corolla": "Toyota Corolla", "corolla": "Toyota Corolla",
    "honda civic": "Honda Civic", "civic": "Honda Civic",
    "ford f-150": "Ford F-150", "f150": "Ford F-150", "ford f150": "Ford F-150", "f-150": "Ford F-150",
    "tesla model 3": "Tesla Model 3", "tesla": "Tesla Model 3", "model 3": "Tesla Model 3",
    "no car": "No car", "none": "No car", "don't drive": "No car", "": "No car",
}
MUSIC = {
    "indie rock": "Indie rock", "indie": "Indie rock",
    "country": "Country", "country music": "Country",
    "hip-hop": "Hip-hop", "hiphop": "Hip-hop", "hip hop": "Hip-hop", "rap": "Hip-hop",
    "pop": "Pop", "jazz": "Jazz", "classical": "Classical",
    "electronic": "Electronic", "edm": "Electronic", "electronic/dance": "Electronic",
}
# Frequency text -> approximate meetups per month. This becomes the edge Weight.
FREQUENCY = {
    "every day": 20, "daily": 20, "everyday": 20,
    "a few times a week": 10, "few times/week": 10, "3x a week": 10, "couple times a week": 10,
    "weekly": 4, "once a week": 4,
    "every other week": 2, "2x a month": 2, "every 2 weeks": 2, "twice a month": 2,
    "once a month": 1, "monthly": 1, "1x month": 1,
}
CONTEXT = {
    "work": "work", "at work": "work", "coworkers": "work",
    "school": "school", "college": "school", "class": "school",
    "club": "club", "the club": "club", "hiking club": "club", "soccer": "club", "book club": "club",
    "neighborhood": "neighborhood", "neighbors": "neighborhood", "next door": "neighborhood",
    "family": "family", "cousin": "family", "in-laws": "family",
}
WORD_AGES = {"thirty-four": 34}


def tidy(text):
    """Lowercase, trim, and collapse repeated spaces. Used before every lookup."""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def recode(series, table, what):
    keys = series.map(tidy)
    unknown = sorted(set(keys) - set(table))
    assert not unknown, f"{what}: add these to the lookup table: {unknown}"
    return keys.map(table)


def fix_name(text):
    """Trim, collapse spaces, title-case, then apply the manual corrections."""
    key = tidy(text)
    if key in NAME_FIXES:
        return NAME_FIXES[key]
    return " ".join(part.capitalize() for part in key.split(" "))


def parse_age(value):
    key = tidy(value)
    if key in ("", "nan"):
        return None
    if key in WORD_AGES:
        return WORD_AGES[key]
    digits = re.sub(r"[^0-9]", "", key)
    return int(digits) if digits else None


# ---------------------------------------------------------------------------
# Step 1. Load both raw files.
# ---------------------------------------------------------------------------
survey = pd.read_csv(RAW / "friendship_survey_export.csv", dtype=str, keep_default_na=False)
roster = pd.read_csv(RAW / "participant_roster.csv", dtype=str)
roster["full_name"] = roster["first_name"] + " " + roster["last_name"]
print("survey rows loaded:", len(survey))

# ---------------------------------------------------------------------------
# Step 2. Standardize the respondent's name.
# ---------------------------------------------------------------------------
survey["name"] = survey["Your name"].map(fix_name)

# ---------------------------------------------------------------------------
# Step 3. Keep only the latest submission from each person.
#         Sort newest first, then drop later duplicates of the same name.
# ---------------------------------------------------------------------------
survey["when"] = pd.to_datetime(survey["Timestamp"], format="%m/%d/%Y %H:%M:%S")
survey = survey.sort_values("when", ascending=False)
before = len(survey)
survey = survey.drop_duplicates(subset="name", keep="first")
print("duplicate submissions removed:", before - len(survey))

# ---------------------------------------------------------------------------
# Step 4. Recode the profile columns.
# ---------------------------------------------------------------------------
survey["age"] = survey["Your age"].map(parse_age)
survey["gender"] = recode(survey["Gender"], GENDER, "gender")
survey["favorite_team"] = recode(survey["Favorite sports team"], TEAM, "team")
survey["car"] = recode(survey["What car do you drive?"], CAR, "car")
survey["music"] = recode(survey["Favorite music"], MUSIC, "music")

# ---------------------------------------------------------------------------
# Step 5. Reshape wide to long: one row per (respondent, friend).
# ---------------------------------------------------------------------------
blocks = []
for i in range(1, 6):
    block = survey[["name", f"Friend #{i} name",
                    f"How often do you see friend #{i}?",
                    f"How did you meet friend #{i}?"]].copy()
    block.columns = ["source_name", "friend_raw", "freq_raw", "context_raw"]
    blocks.append(block)
long = pd.concat(blocks, ignore_index=True)
long = long[long["friend_raw"].str.strip() != ""]
print("friend mentions after stacking:", len(long))

# ---------------------------------------------------------------------------
# Step 6. Standardize the friend name, the frequency, and the context.
# ---------------------------------------------------------------------------
long["target_name"] = long["friend_raw"].map(fix_name)
long["Weight"] = recode(long["freq_raw"], FREQUENCY, "frequency")
long["context"] = recode(long["context_raw"], CONTEXT, "context")

# ---------------------------------------------------------------------------
# Step 7. Replace names with roster ids.
# ---------------------------------------------------------------------------
name_to_id = dict(zip(roster["full_name"], roster["participant_id"]))
missing = sorted((set(long["source_name"]) | set(long["target_name"])) - set(name_to_id))
assert not missing, f"names not on the roster: {missing}"
long["Source"] = long["source_name"].map(name_to_id)
long["Target"] = long["target_name"].map(name_to_id)

# ---------------------------------------------------------------------------
# Step 8. Drop self-loops, then collapse repeated pairs (keep the higher weight).
# ---------------------------------------------------------------------------
loops = int((long["Source"] == long["Target"]).sum())
long = long[long["Source"] != long["Target"]]
before = len(long)
long = (long.sort_values("Weight", ascending=False)
            .drop_duplicates(subset=["Source", "Target"], keep="first"))
print("self-loops removed:", loops, "| repeated pairs removed:", before - len(long))

edges = long[["Source", "Target", "Weight", "context"]].copy()
edges.insert(2, "Type", "Directed")
edges = edges.sort_values(["Source", "Target"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 9. Build the nodes table from the roster plus the survey answers.
# ---------------------------------------------------------------------------
attrs = survey[["name", "gender", "age", "favorite_team", "car", "music"]]
nodes = roster.merge(attrs, left_on="full_name", right_on="name", how="left")
nodes = nodes.rename(columns={"participant_id": "Id", "full_name": "Label",
                              "primary_group": "group"})
nodes = nodes[["Id", "Label", "gender", "age", "group", "favorite_team", "car", "music"]]
nodes["age"] = nodes["age"].astype("Int64")   # keeps the one blank age blank

# ---------------------------------------------------------------------------
# Step 10. Checks, then write the clean files.
# ---------------------------------------------------------------------------
assert nodes["Id"].is_unique
assert set(edges["Source"]) | set(edges["Target"]) <= set(nodes["Id"])
assert (edges["Source"] != edges["Target"]).all()
assert (edges["Weight"] > 0).all()
assert not edges.duplicated(subset=["Source", "Target"]).any()

nodes.to_csv(CLEAN / "nodes.csv", index=False, encoding="utf-8")
edges.to_csv(CLEAN / "edges.csv", index=False, encoding="utf-8")
print(f"wrote clean/nodes.csv ({len(nodes)} rows) and clean/edges.csv ({len(edges)} rows)")

# ---------------------------------------------------------------------------
# Solution GEXF. Attributes typed, positions from a spring layout so the file
# opens readable instead of as a single clump.
# ---------------------------------------------------------------------------
G = nx.DiGraph()
for row in nodes.itertuples(index=False):
    data = dict(label=row.Label, gender=row.gender, group=row.group,
                favorite_team=row.favorite_team, car=row.car, music=row.music)
    if pd.notna(row.age):
        data["age"] = int(row.age)
    G.add_node(row.Id, **data)
for row in edges.itertuples(index=False):
    G.add_edge(row.Source, row.Target, weight=float(row.Weight), context=row.context)

pos = nx.spring_layout(G.to_undirected(), seed=7, k=0.35, iterations=300)
for n, (x, y) in pos.items():
    G.nodes[n]["viz"] = {"position": {"x": float(x * 600), "y": float(y * 600), "z": 0.0}}
nx.write_gexf(G, SOLUTION / "social_network.gexf")
print("wrote solution/social_network.gexf")

# ---------------------------------------------------------------------------
# Findings quoted in SOLUTION.md
# ---------------------------------------------------------------------------
label = nx.get_node_attributes(G, "label")
grp = nx.get_node_attributes(G, "group")


def show(scores, k=5, fmt="{:.3f}"):
    for n in sorted(scores, key=scores.get, reverse=True)[:k]:
        print(f"   {label[n]:<20} {grp[n]:<18} " + fmt.format(scores[n]))


U = G.to_undirected()
print("\n=== findings ===")
print("nodes", G.number_of_nodes(), "edges", G.number_of_edges())
print("weakly connected:", nx.is_weakly_connected(G))
print("betweenness (directed):")
show(nx.betweenness_centrality(G))
print("betweenness (undirected):")
show(nx.betweenness_centrality(U))
print("in-degree:")
show(dict(G.in_degree()), fmt="{}")
print("weighted in-degree:")
show(dict(G.in_degree(weight="weight")), fmt="{:.0f}")
print("out-degree:")
show(dict(G.out_degree()), fmt="{}")
print("degree (undirected):")
show(dict(U.degree()), fmt="{}")
print("avg path length (undirected):", round(nx.average_shortest_path_length(U), 3))
print("diameter (undirected):", nx.diameter(U))
print("avg clustering (undirected):", round(nx.average_clustering(U), 3))
comms = nx.community.louvain_communities(U, weight="weight", seed=1)
print("louvain communities:", len(comms), "sizes", sorted(len(c) for c in comms))
for c in comms:
    print("   ", pd.Series([grp[n] for n in c]).value_counts().to_dict())
mutual = sum(1 for u, v in G.edges if G.has_edge(v, u)) // 2
print("mutual pairs (both directions):", mutual)
path = nx.shortest_path(U, "P06", "P43")
print("shortest path Owen Gallagher -> Walter Osei:", " -> ".join(label[n] for n in path))
path2 = nx.shortest_path(U, "P01", "P36")
print("shortest path Maren Lindqvist -> Victor Nakamura:", " -> ".join(label[n] for n in path2))
ecc = nx.eccentricity(U)
far = max(ecc, key=ecc.get)
print("most peripheral:", label[far], "eccentricity", ecc[far])
