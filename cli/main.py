"""Main CLI entry point for GetLLM."""
import click
from rich.console import Console

# Import command modules
from .commands import models, server

# Create main CLI group
@click.group()
@click.version_option()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
@click.option('--log-file', type=click.Path(dir_okay=False, writable=True), 
              help='Path to log file')
@click.pass_context
def cli(ctx: click.Context, debug: bool, log_file: str) -> None:
    """GetLLM - Command line interface for managing LLM models."""
    # Ensure context.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Store common options in context
    ctx.obj['debug'] = debug
    ctx.obj['log_file'] = log_file
    
    # Set up logging
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Log command execution
    if debug:
        console = Console()
        console.print(f"[debug] Executing command: {ctx.command_path}")


def main() -> None:
    """Entry point for the CLI."""
    # Register command groups
    models.register_commands(cli)
    server.register_commands(cli)
    
    # Run the CLI
    cli(obj={})


if __name__ == "__main__":
    main()
