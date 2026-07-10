import click
from .core.runner import ExperimentRunner


@click.group(help="KMDS Modeling CLI. Requires a workspace config whose featurization data lives under data/featurization/.")
def cli():
    """KMDS Modeling CLI."""
    pass


@cli.command(help="Run model evaluation for configured candidates. The config should reference a workspace with `data/featurization/model_ready_numeric_data.csv`.")
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True),
    help="Path to modeling_config.yaml. This package expects featurization output under data/featurization/ in the workspace.",
)
def evaluate(config):
    """Run model evaluation for configured candidates."""
    runner = ExperimentRunner(config)
    click.echo("Starting candidate model evaluation...")
    df = runner.run_evaluation()
    click.echo("\n--- EXPERIMENT RESULTS LEADERBOARD ---")
    click.echo(df.to_string(index=False))


@cli.command(help="Export the selected champion model using the configured production target. Model inputs are expected from data/featurization/.")
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True),
    help="Path to modeling_config.yaml. This package expects featurization output under data/featurization/ in the workspace.",
)
def export(config):
    """Export the selected champion model using the configured production target."""
    runner = ExperimentRunner(config)
    click.echo("Exporting the champion model artifacts...")
    runner.export_champion()


if __name__ == '__main__':
    cli()
