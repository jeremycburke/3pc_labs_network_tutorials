# Network visualization tutorials for Gephi

Four small projects for an introductory class on network visualization. Three start from data the way it arrives, walk through cleaning it into the two tables Gephi wants, and end with a graph and a set of questions the graph can answer. The fourth redoes those graphs in Python. Set up the software first; the projects are further down.

## Setup

### 1. Get the files

The tutorials live at https://github.com/jeremycburke/3pc_labs_network_tutorials. There are two ways to get a copy onto your machine.

**Download, no git needed.** Open that page in a browser, click the green **Code** button, and choose **Download ZIP**. Unzip it somewhere you will find again, such as your Documents folder. On Windows, right-click the ZIP and choose **Extract All**; opening the ZIP without extracting it looks like a folder but nothing inside will run. The extracted folder is called `3pc_labs_network_tutorials-main`. A download is a snapshot. If the tutorials change later, download again.

**Clone, if git is installed.** In a terminal, go to the folder where you keep projects and run:

```bash
git clone https://github.com/jeremycburke/3pc_labs_network_tutorials.git
```

That creates a folder called `3pc_labs_network_tutorials`. Cloning keeps a link to the repository, so picking up later changes is one command from inside the folder:

```bash
git pull
```

Either way, the folder you end up with is the top folder for every command below. It is the one that contains `requirements.txt`. Open a terminal there before continuing. For a clone:

```bash
cd 3pc_labs_network_tutorials
```

### 2. Create a virtual environment

A virtual environment is a private copy of Python's packages that lives in this folder. Installing into it cannot break anything else on the laptop, and everyone in the room ends up with the same versions. You need Python 3.10 or newer.

From the top folder, run one command. On Windows, in PowerShell:

```bash
python -m venv .venv
```

On macOS or Linux:

```bash
python3 -m venv .venv
```

This creates a `.venv` folder. You do it once.

### 3. Activate it

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

The prompt now starts with `(.venv)`. This is the step to remember: every new terminal window needs it again before `python` can see the packages. If a script ever fails with `No module named pandas`, this is why.

If PowerShell refuses to run the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, answer Y, and try again.

### 4. Install the packages

With the environment active:

```bash
pip install -r requirements.txt
```

That installs pandas (reads CSVs), networkx (builds graphs), and matplotlib (draws them). It takes a minute.

### 5. Check that it works

```bash
python verify_all.py
```

It reloads every dataset, runs the three Python scripts from project 4, and prints a line per check. The last line should read `all checks passed`. If it does, the laptop is ready for every project in this folder.

Skipping the virtual environment is possible: run the install and check commands with whatever Python is already on the machine. It works, but on a laptop with other Python projects it can change their package versions, and if two students end up with different versions the numbers in the solutions may not match. Use the environment for lab machines and for anyone who already has Python projects of their own.

### 6. Install Gephi

Written for Gephi 0.11.2 and tested on Windows. Download from https://gephi.org. Menu and panel names in the tutorials are from 0.11; 0.10 is nearly identical, 0.9 differs in a few places.

Projects 2 and 3 have latitude and longitude on every node, and Gephi's Geo Layout plugin places nodes on those coordinates. Install it once: Tools > Plugins > Available Plugins, search for `GeoLayout`, tick it, Install, restart Gephi. If you skip this, the solution GEXF files already carry map positions, so you can still open those.

## The projects

| Project | Folder | Graph | The question |
|---|---|---|---|
| 1 | `01_social_network/` | 50 people, 160 friendship arrows, five social circles | Who connects the circles, and which attributes follow them? |
| 2 | `02_airport_flights/` | 20 airports, 144 directed routes, flights per week | How do you get from Boston to Seattle, and what does each connection cost you? |
| 3 | `03_citibike_stations/` | 30 Citi Bike stations, 287 flows, one week of trips | Which docks run full, which run empty, and where should the truck go? |
| 4 | `04_networkx_intro/` | The same three graphs, in Python with networkx | Can you answer the same questions in thirty lines of code? |

Do them in order. Project 1 teaches the import and the appearance panels. Project 2 adds map layouts and filtering by attribute. Project 3 adds node metrics derived from a second table. Project 4 reopens the three clean datasets in networkx, answers the same questions in code, and draws each graph with matplotlib.

The cleaning tutorials in projects 1 to 3 each have a spreadsheet path that needs no code and a Python path that runs a short pandas script. Project 4 is Python only. Every script is standalone and can be run from any folder, for example:

```bash
python 01_social_network/scripts/clean.py
```

## What is in each folder

Projects 1 to 3 have the same shape:

```
raw/         the data as exported, before cleaning
clean/       nodes.csv and edges.csv, ready for Gephi
solution/    a GEXF file that opens in Gephi with attributes and a layout
scripts/     make_raw.py (instructor) and clean.py (answer key)
README.md    scenario, column dictionary, import steps, exercises
CLEANING.md  the cleaning tutorial, spreadsheet path and Python path
SOLUTION.md  Gephi walkthrough and expected findings
```

Project 4 is smaller: three scripts, one per graph, an `output/` folder for the pictures they draw, a README that walks through the code, and a SOLUTION with the expected output.

All data is synthetic. Names are invented. The airports and the Citi Bike station names are real, the coordinates are approximate, and every flight, trip and survey answer was generated by the scripts in each folder.

## Importing a CSV pair into Gephi

The same recipe works for all three Gephi projects. Each project README lists which columns need which type.

1. File > New Project.
2. File > Import spreadsheet. Pick `clean/nodes.csv`. Separator **Comma**, Charset **UTF-8**, Import as **Nodes table**. Next.
3. Gephi shows every column with a guessed type. Fix any that are wrong (numbers that show as String, for instance). Finish.
4. The import report shows `# of Nodes`. Click OK.
5. File > Import spreadsheet again. Pick `clean/edges.csv`. Import as **Edges table**. Next, check types, Finish.
6. The report shows `Graph Type: Directed` and `# of Edges`. Open **More options** if you want to see the merge strategy and the self-loops setting. At the bottom of the report, choose **Append to existing workspace**. Click OK.
7. Data Laboratory tab: confirm the node count and the edge count.

Gephi recognizes a few column names in a spreadsheet. `Id` and `Label` in a nodes table; `Source`, `Target`, `Type`, `Weight`, `Id` and `Label` in an edges table. `Type` is `Directed` or `Undirected` per row. Everything else becomes an attribute column with the type you picked in step 3.

## Things that go wrong

- **`No module named pandas`.** The virtual environment is not active in this terminal. Run the activate command from setup step 3.
- **`python` is not recognized, or the scripts cannot find the data.** The terminal is not in the top folder, or the ZIP was never extracted. Check with `dir` (Windows) or `ls`; you should see `requirements.txt`.
- **Edges imported into an empty workspace.** You get a graph with the right number of edges, nodes named by id, and no attributes. Cause: New workspace instead of Append to existing workspace in step 6. Delete the workspace and import the edges again.
- **Weight column imported as String.** Ranking by weight and the Edge Weight filter will not work. Reimport and set the type to Double.
- **An edge with weight 0 vanished.** Gephi drops zero-weight edges on import. None of the clean files have any, but yours might after a spreadsheet edit.
- **Parallel edges.** If the edge table has the same Source and Target twice, Gephi merges them using the strategy in More options. Sum is right for flows and flight counts. The clean files here have no duplicates, but the raw data does, and the cleaning tutorials remove them on purpose so the choice is yours rather than Gephi's.
- **Accented names come out as `Ã«`.** The file is fine; the program reading it guessed the wrong encoding. In Gephi, set Charset to UTF-8. In Excel, open the file with Data > From Text/CSV rather than double-clicking it.
- **A column named `Type` in the nodes file.** Gephi reserves that name for edges. Rename it before importing nodes.
- **Geo Layout puts every node on one line at the bottom.** The latitude or longitude column was imported as String. Reimport with both set to Double.
- **No picture window from a project 4 script.** Some terminals and remote desktops cannot open one. The picture is still saved in `04_networkx_intro/output/`.

## Generating the data again

Each `scripts/make_raw.py` rebuilds that project's `raw/` folder from a fixed random seed, and `clean.py` rebuilds `clean/` and `solution/` from `raw/`. Running both and then `verify_all.py` reproduces every file in the repo byte for byte.
