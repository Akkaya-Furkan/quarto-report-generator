# Parameterised measurement reports with Quarto

## Question

Can a validated measurement CSV become a reproducible, parameterised report with one command?

## Approach

An installable Python CLI validates the complete CSV before invoking a Jupyter-backed Quarto template. Select a group, inclusive minimum dose, and title. The report shows per-group, per-dose observation counts, arithmetic means, sample standard deviations, and an error-bar plot. Groups are never pooled. A JSON sidecar records full-precision summaries, effective parameters, and the input SHA-256. Rendering uses an isolated snapshot of the validated CSV, then publishes completed artifacts without overwriting existing files.

The [scope and acceptance criteria](docs/SCOPE.md) define the implementation boundary. The [synthetic data provenance](examples/data/README.md) and [generator](scripts/generate_example.py) explain every input value. There are no experimental measurements or biological claims.

## Run

Python 3.11 is the tested runtime. Install Quarto through pip with the pinned environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install --no-deps -e .
quarto check jupyter
measurement-report examples/data/measurements.csv \
  --group reference --min-dose 2 --title "Selected measurements" \
  --output build/selected.html
```

Alternatively, run `conda env create -f environment.yml` from the repository root and then `conda activate quarto-report-generator`. The environment also installs Quarto through pip. `pip install -e '.[dev]'` provides an unpinned development installation.

Input must be a UTF-8 CSV with exactly this header and column order:

```csv
group,dose,response
```

Group labels must be nonempty. Dose and response must be finite numbers; dose must be nonnegative. Every input row is validated even if a filter would exclude it. Omit `--group` for all groups. `--min-dose` defaults to zero. `--title` changes the report heading. Use a new output path for each run: both the report and its `.json` sidecar must not already exist. Invalid data, empty selections, missing tools, and render failures return exit code 2 with an actionable error. `measurement-report --help` lists the options.

To generate PDF using Quarto's bundled Typst engine (no TinyTeX, XeLaTeX, sudo, or separate Typst installation required):

```bash
measurement-report examples/data/measurements.csv --format pdf \
  --group reference --title "Reference measurements" --output build/measurements.pdf
pdfinfo build/measurements.pdf
```

**PDF done:** `--format pdf` renders the template with `--to typst` and publishes a `.pdf` plus its JSON sidecar. [Quarto includes Typst](https://quarto.org/docs/output-formats/typst.html), so the pinned pip environment is sufficient. Activate `.venv` before running the CLI so `quarto` is on `PATH`. Renderer failures return exit code 2 without publishing a report or sidecar.

## Results

The deterministic example contains 30 synthetic observations. The committed [reference report](examples/reports/reference.html) and [comparison report](examples/reports/comparison.html) each select 15 observations and contain 5 dose summaries. Download an HTML file and open it locally; GitHub's file viewer displays source. Each report has a companion JSON file in the same directory. The committed [reference PDF](examples/reports/reference-pdf.pdf) and [JSON sidecar](examples/reports/reference-pdf.json) select 15 observations across 5 doses. Local `pdfinfo` measured **2 A4 pages and 47,586 bytes**, produced by Typst 0.15.1; both pages were rendered to PNG and visually inspected. PDF bytes can vary with creation metadata and platform fonts.

The real-render parameter test uses minimum dose 2: each selection contains 9 observations, and the first dose mean changes from 14 (reference) to 18 (comparison). The test reads these values from both rendered HTML tables and JSON sidecars, and checks an embedded plot and the input fingerprint. These are descriptive results of a synthetic formula, not an efficacy comparison.

Local validation: **38/38 pytest cases passed** using Python 3.11.15 and pip-installed Quarto 1.10.19. Tests cover known statistics, group separation, deterministic data regeneration, malformed/empty CSV, nonfinite values, invalid cutoffs, empty selections, missing tools, output preservation, and rollback on sidecar write failure. Two actual PDF renders are parsed with pypdf to verify nonempty PDF files, pages, selected means, titles, observation counts, fingerprints, embedded plots, and matching JSON. Missing/empty PDF output and renderer failure must leave no published files. The HTML layout was also inspected in headless Chrome.

```bash
python -m pytest -v
python scripts/generate_example.py
```

[GitHub Actions](.github/workflows/ci.yml) installs the pinned environment, verifies the bundled Typst executable, runs the tests including 2 HTML and 2 PDF renders, and generates 2 HTML reports and 1 PDF report with their 3 JSON sidecars as a downloadable CI artifact. CI logs the PDF page count and byte size using pypdf. PDF tests are required and are not skipped: a missing/broken bundled Typst installation fails CI. CI does not require LaTeX or a system package installation; `pdfinfo` is an optional local inspection tool.

## Limitations

This is descriptive reporting with arbitrary units. It performs no curve fitting, hypothesis testing, confidence interval calculation, or potency estimation. Error bars show sample standard deviation. A singleton has undefined SD and is displayed as NA. Values shown in the report are rounded; JSON retains numerical precision. The CSV fingerprint identifies the input bytes but does not establish experimental provenance. Finite inputs whose statistics overflow are rejected. The environment is pinned for Python 3.11 on Linux; HTML and Typst PDF rendering were validated locally on Linux; other platforms have not been validated. The XeLaTeX/TinyTeX route is not implemented or tested. The report/sidecar pair is rolled back on ordinary write failures but is not a crash-atomic multi-file transaction. Very large input files and interactive dashboards are outside scope.

Quarto integration follows the official [parameter documentation](https://quarto.org/docs/computations/parameters.html), [render CLI documentation](https://quarto.org/docs/cli/render.html), and [pip package installation instructions](https://pypi.org/project/quarto-cli/).
