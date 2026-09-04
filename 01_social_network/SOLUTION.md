# Solution: who knows whom

Panel names below are from Gephi 0.11. Older versions are close but not identical.

You can start from `solution/social_network.gexf` (File > Open) or from your own import of the two clean CSVs. The GEXF already carries a layout, so it opens readable.

## Gephi walkthrough

### Layout

1. In the Overview tab, open the Layout panel (bottom left). Choose **ForceAtlas 2**.
2. Set Scaling to 10 and tick **Prevent Overlap**. Click **Run**, wait a few seconds, click **Stop**.
3. The five circles should already be visible as five clumps, with a few people sitting between clumps.

### Color by attribute

4. Appearance panel (top left), **Nodes**, the color icon, **Partition**. Choose `group`. Click **Apply**. Five colors, five clumps.
5. Now choose `car` and Apply. Then `music`. Then `favorite_team`. Then `gender`.

What to notice. Car and music follow the circles. Team follows them less. Gender not at all.

| Circle | Cars | Music | Team |
|---|---|---|---|
| Hiking club | 5 Subaru Outback, 3 Ford F-150 | 7 Indie rock | 4 Bears, 3 Cubs |
| Bakery coworkers | 4 Honda Civic, 3 Corolla, 3 no car | 5 Hip-hop, 4 Pop | 4 no team, 3 White Sox |
| College roommates | 6 Honda Civic, 2 Tesla | 5 Hip-hop, 3 Electronic | 6 Bulls |
| Soccer league | 6 Ford F-150 | 4 Country, 3 Hip-hop | 5 Fire |
| Book club | 5 Corolla, 3 no car | 7 Classical, 3 Jazz | 4 no team, 3 Cubs |

Every circle has roughly half women and half men, so gender colors look like noise. That contrast is the point of the exercise: a category that tracks community structure paints the clumps; one that does not paints confetti.

### Size by number

6. Appearance, Nodes, the size icon, **Ranking**. Choose `age`. Min size 5, max size 30. Apply. The book club grows, the college roommates shrink. Mean ages: college 24, bakery 30, soccer 30, hiking 42, book club 53. Gordon Hale has no age, so he gets the minimum size.
7. Statistics panel (right side), run **Average Degree**. This adds In-Degree, Out-Degree and Degree columns. Size by In-Degree.

In-degree leaders (how many people named you): Priya Natarajan 6, Sofia Marchetti 6, Chloe Adebayo 6, Miriam Feldman 6, then Zoë Fischer 5.

Out-degree is capped by the survey at 5. Priya, Michael Torres, Jordan Vance, Sam Okafor and Nadia Petrov all used every slot.

8. Run **Avg. Weighted Degree** and size by Weighted In-Degree instead. Now the bakery dominates: Sofia Marchetti 74, Gloria Pemberton 70, Elizabeth Chen 48. Coworkers see each other every day, so their edges carry weights of 10 and 20.

### Communities

9. Statistics, **Modularity**. Leave Randomize and Use edge weights ticked, Resolution 1.0. Run.
10. Appearance, Nodes, color, Partition, `Modularity Class`. Apply.

Expected: 5 classes that match the five circles exactly. Gephi's algorithm has a random start, so once in a while it splits or merges a circle; run it again if that happens. The class numbers are arbitrary and will not match the roster order.

Compare with `group` to see which people are assigned to a class that is not their primary circle. Usually none in this network, because the bridge people have more ties inside their own circle than outside it.

### Paths and the connector

11. In the Overview toolbar on the left edge, click the **Shortest Path** tool (the icon with two nodes joined by a route). Click Owen Gallagher, then Walter Osei. The path lights up.

Owen Gallagher to Walter Osei: Owen, Caleb Marsh, Felix Baumann, Gordon Hale, Walter. Four steps. Felix is the hiker who also reads.

Maren Lindqvist to Victor Nakamura: Maren, Ingrid Solberg, Zoë Fischer, Kwame Mensah, Victor. Four steps. Zoë is the hiker who also plays soccer.

12. Statistics, **Network Diameter**. Choose **Undirected** and tick Normalize. Run. This adds Betweenness Centrality, Closeness Centrality and Eccentricity columns.
13. Size nodes by Betweenness Centrality.

Betweenness ranking, undirected: Priya Natarajan, Miriam Feldman, Zoë Fischer, Kwame Mensah, Aisha Rahman. Directed: Priya, Miriam, Nadia Petrov, Aisha, Felix Baumann. Priya is first either way, well ahead of Miriam in second place.

Priya's ties: Elizabeth Chen (bakery, daily), Aisha Rahman (college, neighbor), Nadia Petrov and Kwame Mensah (soccer), Miriam Feldman (book club). Three bakery coworkers named her back, and so did Aisha, Nadia and Miriam.

Network numbers, undirected: average path length 3.4, diameter 7, average clustering 0.44. The most remote person is Maren Lindqvist in the hiking club, seven steps from Brianna Cole, Diego Fuentes and Tyler Brooks in the college group.

14. Filters panel, Library, **Attributes > Partition**, drag `Label` or `Id` into the query area, untick Priya. Click Filter. Or, in the Data Laboratory, right-click her row and delete it (Undo is not available, so do this on a copy of the workspace).

Without Priya the bakery keeps exactly two links to the rest of the network, both from Rowan Blake to the college roommates (Kevin Park and Jordan Vance). The graph stays in one piece, but rerun Network Diameter and the average path length rises from 3.4 to 4.7.

### Edge weights and context

15. Filters, Library, **Edges > Edge Weight**. Drag it in, set the range to 10 or more. Filter.

38 edges survive: 19 from the bakery, 15 from the college roommates, 4 from the soccer league, none from the hiking club or the book club. Mean weight by circle: bakery 9.9, college 6.1, soccer 4.2, hiking 2.9, book club 1.6.

16. Appearance, **Edges**, color, Partition, `context`. Apply. Then Preview tab to see it drawn.

Mean weight by context: work 11.9, school 6.4, family 5.2, neighborhood 3.2, club 2.8. People who share a workplace or a dorm see each other far more than people who share a hobby.

## Findings in one place

| Measure | Value |
|---|---|
| Nodes, edges | 50, 160 |
| Components | 1 |
| Mutual pairs (both named each other) | 30 |
| Edges within a circle, between circles | 142, 18 |
| Modularity communities | 5, matching the roster |
| Highest betweenness | Priya Natarajan |
| Highest in-degree | four-way tie at 6 |
| Highest weighted in-degree | Sofia Marchetti, 74 |
| Average path length (undirected) | 3.4 |
| Diameter (undirected) | 7 |
| Most remote person | Maren Lindqvist |

## Notes for the instructor

Gephi computes betweenness on the directed graph unless you choose Undirected in the dialog, and it reports unnormalized values unless you tick Normalize. Rankings are the same in every case; the numbers are not. `scripts/clean.py` prints both versions.

The five-way split from Modularity is the expected result at resolution 1.0, with a modularity score near 0.68. Raising the resolution to 2.0 splits the bakery into a group of four and a group of six while the other circles hold; lowering it to 0.5 still gives the same five. A quick demonstration of both makes the parameter concrete.
