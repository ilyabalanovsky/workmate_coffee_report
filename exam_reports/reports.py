from collections import defaultdict
from statistics import median


class UnknownReportError(ValueError):
    def __init__(self, report_name):
        self.report_name = report_name
        super().__init__(f"Unknown report: {report_name}")


def build_median_coffee_report(rows):
    coffee_by_student = defaultdict(list)

    for row in rows:
        student_name = row["student"]
        coffee_by_student[student_name].append(float(row["coffee_spent"]))

    report_rows = [
        {
            "student": student_name,
            "median_coffee": median(coffee_values),
        }
        for student_name, coffee_values in coffee_by_student.items()
    ]

    report_rows.sort(key=lambda item: (-item["median_coffee"], item["student"]))
    return report_rows


REPORT_BUILDERS = {
    "median-coffee": build_median_coffee_report,
}
