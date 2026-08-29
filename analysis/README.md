# Reproducing the empirical analysis

These scripts read the harmonized 888-paper SciLitBench release and regenerate
the empirical figure data, tables and figures used in the PRISMA-LLM
manuscript.

## Input

Download or clone [SciLitBench](https://github.com/linlab/SciLitBench). The
scripts require this file:

```text
SciLitBench/benchmark/de_harmonized.json
```

Keep the SciLitBench dataset in its own checkout. The local
`data/publication_dates.csv` file contains the paper ID, publication year and
publication month used for the temporal analyses.
`data/publication_date_overrides.csv` records the 33 dates that required manual
adjudication, including the source evidence and decision basis.

## Run

Python 3.11 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r analysis/requirements.txt
python analysis/analysis.py --scilitbench /path/to/SciLitBench
```

The command writes:

```text
analysis/outputs/
├── derived/
│   ├── paper_level_analysis.csv
│   └── reported_metrics.csv
├── figure_data/
├── figures/
└── table_data/
```

Use `--output-dir` to write elsewhere. Files with the same names are
overwritten.

## Analysis conventions

- Time-based analyses use `publication_year` and `publication_month` from
  `data/publication_dates.csv`. The annotation `year` field is ignored.
- Approach and review-stage analyses are multi-label. Analyses labeled
  `orientation` or `complexity` use mutually exclusive groups.
- Reporting richness is a descriptive 0--15 index. Each of five dimensions is
  scored 0 for no items, 1 for one item, 2 for two or three items and 3 for
  four or more items.
- Time-series results are calculated over overlapping 3-month windows.
- Precision and recall summarize values reported by studies that used different
  datasets, thresholds and validation designs.

The executable group definitions are in `definitions.py`. `analysis.py`
prepares the data and produces the numerical summaries. `figures.py` renders
the figures.
