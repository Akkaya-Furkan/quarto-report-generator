"""Strict CSV validation and descriptive statistics, shared by CLI and template."""
import csv
import hashlib
import io
import math
import statistics
from pathlib import Path


class InputError(ValueError):
    """An actionable input or selection error."""


def analyse(path, group=None, min_dose=0.0):
    if not math.isfinite(min_dose) or min_dose < 0:
        raise InputError("Minimum dose must be finite and nonnegative.")
    try:
        raw = Path(path).read_bytes()
        source = raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise InputError(f"Cannot read UTF-8 CSV: {exc}") from exc
    if not source.strip():
        raise InputError("CSV is empty; expected group,dose,response and data rows.")
    rows = []
    try:
        reader = csv.DictReader(io.StringIO(source), strict=True)
        if reader.fieldnames != ["group", "dose", "response"]:
            raise InputError("CSV header must be exactly: group,dose,response")
        for row in reader:
            line = reader.line_num
            if None in row or any(value is None for value in row.values()):
                raise InputError(f"Row {line}: expected exactly three fields.")
            label = row["group"].strip()
            if not label:
                raise InputError(f"Row {line}: group must be nonempty.")
            try:
                dose, response = float(row["dose"]), float(row["response"])
            except ValueError as exc:
                raise InputError(f"Row {line}: dose and response must be numeric.") from exc
            if not all(map(math.isfinite, (dose, response))) or dose < 0:
                raise InputError(f"Row {line}: values must be finite and dose nonnegative.")
            rows.append((label, dose, response))
    except csv.Error as exc:
        raise InputError(f"Malformed CSV: {exc}") from exc
    if not rows:
        raise InputError("CSV has no data rows.")
    selected = [r for r in rows if (group is None or r[0] == group) and r[1] >= min_dose]
    if not selected:
        raise InputError("No observations match the group and minimum dose parameters.")
    summary = []
    for label, dose in sorted({(r[0], r[1]) for r in selected}):
        values = [r[2] for r in selected if r[0] == label and r[1] == dose]
        try:
            mean = statistics.mean(values)
            sd = statistics.stdev(values) if len(values) > 1 else None
            if not math.isfinite(mean) or (sd is not None and not math.isfinite(sd)):
                raise OverflowError
        except (OverflowError, ValueError) as exc:
            raise InputError("Response magnitudes exceed the supported statistical range.") from exc
        summary.append(dict(group=label, dose=dose, count=len(values), mean=mean, sd=sd))
    return dict(input_sha256=hashlib.sha256(raw).hexdigest(), input_rows=len(rows),
                selected_rows=len(selected), parameters=dict(group=group, min_dose=min_dose),
                summary=summary)
