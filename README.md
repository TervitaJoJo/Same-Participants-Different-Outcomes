# Paired-state estimability audit: reproducible public bundle

This subpackage contains the current analysis outputs and rendering code for the paired-state estimability audit. It is designed to run from a clean download without access to participant-level survey files.

The human-survey CSVs are reviewed aggregate results: survey-wave estimates, CHARLS state counts and estimates, HRS application estimates, CVAI contrasts, and simulation summaries. They contain no participant identifiers and no row-level survey records. They support exact reconstruction of the manuscript figures and headline checks. The original CHARLS, HRS, CVAI and cross-survey analyses require the source releases and access conditions described in the manuscript; those restricted inputs are intentionally absent. The One Health extension adds public bacterial isolate records and a complete reanalysis of its prespecified comparisons.

## Quick start

Reviewer checks added on 15 October 2026 qualify the earlier exploratory
claims and the interpretation of the sparse simulation. Read
`one_health_amr/checks/REPORT_zh.md` first: the crude AMR reversal disappears
on standardized common support; none of the five AMR point reversals passes
serovar-cluster Holm correction over 168 comparisons. The historical 12/400
result characterizes its specified estimation procedure, not universal
nonestimability. Earlier results remain available for comparison.

Python 3.11 or newer is recommended.

From this directory:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

The command writes `outputs/validation.json`, `outputs/run_manifest.json`, the four revised One Health main figures, and seven supplementary figures. To render only the manuscript figures, use `python scripts/reproduce.py --main-only`. The current layout is human reversals (Fig. 1), procedure-specific sparse simulation (Fig. 2), CHARLS allocation (Fig. 3), and the integrated AMR application (Fig. 4). HRS/CVAI is Supplementary Fig. S7.

The public food-chain AMR extension is included under `one_health_amr/`.
To reproduce the revised figures and the primary AMR analyses together, run:

```bash
python scripts/reproduce.py --include-amr
```

To include both exploratory families and all new reviewer checks in one
offline run (after dependency installation):

```bash
python -B scripts/reproduce.py --include-reviewer-checks
```

The above command first renders from saved outputs, recomputes the public AMR and synthetic diagnostic checks, then refreshes the revised displays. Install `one_health_amr/requirements_amr.txt` in addition to the root requirements for the tested AMR environment. To redraw only the revised submission figures from saved analysis outputs, run `python -B scripts/render_submission_revision.py`.

The added simulation includes 200,000 synthetic records and the original
generating-code snapshot. It regenerates the same 400 datasets; it includes
no restricted participant records. Cached official metadata snapshots permit
offline provenance checks. This command does not edit the manuscript.

The extension includes the public bacterial isolate source subset, an analysis
plan written before the full retrieval and source-association calculations,
all prespecified comparisons, failed attempts, verification, a Chinese report,
and a 600-dpi PNG plus vector PDF figure. It runs offline after dependencies
are installed. Its results are written under `one_health_amr/results/` and
`one_health_amr/figures/`. See `one_health_amr/README.md` for source retrieval
and `one_health_amr/AMR_analysis_report_zh.md` for interpretation. The extension
reanalyzes public bacterial records; the original human cohort component
continues to reproduce reviewed aggregate results.

The separately labelled exploratory AMR reversal searches are in
`one_health_amr/exploratory/`. To include it after the primary AMR workflow,
run `python one_health_amr/reproduce_amr.py --include-exploratory`.
The first search includes 54 phenotype/marker comparisons; the additional
threshold search includes 114 R-versus-R-or-I comparisons. All results and
candidate checks are retained, with cumulative multiplicity accounting
over 168 comparisons. The two searches found one marker point reversal
and four threshold point reversals. See the two exploratory Chinese reports
for the distinct uncertainty and interpretation of these findings.

The rendering code uses relative paths and never modifies files under `data/derived`. Each input table is checked for expected row counts, the 8/26 reversal result, the 6/8 supported reversals, CHARLS state totals, the allocation identity, CVAI definition consistency, and the 12/400 sparse-fit denominator result.

## Data boundary

The human-survey component is a derived-data reproduction layer, not a substitute for a raw-data reanalysis. `scripts/export_derived_data.py` is an author-side helper for copying only the ten reviewed aggregate exports from a private workspace. It does not search recursively and does not copy `.dta`, `.sav`, `.pkl`, `.parquet`, compressed raw files or unidentified files.

The source CSVs preserve the values used for figure production. `data/derived/charls_bridge.csv` labels the primary CHARLS contrast as current versus noncurrent smoking; the separate current-versus-never sensitivity results remain identifiable in `charls_estimates.csv`.

## Layout

```text
paired_state_audit/
  data/derived/       aggregate CSVs only
  scripts/            validation, rendering and export entry points
  scripts/templates/  small independent Matplotlib drawing helpers
  docs/               data dictionary and reproducibility limits
  outputs/            generated figures and run reports
```

This directory was added to the existing project `code` folder. It is not a replacement for the historical source collection elsewhere under `code/analysis/statistical_modeling`.
