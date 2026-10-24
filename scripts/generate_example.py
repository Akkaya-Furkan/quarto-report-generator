"""Deterministic illustrative measurements, with no experimental provenance."""
import csv
from pathlib import Path


def generate(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['group', 'dose', 'response'])
        for group, baseline, slope in [('reference', 10, 2), ('comparison', 12, 3)]:
            for dose in [0, 1, 2, 4, 8]:
                for offset in [-1, 0, 1]:
                    writer.writerow([group, dose, baseline + slope * dose + offset])


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1] / 'examples/data/measurements.csv')
