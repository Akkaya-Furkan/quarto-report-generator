# One-day scope — 2026-10-24

## Question
Can a user turn a validated measurement CSV into a reproducible, parameterised analysis report with one CLI command?

## Implementation boundary
Build an installable Python CLI using a Jupyter-backed Quarto template. Input columns are `group`, `dose`, and `response`; dose and response are finite numeric values, dose is nonnegative, and group is nonempty. Parameters select a group, an inclusive minimum dose, and a report title. Summarise selected observations by dose (count, mean, sample standard deviation) and plot the means with standard deviation error bars. Include input SHA-256 and the effective parameters in the report and JSON sidecar. Use a deterministic synthetic measurement table with explicitly documented provenance. No biological claims, model fitting, external datasets, thesis ligands, or homelab content.

## Acceptance criteria
1. An installed CLI accepts CSV input, parameters, output path, and HTML/PDF format. HTML is self-contained; PDF uses LaTeX only when available. If unavailable, explicitly record **PDF not done** and demonstrate HTML.
2. Commit a deterministic synthetic CSV, its generator, and two rendered HTML reports using different group selections; all analytical numbers originate in executed Python code.
3. An end-to-end pytest test renders both parameter choices and checks different selected means in the HTML and JSON sidecars.
4. Empty, malformed, nonfinite, invalid-schema, and empty-selection inputs produce actionable CLI errors without report artifacts. Rendering failure does not overwrite existing output.
5. Unit and CLI tests pass; an environment file and GitHub Actions workflow install Quarto through pip, run tests, and retain rendered example artifacts.
6. English README documents question, approach, observed results, usage, and limitations. Commit and push to main, verify the remote commit with `git ls-remote`, and inspect the CI run result.

## Explicit limits
This is descriptive measurement reporting, not dose-response inference. Standard deviation is undefined for singleton doses and displayed as NA. No LaTeX installation is required for the one-day HTML deliverable. PDF rendering is optional and must not be claimed without a verified PDF. Outputs are local artifacts; deployment and external messaging are excluded.
