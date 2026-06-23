"""CLI entry point."""
import click
@click.group()
def main():
    """AI-Crypto Nexus CLI."""
    pass
@main.command()
@click.option("--strategy", default="momentum", help="Trading strategy")
@click.option("--chain", default="ethereum", help="Target chain")
def analyze(strategy: str, chain: str):
    """Run market analysis."""
    click.echo(f"Running {strategy} analysis on {chain}...")
@main.command()
def agents():
    """List active agents."""
    click.echo("No agents running.")
if __name__ == "__main__":
    main()
