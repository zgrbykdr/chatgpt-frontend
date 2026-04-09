from pathlib import Path

import typer

from fmu_reverse_engineering.core.config import load_config
from fmu_reverse_engineering.core.enums import WorkflowMode
from fmu_reverse_engineering.core.logging_utils import configure_logging
from fmu_reverse_engineering.workflows.automatic_workflow import AutomaticWorkflow
from fmu_reverse_engineering.workflows.manual_workflow import ManualWorkflow
from fmu_reverse_engineering.workflows.semi_automatic_workflow import SemiAutomaticWorkflow

app = typer.Typer(help="FMU reverse engineering CLI")


@app.command()
def run(
    fmu: str = typer.Option(..., help="Path to FMU file"),
    mode: WorkflowMode = typer.Option(WorkflowMode.AUTOMATIC),
    config: str = typer.Option("configs/default.yaml"),
    output_dir: str = typer.Option("artifacts/reports/latest_run"),
    log_level: str = typer.Option("INFO"),
) -> None:
    configure_logging(log_level)
    cfg = load_config(config)
    cfg.workflow.mode = mode

    if mode == WorkflowMode.AUTOMATIC:
        result = AutomaticWorkflow(cfg).execute(fmu, output_dir)
    elif mode == WorkflowMode.SEMI_AUTOMATIC:
        result = SemiAutomaticWorkflow(cfg).execute(fmu, output_dir)
    else:
        result = ManualWorkflow(cfg).execute(fmu, output_dir)

    typer.echo(f"Run completed. Summary keys: {list(result.keys())}")


if __name__ == "__main__":
    app()
