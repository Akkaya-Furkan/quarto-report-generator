# One-day scope — 2026-10-24

## Question
Can a user turn a validated measurement CSV into a reproducible, parameterised analysis report with one CLI command?

## Implementation boundary
Build an installable Python CLI using a Jupyter-backed Quarto template. Input columns are `group`, `dose`, and `response`; dose and response are finite numeric values, dose is nonnegative, and group is nonempty. Parameters select a group, an inclusive minimum dose, and a report title. Summarise selected observations by dose (count, mean, sample standard deviation) and plot the means with standard deviation error bars. Include input SHA-256 and the effective parameters in the report and JSON sidecar. Use a deterministic synthetic measurement table with explicitly documented provenance. No biological claims, model fitting, external datasets, thesis ligands, or homelab content.

## Acceptance criteria
1. An installed CLI accepts CSV input, parameters, output path, and HTML/PDF format. HTML is self-contained; PDF uses Quarto's bundled Typst engine without LaTeX. Both formats must be exercised by actual renders; PDF must be nonempty and parseable.
2. Commit a deterministic synthetic CSV, its generator, and two rendered HTML reports using different group selections, plus a reference PDF and its JSON sidecar; all analytical numbers originate in executed Python code.
3. An end-to-end pytest test renders both parameter choices and checks different selected means in the HTML and JSON sidecars. Two further end-to-end cases render PDF for both groups and parse pages, text, provenance, selected means, and embedded plots with pypdf.
4. Empty, malformed, nonfinite, invalid-schema, and empty-selection inputs produce actionable CLI errors without report artifacts. Rendering failure does not overwrite existing output.
5. Unit and CLI tests pass; an environment file and GitHub Actions workflow install Quarto through pip, run tests, and retain rendered example artifacts.
6. English README documents question, approach, observed results, usage, and limitations. Commit and push to main, verify the remote commit with `git ls-remote`, and inspect the CI run result.

## Explicit limits
This is descriptive measurement reporting, not dose-response inference. Standard deviation is undefined for singleton doses and displayed as NA. No LaTeX installation is required for HTML or PDF. Typst PDF rendering is verified; XeLaTeX/TinyTeX rendering is outside the implemented path. Outputs are local artifacts; deployment and external messaging are excluded.

## Verified PDF continuation — 2026-10-24

- CLI `--format pdf` maps to Quarto `--to typst`; `.pdf` suffix validation and exclusive publication of the report/JSON pair remain in effect.
- `examples/reports/reference-pdf.pdf` and `reference-pdf.json`: **2/2 artifacts** verified, 15 selected observations, 5 dose summaries. `pdfinfo`: **2 A4 pages, 47,586 bytes**, Typst 0.15.1 with Quarto 1.10.19. Both pages visually inspected after PNG rendering.
- Local pytest: **38/38 passed**, including 2 real PDF renders and 2 real HTML renders. Failed renderers and missing/empty PDF artifacts publish neither PDF nor JSON.
- CI uses pinned pip-installed Quarto and its bundled Typst, runs PDF tests without skips, renders a PDF artifact, and logs its page count and size. A missing Typst engine fails CI rather than masking the missing deliverable.
- Remaining limits: Linux validation only; PDF bytes may vary with metadata/fonts; publication of the report/JSON pair is not crash-atomic.
