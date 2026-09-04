# Cleaning the friendship survey

The raw file `raw/friendship_survey_export.csv` is what a form tool hands you: one row per submission, one column per question. Gephi wants two tables instead, one row per person and one row per friendship. Getting from one to the other is the whole exercise.

Two ways to do it. Path A uses a spreadsheet and needs no code. Path B is a Python script you can run and read. Both produce the same two files.

## What is wrong with the raw file

Open the export and look before you fix anything. Here is the full list.

| Problem | Where you see it | Fix |
|---|---|---|
| Three people submitted twice | Marcus Bell, Ingrid Solberg, Yuki Sato each have two rows with different timestamps | Keep the newer row, drop the older one |
| Names typed in lowercase, with trailing spaces, or with two spaces | About a third of the name cells, in the name column and in the friend columns | Trim, collapse spaces, and capitalize |
| Nicknames instead of roster names | `Liz Chen`, `Mike Torres`, `Sam W` | Replace with `Elizabeth Chen`, `Michael Torres`, `Sam Whitfield` |
| A misspelled friend | `Priya Natarajen` | Replace with `Priya Natarajan` |
| Ages written several ways | `34`, `34 years`, `thirty-four`, and one blank (Gordon Hale) | Keep the number. Type 34 for Ethan Walsh. Leave Gordon blank. |
| Gender written several ways | `F`, `female`, `woman`, `NB`, and so on | Recode to Female, Male, Nonbinary |
| Teams, cars and music written several ways | `cubs`, `Chicago Cubs`, `Da Bears`, `corolla`, `hiphop`, `EDM` | Recode with a lookup table |
| Blanks meaning "none" | Empty team and car cells | `No team` and `No car` |
| Frequency is text | `weekly`, `2x a month`, `few times/week`, `daily` | Convert to a number of meetups per month |
| Someone listed themselves as a friend | Hank Dooley, friend slot 3 | Drop the row |
| Someone listed the same friend twice | Tyler Brooks named Kevin Park twice with different frequencies | Keep one row with the higher weight |
| Empty friend slots | Most people named fewer than five friends | Drop empty slots when you stack the columns |
| Two people share a first name | Sam Okafor and Sam Whitfield | Always match on the full name |

Two things that look like problems and are not. Accented names (Zoë, José, Renée) are correct; if they show up as `ZoÃ«`, your spreadsheet opened the file in the wrong encoding, so reopen it as UTF-8. And a person who named B as a friend while B did not name them back is not an error. That is what a directed graph records.

## The lookup tables

You will need these in either path. In a spreadsheet, put each one on its own sheet with two columns: what people typed on the left, the value you keep on the right. Always lowercase and trim the typed value before you look it up.

Frequency to weight (meetups per month):

| Typed | Weight |
|---|---|
| every day, daily, everyday | 20 |
| a few times a week, few times/week, 3x a week, couple times a week | 10 |
| weekly, once a week | 4 |
| every other week, 2x a month, every 2 weeks, twice a month | 2 |
| once a month, monthly, 1x month | 1 |

How they met:

| Typed | Keep |
|---|---|
| work, at work, coworkers | work |
| school, college, class | school |
| club, the club, hiking club, soccer, book club | club |
| neighborhood, neighbors, next door | neighborhood |
| family, cousin, in-laws | family |

Gender: `f`, `female`, `woman` to Female. `m`, `male`, `man` to Male. `nb`, `nonbinary`, `non-binary` to Nonbinary.

Team: `cubs`, `chicago cubs` to Cubs. `bears`, `da bears`, `chicago bears` to Bears. `sox`, `white sox` to White Sox. `bulls`, `chicago bulls` to Bulls. `fire`, `chicago fire` to Fire. `none`, `n/a`, blank to No team.

Car: `subaru`, `outback`, `subaru outback` to Subaru Outback. `corolla`, `toyota corolla` to Toyota Corolla. `civic`, `honda civic` to Honda Civic. `f150`, `f-150`, `ford f150`, `ford f-150` to Ford F-150. `tesla`, `model 3`, `tesla model 3` to Tesla Model 3. `none`, `no car`, `don't drive`, blank to No car.

Music: `indie`, `indie rock` to Indie rock. `country`, `country music` to Country. `hiphop`, `hip hop`, `hip-hop`, `rap` to Hip-hop. `edm`, `electronic`, `electronic/dance` to Electronic. Pop, Jazz and Classical only vary in case.

The complete tables are at the top of `scripts/clean.py`.

## Path A: spreadsheet

Works in Excel and Google Sheets. Formulas below are Excel syntax; Sheets accepts the same ones. If your Excel has no `XLOOKUP`, use `VLOOKUP` with the same arguments in a different order.

### Part 1: the nodes table

1. Open the export with Data > From Text/CSV in Excel, or File > Import in Sheets. Confirm the encoding is UTF-8 and that Zoë Fischer's name shows the ë.
2. Add a column `clean_name` next to `Your name` with `=PROPER(TRIM(B2))` and fill down. `TRIM` removes leading, trailing and doubled spaces. `PROPER` capitalizes each word.
3. Sort the sheet by `Timestamp`, newest first.
4. Data > Remove Duplicates, using only the `clean_name` column. Because the sheet is sorted newest first, the row that survives is the latest submission. Expect 3 rows removed, 50 left.
5. Add `age_clean`. Use Find and Replace on the `Your age` column to delete the text ` years` and ` yrs`, then type `34` in Ethan Walsh's cell. Gordon Hale stays blank.
6. Add `gender_clean` with `=XLOOKUP(LOWER(TRIM(D2)), Lookups!A:A, Lookups!B:B, "CHECK")`, pointing at the gender lookup sheet. Filter for `CHECK` to find anything you did not anticipate. Repeat for team, car and music with their own lookup sheets. Blank team and car cells need a blank row in the lookup, or a wrapper like `=IF(F2="", "No team", XLOOKUP(...))`.
7. On the roster sheet, add `full_name` with `=B2 & " " & C2`.
8. Back on the survey sheet, add `Id` with `=XLOOKUP(clean_name, Roster!full_name, Roster!participant_id, "CHECK")` and `group` with the same lookup returning `primary_group`. No cell should say `CHECK`; if one does, the respondent's name did not match the roster.
9. Copy these columns to a new sheet in this order and with these headers: `Id`, `Label` (the clean name), `gender`, `age`, `group`, `favorite_team`, `car`, `music`. Sort by `Id`. Save as `nodes.csv`, choosing the CSV UTF-8 option.

### Part 2: the edges table

10. The five friend blocks need to become one long list. Make a new sheet with headers `source_name`, `friend`, `frequency`, `context`. Copy `clean_name`, `Friend #1 name`, `How often do you see friend #1?`, `How did you meet friend #1?` from the 50 deduplicated rows and paste as values. Then copy the same four columns for friend #2 and paste directly underneath, and so on through friend #5. You now have 250 rows.
11. Sort by `friend` so the blanks group together, and delete the rows with no friend. 162 rows remain.
12. Add `friend_clean` with `=PROPER(TRIM(B2))`. Then Find and Replace, whole cell only: `Liz Chen` to `Elizabeth Chen`, `Mike Torres` to `Michael Torres`, `Sam W` to `Sam Whitfield`, `Priya Natarajen` to `Priya Natarajan`.
13. Add `Source` with `=XLOOKUP(source_name, Roster!full_name, Roster!participant_id, "CHECK")` and `Target` with the same lookup on `friend_clean`. Filter for `CHECK`. There should be none left after step 12.
14. Add `Weight` with an `XLOOKUP` on `LOWER(TRIM(frequency))` against the frequency table, and `context_clean` the same way against the context table.
15. Find the self-loop: filter for rows where `Source` equals `Target` (a helper column `=C2=D2` makes this quick). Delete it. Hank Dooley is the culprit.
16. Find the repeated pair: sort by `Source`, then `Target`, then `Weight` descending, and use Remove Duplicates on `Source` and `Target` together. The row that survives is the higher weight. One row goes: Tyler Brooks and Kevin Park.
17. Add a column `Type` filled with `Directed`. Copy `Source`, `Target`, `Type`, `Weight`, `context_clean` (renamed `context`) to a new sheet. 160 rows. Save as `edges.csv`, CSV UTF-8.

### Check your work

| Check | Expected |
|---|---|
| Rows in nodes.csv | 50 |
| Rows in edges.csv | 160 |
| Blank ages | 1 (P45, Gordon Hale) |
| Distinct values of `gender` | 3 |
| Distinct values of `Weight` | 5 (1, 2, 4, 10, 20) |
| Rows where Source equals Target | 0 |
| Duplicate Source and Target pairs | 0 |
| Every Source and Target is one of P01 to P50 | yes |

A few rows to compare against:

```
Id,Label,gender,age,group,favorite_team,car,music
P01,Maren Lindqvist,Female,44,Hiking club,No team,Subaru Outback,Indie rock
P11,Priya Natarajan,Female,31,Bakery coworkers,No team,Honda Civic,Hip-hop
P45,Gordon Hale,Male,,Book club,No team,No car,Classical

Source,Target,Type,Weight,context
P01,P03,Directed,1,club
P11,P13,Directed,20,work
P11,P44,Directed,1,club
```

## Path B: Python

```bash
python 01_social_network/scripts/clean.py
```

The script needs pandas and networkx (`pip install -r requirements.txt` from the top folder; the top-level README covers virtual environments). It prints what it removed at each step and ends with the numbers used in `SOLUTION.md`.

What each block does, in the same order as Path A:

- **Lookup tables** at the top. Same tables as above, as Python dictionaries. `tidy()` lowercases and trims before every lookup, and `recode()` stops with a message if it meets a value that is not in the table. That is deliberate: a silent blank is worse than an error.
- **Step 1 to 3** load both files, standardize the respondent's name, sort by timestamp, and keep the first row per name.
- **Step 4** recodes age, gender, team, car and music.
- **Step 5** is the stack. A loop slices the four columns for friend 1, then friend 2, and so on, gives each slice the same headers, and concatenates them. `pandas.melt` can do the same thing in one call, but the loop is easier to read.
- **Step 6 and 7** standardize the friend name, convert frequency and context, and map both names to roster ids. An assertion fails if any name did not match.
- **Step 8** drops self-loops and repeated pairs, keeping the higher weight.
- **Step 9 and 10** assemble the nodes table from the roster plus the survey answers, run the checks in the table above, and write both files.
- The rest writes `solution/social_network.gexf` with networkx and prints centralities, communities and sample paths.

## Why the raw file was shaped this way

Survey tools always export wide: one row per respondent, one column per question. Network tools always want long: one row per relationship. Whatever tool you use, this reshape is the step you will do most often, so it is worth doing by hand once.

The roster is the other half of the lesson. Names are not identifiers. People abbreviate them, misspell them, and share them. Joining every name to an id from a reference list is what makes the edge table trustworthy, and it is why the two Sams did not get merged into one person.
