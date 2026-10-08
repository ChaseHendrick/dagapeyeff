"""Write every number and table the manuscript prints from the frozen search results.

    python3 code/make_numbers.py          # rewrite paper/numbers.tex, paper/tab_*.tex, paper/fig_*.tex and the README abstract
    python3 code/make_numbers.py --check  # fail if any of them is stale

The inputs are the frozen outputs of the probes: JSON files, three held-out texts whose letters are
counted, and the cells. In the companion repository they sit in data/. In the development repository,
ChaseHendrick/Undeciphered-Texts, they are read from engine/data/ and the cells from the engine, and
companion_data() gives the files the companion carries. Nothing here searches; it only reads and formats.
No letter string from any search is read or written.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PAPER = HERE / "paper"
README = HERE / "README.md"
COMPANION = (HERE / "data" / "swarm_cache").is_dir()
if COMPANION:
    CACHE = HERE / "data" / "swarm_cache"
    DATA = HERE / "data" / "texts"
else:
    ROOT = HERE.parents[1]
    CACHE = ROOT / "engine" / "data" / "swarm_cache"
    DATA = ROOT / "engine" / "data"

INPUTS = (
    "corpus", "columnar", "columnar14c", "exhaustive", "exhaustive10", "double", "keywords",
    "foursquare", "pairmap", "grillec", "quick", "homophone", "additive", "direction",
    "errors", "italian", "screen", "latin", "fskeyed", "latin14", "tongues", "romanian-wide",
    "keyedsquares", "nomessage", "latinmore", "latinshift",
    "alllanguages", "russian", "esperanto", "latinlib", "latinlibrary", "latinw", "shiftgap",
    "reseed", "latinsmall", "rarecolumn", "latinwords", "latingrille", "latindouble",
)
HELD = ("neural_train_austen", "neural_heldout_doyle", "neural_audit_wells")


def _cells_list() -> list[int]:
    if COMPANION:
        return json.loads((HERE / "data" / "cells.json").read_text(encoding="utf-8"))["cells"]
    sys.path.insert(0, str(ROOT))
    from engine.dagapeyeff_add import _cells

    return _cells()


def companion_data() -> dict[str, bytes]:
    """The inputs, by their path in the companion repository. Development repository only."""
    if COMPANION:
        raise SystemExit("companion_data() reads the development repository")
    out = {f"data/swarm_cache/dagapeyeff-{name}.json": (CACHE / f"dagapeyeff-{name}.json").read_bytes() for name in INPUTS}
    out.update({f"data/texts/{name}.txt": (DATA / f"{name}.txt").read_bytes() for name in HELD})
    out["data/texts/neural_audit_wells_source.json"] = (DATA / "neural_audit_wells_source.json").read_bytes()
    cells = {"source": "English Wikipedia, D'Agapeyeff cipher, fetched 2 October 2026; final 000 dropped",
             "coding": "x = 5r + c, rows 6,7,8,9,0 and columns 1,2,3,4,5", "cells": _cells_list()}
    out["data/cells.json"] = (json.dumps(cells) + "\n").encode("utf-8")
    return out


def load(name: str) -> dict:
    data = json.loads((CACHE / f"dagapeyeff-{name}.json").read_text(encoding="utf-8"))
    if data.get("solved") is not False or data.get("claimed_plaintext") is not None:
        raise SystemExit(f"{name}: a frozen result claims a reading; refusing to print it")
    return data


def n(value: int) -> str:
    """An integer with thin thousands separators."""
    text = f"{value:,}"
    return text.replace(",", "{,}")


def d(value: float, places: int = 4) -> str:
    """A signed decimal in math mode."""
    return f"\\ensuremath{{{value:.{places}f}}}"


def p(value: float, places: int = 2) -> str:
    return f"\\ensuremath{{{value:.{places}f}}}"


def macros() -> dict[str, str]:
    out: dict[str, str] = {}
    corpus = load("corpus")
    out["corpusLetters"] = n(corpus["corpus_letters"])
    out["corpusWindows"] = n(corpus["windows"])
    out["corpusAllThree"] = n(corpus["windows_all_three"])
    out["cellsDistinct"] = str(corpus["cell_distinct"])
    out["cellsLargest"] = str(corpus["cell_largest"])
    out["cellsChi"] = p(corpus["cell_chi_square"])

    held = {name: len("".join(ch for ch in (DATA / f"{name}.txt").read_text(encoding="utf-8").upper() if "A" <= ch <= "Z"))
            for name in HELD}
    out["heldAusten"] = n(held["neural_train_austen"])
    out["heldDoyle"] = n(held["neural_heldout_doyle"])
    out["heldWells"] = n(held["neural_audit_wells"])

    columnar = load("columnar")
    small = [row for row in columnar["rows"] if row["width"] in (1, 2, 4, 7)]
    out["subCellsLow"] = d(min(row["cells_per_letter"] for row in small))
    out["subCellsHigh"] = d(max(row["cells_per_letter"] for row in small))
    out["subPlantedLow"] = d(min(pl["true_per_letter"] for row in small for pl in row["planted"]))
    out["subRecovered"] = str(sum(row["planted_recovered"] for row in small))
    out["subPlanted"] = str(sum(len(row["planted"]) for row in small))

    c14 = load("columnar14c")
    out["widthFourteenRecovered"] = str(sum(v[0] for v in c14["planted_recovered"].values()))
    out["widthFourteenPlanted"] = str(sum(v[1] for v in c14["planted_recovered"].values()))
    out["widthFourteenWithErrors"] = str(sum(1 for pl in c14["planted"] if pl["errors"] > 0))
    out["widthFourteenErrors"] = str(max(pl["errors"] for pl in c14["planted"]))
    out["widthFourteenSteps"] = n(c14["search"]["steps"])
    out["widthFourteenRestarts"] = str(c14["search"]["restarts"])
    scores = [row["per_letter"] for row in c14["searched"].values()]
    out["widthFourteenCellsLow"] = d(min(scores))
    out["widthFourteenCellsHigh"] = d(max(scores))
    out["widthFourteenPlantedLow"] = d(c14["planted_lowest_true"])
    highs = [row["shuffles_as_high"] for row in c14["searched"].values()]
    out["widthFourteenShufflesLow"] = str(min(highs))
    out["widthFourteenShufflesHigh"] = str(max(highs))
    out["widthFourteenShuffles"] = str(len(next(iter(c14["searched"].values()))["shuffles"]))

    ex = load("exhaustive")
    out["exhaustiveCases"] = str(len(ex["rows"]))
    out["exhaustivePlantedSmallest"] = p(ex["planted_smallest_excess"], 4)
    out["exhaustiveCellsLargest"] = p(ex["cells_largest_excess"], 4)
    out["exhaustiveRegroupedLargest"] = p(ex["regrouped_largest_excess"], 4)
    ex10 = {row["family"]: row for row in load("exhaustive10")["rows"]}
    done = ex10["columnar-done"]
    out["tenDonePlantedLow"] = p(min(pl["excess"] for pl in done["planted"]), 4)
    out["tenDoneCells"] = p(done["cells"]["excess"], 4)
    out["tenDoneRegrouped"] = p(done["regrouped"]["excess"], 4)

    double = load("double")
    out["doubleCases"] = str(double["cases"])
    out["doubleBelow"] = str(double["cases_cells_below_planted"])

    kw = load("keywords")
    out["keywordCount"] = n(kw["keywords"])
    out["keywordOrders"] = n(kw["orders_scored"])
    out["keywordCells"] = p(kw["cells_best_mi"], 4)
    out["keywordNullHigh"] = p(max(kw["null_best_mi"]), 4)
    out["keywordPlants"] = str(len(kw["plants"]))
    out["keywordPlantsFirst"] = str(kw["plants_ranked_first"])
    out["keywordPlantsLow"] = p(min(pl["top_mi"] for pl in kw["plants"]), 4)

    fs = load("foursquare")
    counts = fs["counts"]
    low, high = sorted(counts["texts"]["cells"]["pairs-from-first"])
    out["fsCellsLow"] = str(low)
    out["fsCellsHigh"] = str(high)
    fk = load("fskeyed")
    out["fskReaching"] = str(fk["reaching"])
    out["fskWindows"] = str(fk["windows"])
    out["fsRegroupedA"], out["fsRegroupedB"] = (str(x) for x in counts["texts"]["regrouped"]["pairs-from-first"])
    out["fsStandardWindows"] = n(counts["standard_windows"])
    out["fsStandardFewest"] = str(counts["standard_fewest_larger_side"])
    out["fsKeyedDraws"] = n(counts["keyed_draws"])
    out["fsKeyedFewest"] = str(counts["keyed_fewest_larger_side"])
    out["fsKeyedReaching"] = str(counts["keyed_reaching_cells"])
    out["fsRecovered"] = str(fs["planted_recovered"])
    out["fsPlanted"] = str(len(fs["planted"]))
    out["fsPlantedLow"] = d(fs["planted_lowest_true"])
    out["fsSteps"] = n(fs["search"]["steps"])
    out["fsRestarts"] = str(fs["search"]["restarts"])
    rows = fs["searched"]
    out["fsCellsBest"] = d(max(r["per_letter"] for k, r in rows.items() if k.startswith("cells")))
    out["fsRegroupedBest"] = d(max(r["per_letter"] for k, r in rows.items() if k.startswith("regrouped")))
    out["fsShufflesMin"] = str(min(r["shuffles_as_high"] for r in rows.values()))
    out["fsShuffles"] = str(len(next(iter(rows.values()))["shuffles"]))

    pm = load("pairmap")
    t = pm["texts"]
    out["pairCellsA"] = str(t["cells"]["phase 0"]["different_pairs"])
    out["pairCellsB"] = str(t["cells"]["phase 1"]["different_pairs"])
    out["pairCellsAMany"] = n(t["cells"]["phase 0"]["windows_as_many"])
    out["pairCellsBMany"] = n(t["cells"]["phase 1"]["windows_as_many"])
    out["pairRegrouped"] = str(t["regrouped"]["phase 0"]["different_pairs"])
    out["pairRegroupedAMany"] = n(t["regrouped"]["phase 0"]["windows_as_many"])
    out["pairRegroupedBMany"] = n(t["regrouped"]["phase 1"]["windows_as_many"])

    gr = load("grillec")
    for case in ("known", "joint", "seeded"):
        found, total = gr["recovered"][case]
        out[f"grille{case.capitalize()}"] = f"{found} of {total}"
    out["grilleJointSteps"] = n(gr["search"]["joint"]["steps"])
    joint = [pl for pl in gr["planted"] if pl["case"] == "joint"]
    out["grilleJointHolesHigh"] = str(max(pl["holes_right"] for pl in joint))

    q = load("quick")
    out["quickRecovered"] = str(q["planted_recovered"])
    out["quickPlanted"] = str(len(q["planted"]))
    out["quickPlantedLow"] = d(q["planted_lowest_true"])
    out["quickVariants"] = str(q["search"]["variants"])
    out["quickShuffles"] = str(q["search"]["shuffles"])
    out["quickBest"] = d(q["searched_best"]["per_letter"])
    out["quickShuffleBestHigh"] = d(max(q["shuffle_bests"]))
    out["quickShuffleBestLow"] = d(min(q["shuffle_bests"]))
    out["quickShuffleBestAsHigh"] = str(q["shuffle_bests_as_high"])
    sp = q["spaces"]
    out["spacesSeparators"] = str(sp["separators"])
    cells = _cells_list()
    rare = {c for i, c in enumerate(cells) if i % 14 == 13} - {c for i, c in enumerate(cells) if i % 14 != 13}
    words, word = [], 0
    for cell in cells:
        if cell in rare:
            if word:
                words.append(word)
            word = 0
        else:
            word += 1
    if word:
        words.append(word)
    out["spacesWords"] = str(len(words))
    out["spacesLetters"] = str(sp["letters"])
    out["spacesMean"] = p(sum(words) / len(words), 1)
    out["spacesEnglishMax"] = p(sp["english_longest_mean_word"], 1)
    out["spacesRuns"] = n(sp["english_runs"])
    out["spacesDistinct"] = str(sp["distinct_letters"])
    out["spacesEnglishFewest"] = str(sp["english_fewest_distinct"])
    cd = q["column_digits"]
    out["coincidenceA"] = p(cd["phase 0"]["coincidence"], 4)
    out["coincidenceB"] = p(cd["phase 1"]["coincidence"], 4)
    out["coincidenceEnglishLow"] = p(min(r["english_lowest"] for r in cd.values()), 4)
    out["coincidenceWindows"] = n(cd["phase 0"]["english_windows"])
    out["coincidenceShufflesA"] = n(cd["phase 0"]["shuffles_at_or_above"])
    out["coincidenceShufflesB"] = n(cd["phase 1"]["shuffles_at_or_above"])
    out["coincidenceShuffles"] = n(cd["phase 0"]["shuffles"])

    h = load("homophone")
    out["homCap"] = str(h["search"]["letter_cap"])
    out["homRecovered"] = str(h["planted_recovered"])
    out["homPlanted"] = str(len(h["planted"]))
    out["homPlantedLow"] = d(h["planted_lowest_true"])
    out["homCells"] = d(h["searched"]["cells"]["per_letter"])
    out["homCellsAsHigh"] = str(h["searched"]["cells"]["shuffles_as_high"])
    out["homRegrouped"] = d(h["searched"]["regrouped"]["per_letter"])
    out["homRegroupedAsHigh"] = str(h["searched"]["regrouped"]["shuffles_as_high"])
    out["homShuffles"] = str(len(h["searched"]["cells"]["shuffles"]))

    a = load("additive")
    rows = a["counts"]["rows"]
    out["addDraws"] = n(sum(r["draws"] for r in rows))
    out["addFewest"] = str(min(r["fewest_distinct"] for r in rows))
    out["addReaching"] = str(sum(r["reaching_cells"] for r in rows))
    out["addTopRows"] = str(a["counts"]["cells"]["top_three_rows"])
    out["addTopRowsEnglish"] = str(max(r["most_in_top_three_rows"] for r in rows))
    out["addRecovered"] = str(a["planted_recovered"])
    out["addPlanted"] = str(len(a["planted"]))
    out["addPlantedLow"] = d(a["planted_lowest_true"])
    out["addBest"] = d(a["searched_best"])
    out["addSteps"] = n(a["search"]["steps"])
    out["addRestarts"] = str(a["search"]["restarts"])
    out["addCases"] = str(len(a["searched"]))
    out["addAsHighMin"] = str(min(r["shuffles_as_high"] for r in a["searched"].values()))
    out["addShuffles"] = str(len(next(iter(a["searched"].values()))["shuffles"]))

    dr = load("direction")
    out["dirTransforms"] = n(dr["search"]["transforms"])
    out["dirShuffles"] = str(dr["search"]["shuffles"])
    out["dirRecovered"] = str(dr["planted_recovered"])
    out["dirPlanted"] = str(len(dr["planted"]))
    out["dirPlantedLow"] = d(dr["planted_lowest_true"])
    fam = dr["families"]
    out["dirBest"] = d(fam["all"]["cells_best"])
    out["dirShuffleBestHigh"] = d(max(fam["all"]["shuffle_bests"]))
    out["dirShuffleBestLow"] = d(min(fam["all"]["shuffle_bests"]))
    out["dirAsHigh"] = str(fam["all"]["shuffle_bests_as_high"])
    top = dr["top"][0]
    out["dirTopTransform"] = top["transform"].replace(":", "{:}")
    out["dirTopZ"] = p(top["z"])
    out["dirTopScore"] = d(top["per_letter"])
    e = load("errors")
    ec = e["counts"]
    out["errWindows"] = n(ec["windows"])
    out["errBestFewest"] = str(ec["best_case_fewest"])
    out["errBestMedian"] = p(ec["best_case_median"], 0)
    out["errRandomDraws"] = n(sum(r["draws"] for r in ec["random"]))
    out["errRandomFewest"] = str(min(r["fewest_remaining"] for r in ec["random"]))
    out["errCells"] = d(e["cells_per_letter"])
    out["errEightLow"] = d(e["by_errors"]["8"]["found_low"])
    out["errEightRight"] = str(round(100 * e["by_errors"]["8"]["letters_right_low"]))
    out["errSixteenLow"] = d(e["by_errors"]["16"]["found_low"])
    out["errLevel"] = str(e["fewest_errors_at_cells_level"])
    out["errLevelRight"] = str(round(100 * e["by_errors"][str(e["fewest_errors_at_cells_level"])]["letters_right_low"]))
    out["corpusClosestDistance"] = str(load("corpus")["closest_sorted_distance"] // 2)

    it = json.loads((CACHE / "dagapeyeff-italian.json").read_text(encoding="utf-8"))
    out["itLetters"] = n(it["counts"]["letters"])
    out["itWindows"] = n(it["counts"]["windows"])
    out["itFewest"] = str(it["counts"]["fewest_errors"])
    out["itMedian"] = p(it["counts"]["median_errors"], 0)
    out["itCells"] = d(it["cells_per_letter"])
    out["itAsHigh"] = str(it["shuffles_as_high"])
    out["itRecovered"] = str(it["planted_recovered"])
    out["itErrRecovered"] = str(it["planted_with_errors_recovered"])

    sc = load("screen")
    out["screenLanguages"] = str(len(sc["languages"]))
    latin = sc["languages"]["Latin-ITTB"]
    out["screenLatinFewest"] = str(latin["fewest_errors"])
    out["screenLatinMedian"] = p(latin["median_errors"], 0)
    out["screenLatinWithin"] = str(latin["within_8"])
    perseus = sc["languages"]["Latin-Perseus"]
    out["screenPerseusFewest"] = str(perseus["fewest_errors"])
    out["screenPerseusWithin"] = str(perseus["within_8"])
    out["screenGermanFewest"] = str(sc["languages"]["German-GSD"]["fewest_errors"])
    out["screenRussianFewest"] = str(sc["languages"]["Russian-GSD"]["fewest_errors"])
    out["screenFrenchFewest"] = str(sc["languages"]["French-GSD"]["fewest_errors"])
    others = [row["median_errors"] for name, row in sc["languages"].items() if not name.startswith("Latin")]
    out["screenOthersMedianLow"] = p(min(others), 0)

    la = load("latin")
    out["laRecovered"] = str(la["planted_recovered"])
    out["laErrRecovered"] = str(la["planted_with_errors_recovered"])
    out["laTrainLetters"] = n(la["letters"]["train"])
    out["laSquare"] = d(la["searched"]["cells"]["square"])
    out["laSquareAsHigh"] = str(la["searched"]["cells"]["square_shuffles_as_high"])
    out["laBest"] = d(la["searched"]["cells"]["best"])
    out["laBestAsHigh"] = str(la["searched"]["cells"]["shuffle_bests_as_high"])
    out["laClassicalLow"] = d(min(pl["true_per_letter"] for pl in la["planted"] if pl["case"] == "classical 0"))
    l14 = load("latin14")
    out["laFourteenRecovered"] = str(l14["planted_recovered"])
    out["laFourteenPlanted"] = str(len(l14["planted"]))
    out["laFourteenUndone"] = d(l14["searched"]["cells undone"]["per_letter"])
    out["laFourteenUndoneHigh"] = str(l14["searched"]["cells undone"]["shuffles_as_high"])
    out["laFourteenDone"] = d(l14["searched"]["cells done"]["per_letter"])
    out["laFourteenDoneHigh"] = str(l14["searched"]["cells done"]["shuffles_as_high"])
    out["laFourteenShuffles"] = str(len(l14["searched"]["cells done"]["shuffles"]))
    out["laFourteenRegroupedHigh"] = str(max(l14["searched"][k]["shuffles_as_high"]
                                             for k in ("regrouped undone", "regrouped done")))

    tg = load("tongues")["languages"]
    wide = load("romanian-wide")
    out["caCells"] = d(tg["Catalan-AnCora"]["searched"]["cells"]["best"])
    out["caCellsHigh"] = str(tg["Catalan-AnCora"]["searched"]["cells"]["shuffle_bests_as_high"])
    out["roCells"] = d(tg["Romanian-RRT"]["searched"]["cells"]["best"])
    out["roCellsHigh"] = str(tg["Romanian-RRT"]["searched"]["cells"]["shuffle_bests_as_high"])
    out["roWideHigh"] = str(wide["searched"]["cells"]["shuffle_bests_as_high"])
    out["roWideRegroupedHigh"] = str(wide["searched"]["regrouped"]["shuffle_bests_as_high"])
    out["roWideShuffles"] = str(wide["shuffles"])

    ks = load("keyedsquares")
    out["ksRecovered"] = str(ks["planted_recovered"])
    out["ksPlanted"] = str(len(ks["planted"]))
    out["ksWrong"] = d(ks["highest_wrong_found"])
    out["ksSteps"] = n(ks["search"]["steps"])

    nm = load("nomessage")
    out["nmFamilyP"] = p(nm["cells"]["family_p"], 4)
    out["nmSmallestP"] = p(nm["cells"]["smallest_p"], 4)
    out["nmStatistics"] = str(len(nm["statistics"]))
    out["nmFixed"] = str(len(nm["fixed_places"]))
    for key, name in (("nmSquare", "keyed square"), ("nmDone", "columnar 14 done"), ("nmUndone", "columnar 14 undone"),
                      ("nmGrille", "turning grille"), ("nmShift", "repeating shift"), ("nmRandom", "random transposition")):
        out[key] = str(nm["power"][name]["flagged"])
    out["nmPlanted"] = str(nm["power"]["keyed square"]["planted"])

    lm = load("latinmore")
    out["lmShiftReaching"] = str(sum(r["reaching_cells"] for r in lm["shift_counts"]["rows"]))
    out["lmShiftDraws"] = n(sum(r["draws"] for r in lm["shift_counts"]["rows"]))
    out["lmShiftFewest"] = str(min(r["fewest_distinct"] for r in lm["shift_counts"]["rows"]))
    out["lmFsRecovered"] = str(lm["foursquare"]["planted_recovered"])
    out["lmFsCellsHigh"] = str(lm["foursquare"]["searched"]["cells"]["shuffles_as_high"])
    out["lmHomRecovered"] = str(lm["homophone"]["planted_recovered"])
    ls = load("latinshift")
    out["lsRecovered"] = str(ls["planted_recovered"])
    out["lsPlanted"] = str(len(ls["planted"]))
    out["lsBest"] = d(ls["searched_best"]["per_letter"])
    out["lsAbove"] = str(ls["cases_cells_above_all_shuffles"])
    out["lsCases"] = str(len(ls["searched"]))
    # Draft 2: every language, more Latin, and Latin at widths 10 to 15.
    al = load("alllanguages")
    rows = al["languages"]
    out["allLanguages"] = str(len(rows))
    out["allListed"] = str(len(rows) + len(al["skipped"]))
    out["allSkippedScript"] = str(sum(1 for s in al["skipped"] if s["reason"].startswith("script")))
    out["allSkippedEmpty"] = str(sum(1 for s in al["skipped"] if s["reason"].startswith("no sentence")))
    rs = {row["probe"]: row for row in load("reseed")["rows"]}
    for key, name in (("Fs", "foursquare"), ("Add", "additive")):
        second = rs[name]["second"]
        out[f"rs{key}Recovered"] = str(second["recovered"])
        out[f"rs{key}Planted"] = str(second["planted"])
        out[f"rs{key}Best"] = d(second["searched_best"])
        out[f"rs{key}Gap"] = p(second["gap"])
        out[f"rs{key}AsHigh"] = str(second["shuffles_as_high"])
        out[f"rs{key}Shuffles"] = str(second["shuffles"])
    english = [row for row in rs.values() if not row["probe"].startswith(("latin", "shiftgap latin"))]
    weakest = min(english, key=lambda row: row["second"]["gap"])
    out["rsRows"] = str(len(rs))
    out["rsEnglishLow"] = p(weakest["second"]["gap"])
    out["rsEnglishLowFound"] = d(weakest["second"]["weakest_recovered"])
    out["rsEnglishLowCells"] = d(weakest["second"]["searched_best"])
    out["rsEnglishLowFirstCells"] = d(weakest["first"]["searched_best"])
    out["rsGapLow"] = p(min(row[run]["gap"] for row in rs.values() for run in ("first", "second")))
    lfs = rs["latinmore foursquare"]
    out["rsLaFsRecovered"] = str(lfs["second"]["recovered"])
    out["rsLaFsPlanted"] = str(lfs["second"]["planted"])
    out["corpusMedianErrors"] = str(load("corpus")["median_sorted_distance"] // 2)
    outliers = []
    for name, median in screen_outliers():
        row = al["languages"][name]
        label = name.replace("_", " ").replace("-", " (", 1) + ")"
        outliers.append(label + (", romanized" if row["script"] != "latin" else "") + f", at {median}")
    if len(outliers) != 1:
        raise SystemExit("alllanguages: Figure 2's caption names exactly one language off its scale")
    out["screenOutliers"] = outliers[0]
    short = [s for s in al["skipped"] if s["reason"].endswith(" letters")]
    out["allSkippedShort"] = str(len(short))
    out["allSkippedShortMost"] = n(max(int(s["reason"].split()[0]) for s in short))
    if any(not s["reason"].startswith(("script", "no sentence")) and not s["reason"].endswith(" letters") for s in al["skipped"]):
        raise SystemExit("alllanguages: a skipped treebank has a reason the manuscript does not state")
    latin = rows["Latin-ITTB"]
    others = {k: v for k, v in rows.items() if k != "Latin-ITTB"}
    out["allLatinMedian"] = p(latin["median_errors"], 0)
    out["allOthersMedianLow"] = p(min(v["median_errors"] for v in others.values()), 0)
    out["allLatinRate"] = n(round(latin["within_8_per_million_windows"]))
    second = max(others, key=lambda k: others[k]["within_8_per_million_windows"])
    out["allSecondRate"] = n(round(others[second]["within_8_per_million_windows"]))
    out["allSecondRateName"] = second.split("-")[0].replace("_", " ")
    out["allSecondRateLetters"] = n(others[second]["letters"])
    big = {k: v for k, v in others.items() if v["letters"] >= 1_000_000}
    out["allBigRateHigh"] = n(round(max(v["within_8_per_million_windows"] for v in big.values())))
    out["allEstonianFewest"] = str(rows["Estonian-EDT"]["fewest_errors"])
    out["allEstonianMedian"] = p(rows["Estonian-EDT"]["median_errors"], 0)
    ru = load("russian")
    out["ruFewest"] = str(ru["fewest_errors"])
    out["ruWithin"] = str(ru["windows_within_8"])
    out["ruRows"] = str(len(ru["rows"]))
    eo = load("esperanto")
    out["eoFewest"] = str(eo["esperanto"]["fewest_errors"])
    out["eoMedian"] = p(eo["esperanto"]["median_errors"], 0)
    out["eoLetters"] = n(eo["esperanto"]["letters"])
    lib = load("latinlib")
    ll = load("latinlibrary")
    out["libLetters"] = n(lib["letters"])
    out["libSources"] = str(len(lib["sources"]))
    out["libFewest"] = str(lib["fewest_errors"])
    out["llLetters"] = n(ll["letters"])
    out["llPages"] = n(ll["pages_screened"])
    out["llFewest"] = str(ll["fewest_errors"])
    out["llWithinFour"] = str(ll["within_4"])
    out["latinLettersAll"] = p((lib["letters"] + ll["letters"]) / 1e6, 1)
    out["latinWithinTwo"] = str(lib["within_2"] + ll["within_2"])
    lw = load("latinw")
    out["lwRecovered"] = str(lw["planted_recovered"])
    out["lwPlanted"] = str(lw["planted"])
    out["lwCellsLow"] = d(min(r["cells"]["per_letter"] for r in lw["rows"]), 2)
    out["lwCellsHigh"] = d(max(r["cells"]["per_letter"] for r in lw["rows"]), 2)
    out["lwWeakestFound"] = d(min(pl["found_per_letter"] for r in lw["rows"] for pl in r["planted"] if pl["cells_right"] >= 0.9), 2)
    out["lwAsHighLow"] = str(min(r["cells"]["shuffles_as_high"] for r in lw["rows"]))
    lsm = load("latinsmall")
    out["lsmRecovered"] = str(lsm["planted_recovered"])
    out["lsmPlanted"] = str(lsm["planted"])
    out["lsmBest"] = d(lsm["searched_best"], 2)
    out["lsmWeakestFound"] = d(lsm["weakest_recovered_found"], 2)
    out["lsmAbove"] = str(lsm["cases_cells_above_all_shuffles"])
    out["lsmCases"] = str(2 * len(lsm["rows"]))
    lwd = load("latinwords")
    pct = lambda share: str(round(100 * share))
    out["lwdVocab"] = n(lwd["vocabulary"])
    out["lwdSearches"] = str(lwd["searches_per_source"])
    out["lwdCellsBest"] = pct(lwd["searched"]["cells"]["best_coverage"])
    out["lwdCellsAsHigh"] = str(lwd["searched"]["cells"]["shuffles_as_high"])
    out["lwdShuffles"] = str(len(lwd["searched"]["cells"]["shuffle_best_coverages"]))
    out["lwdRegroupedBest"] = pct(lwd["searched"]["regrouped"]["best_coverage"])
    out["lwdRegroupedAsHigh"] = str(lwd["searched"]["regrouped"]["shuffles_as_high"])
    out["lwdPlanted"] = str(lwd["planted"])
    out["lwdAbove"] = str(lwd["planted_above_cells"])
    clean, worst = lwd["planted_by_errors"]["0"], lwd["planted_by_errors"][max(lwd["planted_by_errors"], key=int)]
    out["lwdErrMax"] = max(lwd["planted_by_errors"], key=int)
    out["lwdCleanLow"] = pct(min(clean["coverage"]))
    out["lwdCleanHigh"] = pct(max(clean["coverage"]))
    out["lwdWorstLow"] = pct(min(worst["coverage"]))
    out["lwdWorstHigh"] = pct(max(worst["coverage"]))
    out["lwdWorstRecovered"] = str(worst["recovered"])
    out["lwdWorstPlanted"] = str(worst["planted"])
    lg = load("latingrille")
    fx = lg["fixed_by_spoiled"]
    out["lgPlanted"] = str(fx["0.0"]["of"])
    out["lgExact"] = str(fx["0.0"]["recovered"])
    out["lgMid"] = str(fx["0.15"]["recovered"])
    out["lgMidLow"] = str(round(100 * min(fx["0.15"]["key_cells_right"])))
    out["lgMidHigh"] = str(round(100 * max(fx["0.15"]["key_cells_right"])))
    out["lgLow"] = str(fx["0.3"]["recovered"])
    out["lgLowLow"] = str(round(100 * min(fx["0.3"]["key_cells_right"])))
    out["lgLowHigh"] = str(round(100 * max(fx["0.3"]["key_cells_right"])))
    out["lgNested"] = str(lg["nested_recovered"])
    out["lgNestedOf"] = str(len(lg["nested"]))
    out["lgNestedHoles"] = str(lg["nested_holes_high"])
    ld = load("latindouble")["by_size"]
    out["ldSmall"] = str(ld["4x5"]["recovered"] + ld["5x7"]["recovered"])
    out["ldSmallOf"] = str(ld["4x5"]["of"] + ld["5x7"]["of"])
    out["ldSix"] = str(ld["6x8"]["recovered"])
    out["ldSixOf"] = str(ld["6x8"]["of"])
    out["ldLarge"] = str(ld["7x9"]["recovered"] + ld["9x11"]["recovered"])
    rc = load("rarecolumn")
    out["rcSymbolsRest"] = str(rc["symbols_without_private"])
    out["rcCellsRest"] = str(rc["cells_without_private"])
    latin_pad = {k: v for k, v in rc["padding"].items() if k.startswith("Latin")}
    english_pad = {k: v for k, v in rc["padding"].items() if k.startswith("English")}
    out["rcLatinFewest"] = str(min(v["fewest"] for v in latin_pad.values()))
    out["rcClassicalFewest"] = str(next(v["fewest"] for k, v in latin_pad.items() if "classical" in k))
    out["rcEnglishFewest"] = str(min(v["fewest"] for v in english_pad.values()))
    out["rcPadWindows"] = n(sum(v["windows"] for v in rc["padding"].values()))
    out["rcRareWindows"] = n(sum(v["windows"] for v in rc["rare_letters"].values()))
    out["rcRareEnough"] = n(sum(v["five_or_more_rare"] for v in rc["rare_letters"].values()))
    out["rcPacked"] = str(sum(v["rare_in_one_stretch"] for v in rc["rare_letters"].values()))
    out["rcPrivateCells"] = str(rc["private_cells"])
    # Review 2: gaps between the cells and the weakest planted text found, and counts against chance.
    la = load("latin")
    out["gapLatin"] = p(min(pl["found_per_letter"] for pl in la["planted"]) - la["searched"]["cells"]["best"], 2)
    tg = load("tongues")["languages"]
    out["gapRomanian"] = p(min(pl["found_per_letter"] for pl in tg["Romanian-RRT"]["planted"]) - tg["Romanian-RRT"]["searched"]["cells"]["best"], 2)
    out["gapCatalan"] = p(min(pl["found_per_letter"] for pl in tg["Catalan-AnCora"]["planted"]) - tg["Catalan-AnCora"]["searched"]["cells"]["best"], 2)
    h = load("homophone")
    out["gapHom"] = p(min(pl["found_per_letter"] for pl in h["planted"]) - max(r["per_letter"] for r in h["searched"].values()), 2)
    out["roRegroupedFirst"] = d(tg["Romanian-RRT"]["searched"]["regrouped"]["best"])
    out["roRegroupedFirstHigh"] = str(tg["Romanian-RRT"]["searched"]["regrouped"]["shuffle_bests_as_high"])
    wide = load("romanian-wide")
    out["roRegroupedRerun"] = d(wide["searched"]["regrouped"]["best"])
    out["roRegroupedRerunAbove"] = str(sum(s > tg["Romanian-RRT"]["searched"]["regrouped"]["best"] for s in wide["searched"]["regrouped"]["shuffle_bests_high"]))
    ex = load("exhaustive")["rows"]
    out["exAboveAll"] = str(sum(r["cells"]["shuffles_as_high"] == 0 for r in ex))
    out["exCasesAll"] = str(len(ex))
    from math import comb
    k, m = sum(r["cells"]["shuffles_as_high"] == 0 for r in ex), len(ex)
    out["exAboveP"] = p(sum(comb(m, j) * 0.25 ** j * 0.75 ** (m - j) for j in range(k, m + 1)), 3)
    out["exAboveChance"] = str(round(m / 4))
    sg = load("shiftgap")
    for lang, tag in (("english", "En"), ("latin", "La")):
        x = sg[lang]
        out[f"sg{tag}Draws"] = n(sum(r["draws"] for r in x["counts"]))
        out[f"sg{tag}Fewest"] = str(min(r["fewest_distinct"] for r in x["counts"]))
        out[f"sg{tag}Reaching"] = str(sum(r["reaching_cells"] for r in x["counts"]))
        out[f"sg{tag}Recovered"] = str(x["planted_recovered"])
        out[f"sg{tag}Planted"] = str(len(x["planted"]))
        out[f"sg{tag}Best"] = d(x["searched_best"]["per_letter"])
        out[f"sg{tag}Above"] = str(x["cases_cells_above_all_shuffles"])
        out[f"sg{tag}Cases"] = str(len(x["searched"]))
        out[f"sg{tag}Chance"] = str(round(len(x["searched"]) / 4))
    nm = load("nomessage")
    out["nmCellNull"] = n(20_000)
    out["nmPlantNull"] = n(2_000)
    return out


def screen_table() -> str:
    sc = load("alllanguages")
    lines = ["\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
             "Treebank & Letters & Fewest & Median & Within 8 per million \\\\", "\\midrule"]
    for name in sc["ranked"][:12]:
        row = sc["languages"][name]
        label = name.replace("_", " ").replace("-", " (", 1) + ")"
        if row["script"] != "latin":
            label += ", romanized"
        lines.append(f"{label} & {n(row['letters'])} & {row['fewest_errors']} & {row['median_errors']:.0f} & "
                     f"{n(round(row['within_8_per_million_windows']))} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines) + "\n"


def power_table() -> str:
    """One row per searched family: planted recovered, weakest planted text, the cells' best, shuffles as high."""
    rows = []

    def row(family: str, recovered: str, planted: str, cells: str, shuffles: str) -> None:
        rows.append(f"{family} & {recovered} & {planted} & {cells} & {shuffles} \\\\")

    columnar = load("columnar")
    small = [r for r in columnar["rows"] if r["width"] in (1, 2, 4, 7)]
    row("Keyed square; columnar widths 1, 2, 4, 7",
        f"{sum(r['planted_recovered'] for r in small)}/{sum(len(r['planted']) for r in small)}",
        d(min(pl["true_per_letter"] for r in small for pl in r["planted"]), 2),
        d(max(r["cells_per_letter"] for r in small), 2),
        f"{min(r['shuffles_as_high'] for r in small)}--{max(r['shuffles_as_high'] for r in small)}/4")
    c14 = load("columnar14c")
    rec = c14["planted_recovered"]
    best = max(c14["searched"].values(), key=lambda r: r["per_letter"])
    row("Columnar width 14, both directions",
        f"{sum(v[0] for v in rec.values())}/{sum(v[1] for v in rec.values())}",
        d(c14["planted_lowest_true"], 2), d(best["per_letter"], 2),
        f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    fs = load("foursquare")
    best = max(fs["searched"].values(), key=lambda r: r["per_letter"])
    row("Four-square", f"{fs['planted_recovered']}/{len(fs['planted'])}", d(fs["planted_lowest_true"], 2),
        d(best["per_letter"], 2), f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    a = load("additive")
    best = max(a["searched"].values(), key=lambda r: r["per_letter"])
    row("Repeating shift, periods 2--5, 7, 14", f"{a['planted_recovered']}/{len(a['planted'])}",
        d(a["planted_lowest_true"], 2), d(best["per_letter"], 2),
        f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    sg = load("shiftgap")
    for lang, label in (("english", "Repeating shift, periods 6, 8--13"),):
        x = sg[lang]
        row(label, f"{x['planted_recovered']}/{len(x['planted'])}", d(min(r["true_per_letter"] for r in x["planted"]), 2),
            d(x["searched_best"]["per_letter"], 2), f"{x['searched_best']['shuffles_as_high']}/{len(x['searched_best']['shuffles'])}")
    q = load("quick")
    row("Nulls by place; reversed; column digits", f"{q['planted_recovered']}/{len(q['planted'])}",
        d(q["planted_lowest_true"], 2), d(q["searched_best"]["per_letter"], 2),
        f"{q['shuffle_bests_as_high']}/{len(q['shuffle_bests'])}\\textsuperscript{{a}}")
    h = load("homophone")
    best = max(h["searched"].values(), key=lambda r: r["per_letter"])
    row("Homophonic key, capped", f"{h['planted_recovered']}/{len(h['planted'])}", d(h["planted_lowest_true"], 2),
        d(best["per_letter"], 2), f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    dr = load("direction")
    fam = dr["families"]["all"]
    row("Delays, nulls 2--14, rails, columns 10--28", f"{dr['planted_recovered']}/{len(dr['planted'])}",
        d(dr["planted_lowest_true"], 2), d(fam["cells_best"], 2),
        f"{fam['shuffle_bests_as_high']}/{len(fam['shuffle_bests'])}\\textsuperscript{{a}}")
    e = load("errors")
    row("Keyed square with 8 enciphering slips", f"{sum(1 for r in e['planted'] if r['errors'] == 8 and r['letters_right'] >= 0.9)}/"
        f"{sum(1 for r in e['planted'] if r['errors'] == 8)}", d(e["by_errors"]["8"]["found_low"], 2),
        d(e["cells_per_letter"], 2), "--")
    it = json.loads((CACHE / "dagapeyeff-italian.json").read_text(encoding="utf-8"))
    row("Italian keyed square (0 and 8 slips)", f"{it['planted_recovered'] + it['planted_with_errors_recovered']}/8",
        d(it["planted_with_errors_lowest_found"], 2), d(it["cells_per_letter"], 2), f"{it['shuffles_as_high']}/8")
    la = load("latin")
    row("Latin keyed square and dummy rule (0 and 8 slips)",
        f"{la['planted_recovered'] + la['planted_with_errors_recovered']}/12",
        d(min(r["found_per_letter"] for r in la["planted"]), 2), d(la["searched"]["cells"]["best"], 2),
        f"{la['searched']['cells']['shuffle_bests_as_high']}/8\\textsuperscript{{a}}")
    l14 = load("latin14")
    best = max(l14["searched"].values(), key=lambda r: r["per_letter"])
    row("Latin, columnar width 14 (0 and 8 wrong cells)", f"{l14['planted_recovered']}/{len(l14['planted'])}",
        d(min(r["found_per_letter"] for r in l14["planted"]), 2), d(best["per_letter"], 2),
        f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    lw = load("latinw")
    best = max((r["cells"] for r in lw["rows"]), key=lambda c: c["per_letter"])
    row("Latin, columnar widths 10--13, 15 (0 and 8 wrong cells)", f"{lw['planted_recovered']}/{lw['planted']}",
        d(min(pl["found_per_letter"] for r in lw["rows"] for pl in r["planted"] if pl["cells_right"] >= 0.9), 2),
        d(best["per_letter"], 2), f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    lsm = load("latinsmall")
    best = max((r["cells"] for r in lsm["rows"]), key=lambda c: c["per_letter"])
    row("Latin, columnar widths 2--9 (0 and 8 wrong cells)", f"{lsm['planted_recovered']}/{lsm['planted']}",
        d(lsm["weakest_recovered_found"], 2), d(best["per_letter"], 2),
        f"{best['shuffles_as_high']}/{len(best['shuffles'])}")
    ls = load("latinshift")
    row("Latin, repeating shift, periods 2--5, 7, 14", f"{ls['planted_recovered']}/{len(ls['planted'])}",
        d(min(r["true_per_letter"] for r in ls["planted"]), 2), d(ls["searched_best"]["per_letter"], 2),
        f"{ls['searched_best']['shuffles_as_high']}/{len(ls['searched_best']['shuffles'])}")
    x = sg["latin"]
    row("Latin, repeating shift, periods 6, 8--13", f"{x['planted_recovered']}/{len(x['planted'])}",
        d(min(r["true_per_letter"] for r in x["planted"]), 2), d(x["searched_best"]["per_letter"], 2),
        f"{x['searched_best']['shuffles_as_high']}/{len(x['searched_best']['shuffles'])}")
    wide = load("romanian-wide")
    tg = load("tongues")["languages"]
    for lang, label in (("Catalan-AnCora", "Catalan"), ("Romanian-RRT", "Romanian")):
        x = tg[lang]
        shuffles = (f"{wide['searched']['cells']['shuffle_bests_as_high']}/{wide['shuffles']}" if label == "Romanian"
                    else f"{x['searched']['cells']['shuffle_bests_as_high']}/8")
        row(f"{label} keyed square and dummy rule (0 and 8 slips)",
            f"{x['planted_recovered'] + x['planted_with_errors_recovered']}/6",
            d(min(r["found_per_letter"] for r in x["planted"]), 2),
            d((wide["searched"]["cells"]["best"] if label == "Romanian" else x["searched"]["cells"]["best"]), 2),
            shuffles + "\\textsuperscript{a}")
    head = ("\\begin{tabular}{@{}p{0.34\\linewidth}cccc@{}}\n\\toprule\n"
            "Family searched & Planted found & Weakest planted & Cells' best & Shuffles as high \\\\\n\\midrule")
    return head + "\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"


def _power_rows() -> list[tuple[str, float, float]]:
    """Each row of the power table as its family, the weakest planted text's score and the cells' best."""
    out = []
    for line in power_table().splitlines():
        found = re.findall(r"\\ensuremath\{(-?[0-9.]+)\}", line)
        if len(found) >= 2:
            out.append((line.split("&")[0].strip(), float(found[0]), float(found[1])))
    return out


def power_figure() -> str:
    """Figure: for each family of the power table, its weakest recovered planted text and the cells' best."""
    rows = _power_rows()
    count = len(rows)
    labels = ",".join("{" + label.replace("--", "\\textendash{}") + "}" for label, _, _ in rows)
    lines = ["\\begin{tikzpicture}",
             "\\begin{axis}[width=0.52\\linewidth, height=0.62\\linewidth, xmin=-4.8, xmax=-1.6,",
             f"  ymin=0.4, ymax={count}.6, ytick={{1,...,{count}}}, yticklabels={{{labels}}},",
             "  y dir=reverse, yticklabel style={font=\\scriptsize, align=right}, xticklabel style={font=\\scriptsize},",
             "  xlabel={Score, nats a letter}, xlabel style={font=\\small}, xmajorgrids, grid style={gray!25},",
             "  legend style={font=\\scriptsize, at={(0.5,1.02)}, anchor=south, legend columns=2, draw=none,\n"
             "  /tikz/every even column/.append style={column sep=1em}}, legend cell align=left]"]
    for index, (_, planted, cells) in enumerate(rows, start=1):
        lines.append(f"\\addplot[gray!60, forget plot] coordinates {{({cells:.2f},{index}) ({planted:.2f},{index})}};")
    lines.append("\\addplot[only marks, mark=*, mark size=1.6pt, black] coordinates {"
                 + " ".join(f"({planted:.2f},{index})" for index, (_, planted, _) in enumerate(rows, start=1)) + "};")
    lines.append("\\addlegendentry{Weakest planted text}")
    lines.append("\\addplot[only marks, mark=x, mark size=2.4pt, thick, black] coordinates {"
                 + " ".join(f"({cells:.2f},{index})" for index, (_, _, cells) in enumerate(rows, start=1)) + "};")
    lines.append("\\addlegendentry{Cells' best}")
    lines += ["\\end{axis}", "\\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


SCREEN_CLIP = 60


def screen_outliers() -> list[tuple[str, int]]:
    """Languages whose median is off the scale of Figure 2, by name and median."""
    sc = load("alllanguages")
    return [(name, round(sc["languages"][name]["median_errors"])) for name in sc["ranked"]
            if round(sc["languages"][name]["median_errors"]) > SCREEN_CLIP]


def screen_figure() -> str:
    """Figure: how many of the screened languages have each median number of errors, Latin apart."""
    sc = load("alllanguages")
    counts: dict[int, int] = {}
    latin = None
    for name in sc["ranked"]:
        median = round(sc["languages"][name]["median_errors"])
        if name == "Latin-ITTB":
            latin = median
            continue
        if median > SCREEN_CLIP:
            continue
        counts[median] = counts.get(median, 0) + 1
    others = " ".join(f"({median},{count})" for median, count in sorted(counts.items()))
    lines = ["\\begin{tikzpicture}",
             "\\begin{axis}[width=0.9\\linewidth, height=0.36\\linewidth, ybar=0pt, bar width=3.5pt, bar shift=0pt,",
             f"  xmin={min(min(counts), latin) - 3}, xmax={max(counts) + 2}, ymin=0, enlarge y limits={{upper, value=0.15}},",
             "  xlabel={Fewest errors at the median window of 196 letters}, ylabel={Languages},",
             "  label style={font=\\small}, ticklabel style={font=\\scriptsize}, ymajorgrids, grid style={gray!25},",
             "  legend style={font=\\scriptsize, draw=none, at={(0.98,0.95)}, anchor=north east}, legend cell align=left, area legend]",
             f"\\addplot[fill=gray!45, draw=gray!70] coordinates {{{others}}};",
             f"\\addlegendentry{{Other languages ({len(sc['ranked']) - 1 - len(screen_outliers())} shown)}}",
             f"\\addplot[fill=black, draw=black] coordinates {{({latin},1)}};",
             "\\addlegendentry{Latin (ITTB)}",
             "\\end{axis}", "\\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


def words_figure() -> str:
    """Figure: Latin word coverage of the planted texts by wrong cells, against the cells' and shuffles' best."""
    lw = load("latinwords")
    by = lw["planted_by_errors"]
    errors = sorted(by, key=int)
    planted = [r for r in lw["rows"] if r["kind"] == "planted"]
    if sorted(round(r["coverage"], 4) for r in planted) != sorted(c for e in errors for c in by[e]["coverage"]):
        raise SystemExit("latinwords: the planted rows and planted_by_errors disagree")
    def place(rows: list[dict]) -> str:
        out = []
        for e in errors:
            column = sorted((r for r in rows if str(r["errors"]) == e), key=lambda r: r["coverage"])
            for i, r in enumerate(column):
                out.append(f"({int(e) + 0.5 * ((i % 5) - 2):.1f},{100 * r['coverage']:.1f})")
        return " ".join(out)
    found = place([r for r in planted if r["clean_cells_right"] >= 0.9])
    missed = place([r for r in planted if r["clean_cells_right"] < 0.9])
    cells = 100 * lw["searched"]["cells"]["best_coverage"]
    shuffle = 100 * max(lw["searched"]["cells"]["shuffle_best_coverages"])
    low, high = int(errors[0]) - 3, int(errors[-1]) + 3
    lines = ["\\begin{tikzpicture}",
             "\\begin{axis}[width=0.9\\linewidth, height=0.42\\linewidth,",
             f"  xmin={low}, xmax={high}, ymin=0, ymax=90, xtick={{{','.join(errors)}}},",
             "  xlabel={Wrong cells in the planted text, of 196}, ylabel={Letters in Latin words, \\%},",
             "  label style={font=\\small}, ticklabel style={font=\\scriptsize}, ymajorgrids, grid style={gray!25},",
             "  legend style={font=\\scriptsize, draw=none, at={(0.98,0.95)}, anchor=north east}, legend cell align=left]",
             f"\\addplot[only marks, mark=*, mark size=1.5pt, black] coordinates {{{found}}};",
             "\\addlegendentry{Planted Latin, recovered}",
             f"\\addplot[only marks, mark=o, mark size=1.5pt, black] coordinates {{{missed}}};",
             "\\addlegendentry{Planted Latin, not recovered}",
             f"\\addplot[dashed, thick, black] coordinates {{({low},{cells:.1f}) ({high},{cells:.1f})}};",
             "\\addlegendentry{Cells' best}",
             f"\\addplot[dotted, thick, gray] coordinates {{({low},{shuffle:.1f}) ({high},{shuffle:.1f})}};",
             "\\addlegendentry{Shuffles' best}",
             "\\end{axis}", "\\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


_RESEED_LABELS = {
    "foursquare": "Four-square",
    "additive": "Repeating shift, periods 2--5, 7, 14",
    "shiftgap english": "Repeating shift, periods 6, 8--13",
    "shiftgap latin": "Latin, repeating shift, periods 6, 8--13",
    "latin14": "Latin, columnar width 14",
    "latinw": "Latin, columnar widths 10--13, 15",
    "latinmore foursquare": "Latin, four-square",
    "latinmore homophone": "Latin, capped homophonic key",
    "latinshift": "Latin, repeating shift, periods 2--5, 7, 14",
}


def reseed_table() -> str:
    """Each rerun search under its first and its second seed."""
    rows = load("reseed")["rows"]
    if [row["probe"] for row in rows] != list(_RESEED_LABELS):
        raise SystemExit("reseed: the frozen rows are not the ones the manuscript's table names")
    lines = ["\\begin{tabular}{@{}p{0.38\\linewidth}lccccc@{}}", "\\toprule",
             "Search & Seed & Found & Weakest & Cells' best & Gap & As high \\\\", "\\midrule"]
    for index, row in enumerate(rows):
        for run, label in (("first", _RESEED_LABELS[row["probe"]]), ("second", "")):
            x = row[run]
            lines.append(f"{label} & {run} & {x['recovered']}/{x['planted']} & {d(x['weakest_recovered'], 2)} & "
                         f"{d(x['searched_best'], 2)} & {p(x['gap'])} & {x['shuffles_as_high']}/{x['shuffles']} \\\\")
        if index < len(rows) - 1:
            lines.append("\\addlinespace[2pt]")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines) + "\n"


def power_gaps() -> dict[str, float]:
    """Weakest planted score minus the cells' best, for each row of the power table."""
    import re

    gaps = {}
    for line in power_table().splitlines():
        found = re.findall(r"\\ensuremath\{(-?[0-9.]+)\}", line)
        if len(found) >= 2:
            gaps[line.split("&")[0].strip()] = float(found[0]) - float(found[1])
    return gaps


def gap_macros() -> dict[str, str]:
    gaps = power_gaps()
    latin = [v for k, v in gaps.items() if k.startswith("Latin")]
    english = [v for k, v in gaps.items() if not k.startswith(("Latin", "Romanian", "Catalan", "Italian"))
               and not k.startswith("Homophonic")]
    return {
        "gapLatinLow": p(min(latin)), "gapLatinHigh": p(max(latin)),
        "gapRomanianTab": p(next(v for k, v in gaps.items() if k.startswith("Romanian"))),
        "gapHomTab": p(next(v for k, v in gaps.items() if k.startswith("Homophonic"))),
        "gapEnglishLow": p(min(english)),
        "gapLatinRows": str(len(latin)),
        "gapLatinUnder": str(sum(v < 1 for v in latin)),
        "gapLatinUnderHigh": p(max(v for v in latin if v < 1)),
        "gapUnderOne": str(sum(v < 1 for v in gaps.values())),
        "gapRows": str(len(gaps)),
    }


def render() -> dict[str, str]:
    values = macros() | gap_macros()
    lines = ["% Written by ../code/make_numbers.py from the frozen search results. Do not edit by hand."]
    for name in INPUTS:
        digest = hashlib.sha256((CACHE / f"dagapeyeff-{name}.json").read_bytes()).hexdigest()
        lines.append(f"% dagapeyeff-{name}.json sha256 {digest}")
    for key in sorted(values):
        lines.append(f"\\newcommand{{\\{key}}}{{{values[key]}}}")
    return {
        "numbers.tex": "\n".join(lines) + "\n",
        "tab_power.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + power_table(),
        "tab_screen.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + screen_table(),
        "tab_reseed.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + reseed_table(),
        "fig_power.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + power_figure(),
        "fig_screen.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + screen_figure(),
        "fig_words.tex": "% Written by ../code/make_numbers.py. Do not edit by hand.\n" + words_figure(),
    }


_TEX = (
    (r"\\ensuremath\{([^{}]*)\}", r"\1"),
    (r"\\emph\{([^{}]*)\}", r"\1"),
    (r"\$5 \\times 5\$", "5 by 5"),
    (r"\$14 \\times 14\$", "14 by 14"),
    (r"\{,\}", ","),
    (r"~", " "),
)


def abstract_text(values: dict[str, str]) -> str:
    """The abstract as plain text, numbers filled in, for the README and so for the Zenodo description."""
    text = (PAPER / "abstract.tex").read_text(encoding="utf-8").strip()
    text = re.sub(r"\\([A-Za-z]+)\{\}", lambda m: values[m.group(1)] if m.group(1) in values else m.group(0), text)
    for pattern, replacement in _TEX:
        text = re.sub(pattern, replacement, text)
    left = re.findall(r"\\[A-Za-z]+|\$|[{}]", text)
    if left:
        raise SystemExit("abstract.tex keeps TeX with no plain-text form: " + " ".join(sorted(set(left))))
    return "\n\n".join(re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text) if part.strip())


def readme(values: dict[str, str]) -> str:
    """README.md with its "## Abstract" section written from abstract.tex."""
    text = README.read_text(encoding="utf-8")
    match = re.search(r"^## Abstract\n\n(.*?)\n\n(?=## )", text, flags=re.S | re.M)
    if not match:
        raise SystemExit("README.md needs an \"## Abstract\" section followed by another section")
    return text[:match.start(1)] + abstract_text(values) + text[match.end(1):]


def main() -> int:
    stale = []
    files = {PAPER / name: text for name, text in render().items()}
    files[README] = readme(macros() | gap_macros())
    for path, text in files.items():
        name = path.name
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        if "--check" in sys.argv:
            stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {name}")
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
