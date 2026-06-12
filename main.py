import click
from kmds_modeling.core.runner import ExperimentRunner

@click.group()
def cli():
    """KMDS Modeling CLI Framework Utility Engine."""
    pass

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to modeling_config.yaml')
def evaluate(config):
    """Runs cross-validation evaluations on all registered candidates."""
    runner = ExperimentRunner(config)
    click.echo("Starting candidate model evaluation loop...")
    df = runner.run_evaluation()
    click.echo("\n--- EXPERIMENT RESULTS LEADERBOARD ---")
    click.echo(df.to_string(index=False))

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to modeling_config.yaml')
def export(config):
    """Freezes training datasets and builds MLOps deployment assets."""
    runner = ExperimentRunner(config)
    click.echo("Building final production pipeline bundles...")
    runner.export_champion()

if __name__ == '__main__':
    cli()
