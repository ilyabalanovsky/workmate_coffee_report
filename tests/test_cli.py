import pytest

from exam_reports.cli import format_table, main
from exam_reports.reports import build_median_coffee_report


CSV_ONE = """student,date,coffee_spent,sleep_hours,study_hours,mood,exam
Алексей Смирнов,2024-06-01,450,4.5,12,норм,Математика
Алексей Смирнов,2024-06-02,500,4.0,14,устал,Математика
Дарья Петрова,2024-06-01,200,7.0,6,отл,Математика
Дарья Петрова,2024-06-02,250,6.5,8,норм,Математика
"""


CSV_TWO = """student,date,coffee_spent,sleep_hours,study_hours,mood,exam
Алексей Смирнов,2024-06-03,550,3.5,16,зомби,Математика
Дарья Петрова,2024-06-03,300,6.0,9,норм,Математика
Иван Кузнецов,2024-06-01,600,3.0,15,зомби,Математика
Иван Кузнецов,2024-06-02,650,2.5,17,зомби,Математика
Иван Кузнецов,2024-06-03,700,2.0,18,не выжил,Математика
"""


def test_build_median_coffee_report_sorts_descending():
    rows = [
        {"student": "Мария", "coffee_spent": "100"},
        {"student": "Мария", "coffee_spent": "300"},
        {"student": "Иван", "coffee_spent": "400"},
        {"student": "Иван", "coffee_spent": "600"},
        {"student": "Ольга", "coffee_spent": "200"},
    ]

    report = build_median_coffee_report(rows)

    assert report == [
        {"student": "Иван", "median_coffee": 500.0},
        {"student": "Мария", "median_coffee": 200.0},
        {"student": "Ольга", "median_coffee": 200.0},
    ]


def test_main_builds_single_report_from_multiple_files(tmp_path, capsys):
    file_one = tmp_path / "part1.csv"
    file_two = tmp_path / "part2.csv"
    file_one.write_text(CSV_ONE, encoding="utf-8")
    file_two.write_text(CSV_TWO, encoding="utf-8")

    exit_code = main(
        [
            "--files",
            str(file_one),
            str(file_two),
            "--report",
            "median-coffee",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Иван Кузнецов" in captured.out
    assert "650" in captured.out
    assert captured.out.index("Иван Кузнецов") < captured.out.index("Алексей Смирнов")


def test_format_table_contains_expected_headers():
    table = format_table([{"student": "Дарья Петрова", "median_coffee": 250.0}])

    assert "student" in table
    assert "median_coffee" in table


def test_main_fails_for_unknown_report(tmp_path):
    file_one = tmp_path / "part1.csv"
    file_one.write_text(CSV_ONE, encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        main(
            [
                "--files",
                str(file_one),
                "--report",
                "unknown-report",
            ]
        )

    assert error.value.code == 2


def test_main_fails_for_missing_file():
    with pytest.raises(SystemExit) as error:
        main(
            [
                "--files",
                "missing.csv",
                "--report",
                "median-coffee",
            ]
        )

    assert error.value.code == 2
