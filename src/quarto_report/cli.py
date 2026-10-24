"""Render in isolation, publish only completed reports, never overwrite files."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import yaml

from .analysis import InputError, analyse


def render(input_path, output, group=None, min_dose=0.0, title="Measurement report", format="html"):
    result = analyse(input_path, group, min_dose)
    output = Path(output).resolve()
    sidecar = output.with_suffix(".json")
    if format not in {"html", "pdf"} or output.suffix != f".{format}":
        raise InputError("Output suffix must match --format (html or pdf).")
    if output.exists() or sidecar.exists():
        raise InputError("Output or JSON sidecar already exists; choose a new output path.")
    quarto = shutil.which("quarto")
    if not quarto:
        raise InputError("Quarto is missing; install the environment with pip install -e '.[dev]'.")
    result["parameters"]["title"] = title
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="measurement-report-") as folder:
        work = Path(folder)
        # A validated snapshot prevents the source changing between validation and render.
        snapshot = work / "input.csv"
        snapshot.write_bytes(Path(input_path).read_bytes())
        if analyse(snapshot, group, min_dose)["input_sha256"] != result["input_sha256"]:
            raise InputError("Input changed during validation; retry with a stable CSV.")
        shutil.copyfile(Path(__file__).parent / "templates/report.qmd", work / "report.qmd")
        params = dict(input_path=str(snapshot), group=group, min_dose=min_dose, report_title=title)
        (work / "params.yml").write_text(yaml.safe_dump(params), encoding="utf-8")
        env = dict(os.environ, QUARTO_PYTHON=sys.executable, MPLBACKEND="Agg")
        engine = "typst" if format == "pdf" else "html"
        command = [quarto, "render", "report.qmd", "--to", engine, "--output", f"report.{format}",
                   "--execute-params", "params.yml", "--no-execute-daemon"]
        completed = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True)
        artifact = work / f"report.{format}"
        if completed.returncode or not artifact.is_file() or not artifact.stat().st_size:
            detail = (completed.stderr or completed.stdout)[-4000:]
            raise InputError(f"Quarto rendering failed; no report published.\n{detail}")
        # Exclusive creation protects existing artifacts, including concurrent writers.
        created = []
        try:
            with output.open("xb") as handle:
                created.append(output)
                handle.write(artifact.read_bytes())
            with sidecar.open("x", encoding="utf-8") as handle:
                created.append(sidecar)
                json.dump(result, handle, indent=2, allow_nan=False)
                handle.write("\n")
        except OSError:
            for path in created:
                path.unlink(missing_ok=True)
            raise
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render a validated measurement CSV with Quarto.")
    parser.add_argument("input", type=Path, help="UTF-8 CSV: group,dose,response")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--group", help="Exact group label; default: all groups")
    parser.add_argument("--min-dose", type=float, default=0.0, help="Inclusive nonnegative dose cutoff")
    parser.add_argument("--title", default="Measurement report")
    parser.add_argument("--format", choices=["html", "pdf"], default="html",
                        help="Output format; PDF uses Quarto's bundled Typst (no LaTeX required)")
    args = parser.parse_args(argv)
    try:
        result = render(args.input, args.output, args.group, args.min_dose, args.title, args.format)
    except (InputError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Created {args.output} and {args.output.with_suffix('.json')}; selected {result['selected_rows']} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
