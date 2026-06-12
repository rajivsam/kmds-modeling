import click
from .core.runner import ExperimentRunner


@click.group()
def cli():
    """KMDS Modeling CLI."""
    pass


@cli.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to modeling_config.yaml")
def evaluate(config):
    """Run model evaluation for configured candidates."""
    runner = ExperimentRunner(config)
    click.echo("Starting candidate model evaluation...")
    df = runner.run_evaluation()
    click.echo("\n--- EXPERIMENT RESULTS LEADERBOARD ---")
    click.echo(df.to_string(index=False))


@cli.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to modeling_config.yaml")
def export(config):
    """Export the selected champion model using the configured production target."""
    runner = ExperimentRunner(config)
    click.echo("Exporting the champion model artifacts...")
    runner.export_champion()


if __name__ == '__main__':
    cli()
