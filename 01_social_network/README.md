# Project 1: who knows whom

A friendship network of 50 people in five social circles: a hiking club, the staff of a bakery, a set of college roommates, a rec-league soccer team, and a book club. Everyone filled in a short survey naming up to five friends, how often they see each one, and how they met. A few people belong to two circles. One person, Priya Natarajan from the bakery, has friends in four of the five circles. She is the Kevin Bacon of this network: most paths between circles run through her.

The graph is directed. An arrow from A to B means A named B as a friend. B may or may not have named A back, and about a third of the pairs did name each other. The edge weight is roughly how many times a month the two see each other.

All names and answers are invented.

## What you practice here

- Import a node table and an edge table into Gephi and read the import report.
- Color nodes by a category (group, car, music) and size them by a number (age, degree).
- Run community detection and compare what Gephi finds with the real groups.
- Find the shortest path between two people and identify the person everyone routes through.

## Files

| Path | What it is |
|---|---|
| `raw/friendship_survey_export.csv` | The survey export. One row per submission, one column per question, 53 rows. Messy. |
| `raw/participant_roster.csv` | The tidy roster: participant id, first and last name, primary group. 50 rows. |
| `clean/nodes.csv` | One row per person with their attributes. Import this first. |
| `clean/edges.csv` | One row per friendship arrow. Import this second. |
| `solution/social_network.gexf` | The finished graph. Opens directly in Gephi with File > Open. |
| `scripts/clean.py` | Python answer key. Reads `raw/`, writes `clean/` and the GEXF. |
| `scripts/make_raw.py` | Instructor script that generates the raw files. Students do not need it. |
| `CLEANING.md` | The cleaning tutorial: what is wrong with the raw file and how to fix it. |
| `SOLUTION.md` | Gephi walkthrough and the findings students should reach. |

## Column dictionary

`clean/nodes.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Id` | String | P01 to P50 |
| `Label` | String | Full name |
| `gender` | String | Female, Male, Nonbinary |
| `age` | Integer | 20 to 67. One blank: Gordon Hale skipped the question. |
| `group` | String | Hiking club, Bakery coworkers, College roommates, Soccer league, Book club |
| `favorite_team` | String | Cubs, Bears, White Sox, Bulls, Fire, No team |
| `car` | String | Subaru Outback, Toyota Corolla, Honda Civic, Ford F-150, Tesla Model 3, No car |
| `music` | String | Indie rock, Country, Hip-hop, Pop, Jazz, Classical, Electronic |

`clean/edges.csv`

| Column | Type in Gephi | Values |
|---|---|---|
| `Source` | String | Id of the person who named the friend |
| `Target` | String | Id of the friend they named |
| `Type` | String | Always `Directed` |
| `Weight` | Double | Meetups per month: 1, 2, 4, 10 or 20 |
| `context` | String | How they met: club, work, school, neighborhood, family |

## Importing into Gephi

The general recipe is in the top-level README. The specifics for this project:

1. File > New Project.
2. File > Import spreadsheet. Choose `clean/nodes.csv`. Separator **Comma**, Charset **UTF-8**, Import as **Nodes table**. Next.
3. Set `age` to **Integer**. Leave everything else as String. Finish.
4. The report should say `# of Nodes: 50`. Click OK.
5. File > Import spreadsheet again. Choose `clean/edges.csv`. Import as **Edges table**. Next.
6. `Weight` should be **Double**, `context` String. Finish.
7. The report should say `Graph Type: Directed` and `# of Edges: 160`. At the bottom, choose **Append to existing workspace**, not New workspace. Click OK.
8. Open the Data Laboratory tab. The Nodes table has 50 rows and the Edges table has 160.

If you get 160 nodes and no attributes, the edges landed in a fresh workspace. Delete it and repeat step 7.

## Exercises

1. Run the ForceAtlas 2 layout. Color nodes by `group`. Do the five circles separate on their own?
2. Color by `car`, then by `music`, then by `favorite_team`. Which attribute lines up with the circles and which one does not?
3. Size nodes by In-Degree. Who gets named as a friend most often? Is that the same person as the one with the most arrows going out?
4. Run Modularity and color by the Modularity Class it creates. Compare with `group`. Where does Gephi disagree with the roster?
5. Use the shortest path tool from Owen Gallagher (hiking) to Walter Osei (book club). How many steps, and who is in the middle?
6. Run Network Diameter and size nodes by Betweenness Centrality. Who is the connector? Filter that person out and look again.
7. Filter to edges with Weight of 10 or more. Which circle sees each other most?

Answers are in `SOLUTION.md`.
