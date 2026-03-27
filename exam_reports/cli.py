import argparse
import csv
from pathlib import Path

from .reports import REPORT_BUILDERS, UnknownReportError

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover
    tabulate = None


def build_parser():
    parser = argparse.ArgumentParser(description="Build reports from student exam preparation CSV files.")
    parser.add_argument("--files", nargs="+", required=True, help="Paths to CSV files with student data.")
    parser.add_argument("--report", required=True, help="Report name to build, for example: median-coffee.")
    return parser


def load_rows(file_paths):
    rows = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            rows.extend(reader)

    return rows


def format_table(report_rows):
    if tabulate is not None:
        return tabulate(report_rows, headers="keys", tablefmt="github")

    if not report_rows:
        return ""

    headers = list(report_rows[0].keys())
    string_rows = [[str(row[header]) for header in headers] for row in report_rows]
    widths = []

    for index, header in enumerate(headers):
        values = [header] + [row[index] for row in string_rows]
        widths.append(max(len(value) for value in values))

    def build_line(values):
        cells = [value.ljust(widths[index]) for index, value in enumerate(values)]
        return " | ".join(cells)

    lines = [build_line(headers), build_line(["-" * width for width in widths])]
    lines.extend(build_line(row) for row in string_rows)
    return "\n".join(lines)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        builder = REPORT_BUILDERS[args.report]
    except KeyError as error:
        message = str(UnknownReportError(args.report))
        parser.exit(status=2, message=f"{message}\n")
        raise AssertionError("parser.exit should stop execution") from error

    try:
        rows = load_rows(args.files)
    except FileNotFoundError as error:
        parser.exit(status=2, message=f"{error}\n")

    report_rows = builder(rows)
    print(format_table(report_rows))
    return 0
