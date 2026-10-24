# Validation evidence

Validated locally on 2026-10-24 with Python 3.11.15 and pip-installed Quarto 1.10.19.

- pytest: 34/34 cases passed, including two actual parameterised HTML renders (9.70 seconds).
- `quarto check jupyter`: passed Python discovery and Jupyter engine render.
- `pip check`: no broken requirements.
- Example artifacts: 4/4 files present (2 HTML + 2 JSON), 4 unique SHA-256 values.
- Committed example tables: 10/10 summary rows checked against executed analysis and JSON.
- Parameter render test: 9 selected observations per group at minimum dose 2; first dose means 14 versus 18 verified in HTML and JSON.
- Invalid CSV, render failure, and sidecar write failure: tests confirm no report or sidecar remains. Existing outputs are preserved.
- HTML layout inspected using headless Chrome. Embedded plot and absence of unproduced PDF links also verified automatically.
- **PDF not done**: real CLI request exited with code 2 because XeLaTeX is unavailable; 0/2 requested PDF/JSON artifacts exist.
- `git diff --check`: passed before commit. Remote commit and CI outcome are checked after push and reported separately.

## Committed example fingerprints

- `comparison.html`: `a20a2db8ba894a134db4c394ac3f3fcd914bd0172704e035e694c56af94f8fe7`
- `comparison.json`: `e41a94bb67d11f2a71d1fb0b3acb3fdb96e273e644365c72d519a027594876a6`
- `reference.html`: `5b17f2c235e459529cc23ee425752bb9a80053cf5f147e70d57c330200aed1ab`
- `reference.json`: `0b1989ff1caeb1570fb5d00865d145fb4f70387e4d84debb3fa222651037accb`
