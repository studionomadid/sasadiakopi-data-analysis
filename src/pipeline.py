from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from src.analysis import get_connection, load_all_data
from src.dashboard import generate_dashboard
from src.insights import generate_insights, save_insights
from src.report import generate_report
from src.validation import (
    run_validation,
    save_validation_report,
)
from src.visualization import generate_all_charts

OUTPUT_DIRECTORY = Path("outputs")


@dataclass(frozen=True)
class PipelineStep:
    """Represent the result of one pipeline step."""

    name: str
    status: str
    duration_seconds: float
    output: str | None = None


def load_datasets() -> dict:
    """Load all Sasadiakopi datasets from the database."""
    connection = get_connection()

    try:
        return load_all_data(connection)
    finally:
        connection.close()


def run_validation_step(
    datasets: dict,
) -> PipelineStep:
    """Run data-quality validation."""
    start = perf_counter()

    validation_results = run_validation(datasets)

    output_path = save_validation_report(
        validation_results
    )

    failed = int(
        (validation_results["status"] == "FAIL").sum()
    )

    duration = perf_counter() - start

    if failed > 0:
        return PipelineStep(
            name="validation",
            status="FAIL",
            duration_seconds=duration,
            output=str(output_path),
        )

    return PipelineStep(
        name="validation",
        status="PASS",
        duration_seconds=duration,
        output=str(output_path),
    )


def run_visualization_step(
    datasets: dict,
) -> PipelineStep:
    """Generate all business visualizations."""
    start = perf_counter()

    generate_all_charts(datasets)

    duration = perf_counter() - start

    return PipelineStep(
        name="visualization",
        status="PASS",
        duration_seconds=duration,
        output="outputs/charts/",
    )


def run_report_step() -> PipelineStep:
    """Generate the business report."""
    start = perf_counter()

    output_path = generate_report()

    duration = perf_counter() - start

    return PipelineStep(
        name="report",
        status="PASS",
        duration_seconds=duration,
        output=str(output_path),
    )


def run_dashboard_step() -> PipelineStep:
    """Generate the business dashboard."""
    start = perf_counter()

    output_path = generate_dashboard()

    duration = perf_counter() - start

    return PipelineStep(
        name="dashboard",
        status="PASS",
        duration_seconds=duration,
        output=str(output_path),
    )


def run_insights_step() -> PipelineStep:
    """Generate business findings and recommendations."""
    start = perf_counter()

    findings, recommendations = generate_insights()

    output_path = save_insights(
        findings,
        recommendations,
    )

    duration = perf_counter() - start

    return PipelineStep(
        name="insights",
        status="PASS",
        duration_seconds=duration,
        output=str(output_path),
    )


def run_pipeline() -> list[PipelineStep]:
    """Run the complete Sasadiakopi analytics pipeline."""
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    steps: list[PipelineStep] = []

    datasets = load_datasets()

    validation_step = run_validation_step(
        datasets
    )
    steps.append(validation_step)

    if validation_step.status == "FAIL":
        return steps

    steps.append(
        run_visualization_step(
            datasets
        )
    )

    steps.append(
        run_report_step()
    )

    steps.append(
        run_dashboard_step()
    )

    steps.append(
        run_insights_step()
    )

    return steps


def main() -> None:
    """Run and summarize the complete analytics pipeline."""
    print("Sasadiakopi analytics pipeline")
    print("==============================")
    print()

    steps = run_pipeline()

    for step in steps:
        duration = f"{step.duration_seconds:.2f}s"

        print(
            f"[{step.status}] "
            f"{step.name:<15} "
            f"{duration:<8} "
            f"{step.output or '-'}"
        )

    print()

    failed_steps = [
        step
        for step in steps
        if step.status == "FAIL"
    ]

    if failed_steps:
        print(
            f"Pipeline failed: "
            f"{len(failed_steps)} step(s) failed."
        )
        raise SystemExit(1)

    print(
        f"Pipeline completed successfully: "
        f"{len(steps)} step(s)."
    )


if __name__ == "__main__":
    main()
