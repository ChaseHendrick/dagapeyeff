# Excluding Classical Cipher Families for the 1939 D'Agapeyeff Challenge: Key-Free Counts and Searches with Demonstrated Power

**Chase Hendrick**, Independent Researcher · [ORCID 0009-0002-9754-6087](https://orcid.org/0009-0002-9754-6087)

**Preprint**, release 1.0.0 in preparation. Not peer reviewed. Each release of this repository is archived on Zenodo with its own DOI, listed in [RELEASES.md](RELEASES.md).

**[Read the manuscript (PDF)](paper/dagapeyeff-exclusions.pdf)** · [LaTeX source](paper/dagapeyeff-exclusions.tex)

## Abstract

The cryptogram that Alexander d'Agapeyeff printed as a challenge in Codes and Ciphers (1939) has no accepted reading. Its 392 digits form 196 cells of a 5 by 5 Polybius square. Many searches have reported no signal, but few showed that their search could find a planted text of the same length, so a null result closed little. We separate two kinds of evidence.

First, counts that no key can change. Under any one-to-one letter key, with or without any transposition, the fewest single-cell errors needed to turn a text's letter counts into the cells' counts is half the distance between the sorted count vectors (proved). Among 479,051 windows of 196 letters of English prose the closest needs 8 such errors. In four-square the number of symbols each side of a pair can use is fixed by the plaintext and the plain squares, whatever the cipher squares (proved). With standard plain squares English never reaches the cells' 13 and 18, but with chosen plain squares it does, so keyed four-square and two-square stay open.

Second, compiled annealing searches whose power is shown on planted held-out texts, with shuffled cells as the control: columnar transposition with a letter key at width 14 (18 of 18 planted texts recovered), four-square with standard plain squares, a repeating coordinate shift on a keyed square at every period from 2 to 14, homophonic keys, the book's own dummy rule, 363 transforms suggested by our own earlier probes, and enciphering errors at the rate of the book's worked example. In every family the cells score below every recovered planted text, by at least 1.14 nats a letter for English with a one-to-one key (0.75 under a second seed), but by only 0.45 to 0.97 in 5 of 6 Latin rows, 0.48 for Romanian and 0.88 for a capped homophonic key, closures we call weaker. The searches rerun under a second seed agree with their first runs. Against their shuffles the cells sit within the range expected by chance, and where a count comes close it is reported against chance.

A screen of 98 languages by letter counts finds Latin closest by its median window and by its rate of close windows: its median window needs 22 errors against at least 25 for any other language, and among 59.8 million letters of Latin no window comes within 2 errors. Latin was searched under a keyed square, the dummy rule, a repeating shift, four-square, and columnar transposition at widths 2 to 15 with a letter key, and nothing was found.

Finally, taking van Eykelen's no-message recipe as the null hypothesis, a test of thirty order statistics that flags 19 of 20 planted messages under a keyed square finds the cells' order consistent with a no-message dealing; the test is nearly blind to a turning grille, which remains open. All results except the stated propositions are numerical. No reading is claimed. Our reading, an interpretation and not a result, is that the challenge most likely carries no message: no search with shown power found one, and a construction with no message remains consistent with every measurement and passes the order test. If the cells do hold a natural language under a one-to-one key, the counts point to Latin, not English.

## Status of the results

- **No reading of the D'Agapeyeff cipher is claimed.** No letter string produced by a search on the cells is recorded anywhere in this repository.
- **Proved:** Propositions 1 to 3 (Section 3): letter counts under any transposition and one-to-one key, the fewest enciphering errors that reconcile two count vectors, and the key-free side counts of four-square. Proposition 1 is standard.
- **Numerical:** every other result. Each is a seeded run of a stated program, frozen once, and bound to the manuscript by its SHA-256 hash at the head of `paper/numbers.tex`. Seven searches, four-square, the repeating shift at periods 2 to 14 and the five Latin searches the abstract cites, were also rerun under a second seed and agree with their first runs (Table 2).
- **Open:** the 14 by 14 turning grille, four-square with chosen plain squares and two-square, a general table from letter pairs to cell pairs, columnar transposition at the widths and in the languages Section 7 lists, double transposition above width 6, and a construction with no message, which is consistent with every measurement.
- **Our reading (an interpretation, not a result):** the challenge most likely carries no message: no search with shown power found one, and a construction with no message remains consistent with every measurement and passes the order test. If the cells do hold a natural language under a one-to-one key, the counts point to Latin, not English (Section 8).
- **Sources:** the digits are taken from the transcription on the English Wikipedia page for the cipher. The prior work is bounded by the sources the manuscript cites.

## Contents

| Folder | What is in it |
|---|---|
| [`paper/`](paper/) | The manuscript, [`dagapeyeff-exclusions.pdf`](paper/dagapeyeff-exclusions.pdf), its LaTeX source, the bibliography, and `numbers.tex`, the tables `tab_*.tex` and the figures `fig_*.tex`, which `code/make_numbers.py` writes |
| [`code/`](code/) | [`make_numbers.py`](code/make_numbers.py), which writes every number, table and figure the manuscript prints from `data/`, and [`build.sh`](code/build.sh), which builds the PDF |
| [`data/`](data/) | `swarm_cache/`: the frozen result of each probe the manuscript cites, one JSON file each. `texts/`: the three held-out public-domain English texts whose letters the manuscript counts. `cells.json`: the 196 cells |

The search programs that produced `data/swarm_cache/` are in the development repository, [ChaseHendrick/Undeciphered-Texts](https://github.com/ChaseHendrick/Undeciphered-Texts), under `engine/`, each with a test under `tests/` and a dated note under `docs/logs/`. A file in `data/swarm_cache/` is named after its probe: `dagapeyeff-foursquare.json` is written by `engine/dagapeyeff_foursquare.py`, and so on. Each release names the development commit it was published from in [RELEASES.md](RELEASES.md).

## Reproduce

From this folder, with Python 3.10 or later and no other packages:

```
python3 code/make_numbers.py --check   # every number, table, figure and the abstract above match data/
sh code/build.sh                       # rebuild the PDF (needs pdflatex, bibtex and pgfplots)
```

`make_numbers.py --check` exits with status 1 and names the stale file if any number in the manuscript no longer matches its frozen result. It refuses any result file that claims a reading.

To rerun a search, clone the development repository and delete the probe's file in `engine/data/swarm_cache/`; the next call of its report function recomputes it, for example `python3 -c "from engine.dagapeyeff_additive import additive_report; additive_report()"`. Searches take from seconds to about thirty minutes on four cores and need a C compiler. The Italian, language-screen and Latin probes fetch their outside texts (Manzoni's 1827 text at a pinned commit, the Universal Dependencies treebanks, Project Gutenberg books, The Latin Library) into an ignored folder; only counts and scores are stored.

## Cite

```bibtex
@misc{hendrick2026dagapeyeff,
  author = {Hendrick, Chase},
  title  = {Excluding Classical Cipher Families for the 1939 {D'Agapeyeff} Challenge: Key-Free Counts and Searches with Demonstrated Power},
  year   = {2026},
  url    = {https://github.com/ChaseHendrick/dagapeyeff}
}
```

## License

The manuscript in `paper/` is Copyright (c) 2026 Chase Hendrick, all rights reserved. The programs in `code/` and the data in `data/` are under the Apache License 2.0 (see `NOTICE`). The three texts in `data/texts/` are excerpts of public-domain works from Project Gutenberg. The paper's own repository and each of its releases carry a `LICENSE` file with both texts.
