"""Model-related CLI commands."""
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table

from ..commands.base import BaseCommand
from getllm import ModelManager

class ListModelsCommand(BaseCommand):
    """Command to list available models."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'list',
            'help': 'List available models',
            'options': [
                {
                    'param_decls': ['--source'],
                    'kwargs': {
                        'type': click.Choice(['all', 'huggingface', 'ollama'], case_sensitive=False),
                        'default': 'all',
                        'help': 'Filter models by source'
                    }
                },
                {
                    'param_decls': ['--installed'],
                    'kwargs': {
                        'is_flag': True,
                        'help': 'Show only installed models'
                    }
                },
                {
                    'param_decls': ['--limit'],
                    'kwargs': {
                        'type': int,
                        'default': None,
                        'help': 'Limit the number of results'
                    }
                }
            ]
        }
    
    def execute(self, source: str, installed: bool, limit: Optional[int], **kwargs) -> None:
        """Execute the list models command."""
        manager = ModelManager()
        models = manager.list_models()
        
        # Filter by source
        if source != 'all':
            models = [m for m in models if m.source.value.lower() == source.lower()]
        
        # Filter installed models if requested
        if installed:
            models = [m for m in models if manager.is_model_installed(m.id)]
        
        # Apply limit
        if limit is not None:
            models = models[:limit]
        
        # Display results
        console = Console()
        
        if not models:
            console.print("[yellow]No models found.[/yellow]")
            return
        
        table = Table(title="Available Models")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Source", style="magenta")
        table.add_column("Type", style="yellow")
        table.add_column("Installed", style="green")
        
        for model in models:
            table.add_row(
                model.id,
                model.name,
                model.source.value,
                model.model_type.value if model.model_type else "N/A",
                "✓" if manager.is_model_installed(model.id) else "✗"
            )
        
        console.print(table)


class InstallModelCommand(BaseCommand):
    """Command to install a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'install',
            'help': 'Install a model',
            'options': [
                {
                    'param_decls': ['model_id'],
                    'kwargs': {
                        'type': str,
                        'help': 'ID of the model to install (e.g., huggingface/gpt2, ollama/llama2)'
                    }
                },
                {
                    'param_decls': ['--force'],
                    'kwargs': {
                        'is_flag': True,
                        'help': 'Force reinstall if already installed'
                    }
                }
            ]
        }
    
    def execute(self, model_id: str, force: bool, **kwargs) -> None:
        """Execute the install model command."""
        manager = ModelManager()
        console = Console()
        
        try:
            with console.status(f"[green]Installing model {model_id}..."):
                success = manager.install_model(model_id, force=force)
                
            if success:
                console.print(f"[green]✓ Successfully installed {model_id}[/green]")
            else:
                console.print(f"[yellow]Model {model_id} is already installed. Use --force to reinstall.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error installing model: {str(e)}[/red]")


class UninstallModelCommand(BaseCommand):
    """Command to uninstall a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'uninstall',
            'help': 'Uninstall a model',
            'options': [
                {
                    'param_decls': ['model_id'],
                    'kwargs': {
                        'type': str,
                        'help': 'ID of the model to uninstall'
                    }
                }
            ]
        }
    
    def execute(self, model_id: str, **kwargs) -> None:
        """Execute the uninstall model command."""
        manager = ModelManager()
        console = Console()
        
        if not manager.is_model_installed(model_id):
            console.print(f"[yellow]Model {model_id} is not installed.[/yellow]")
            return
        
        try:
            with console.status(f"[green]Uninstalling model {model_id}..."):
                success = manager.uninstall_model(model_id)
                
            if success:
                console.print(f"[green]✓ Successfully uninstalled {model_id}[/green]")
            else:
                console.print(f"[red]Failed to uninstall {model_id}[/red]")
        except Exception as e:
            console.print(f"[red]Error uninstalling model: {str(e)}[/red]")


def register_commands(cli_group: click.Group) -> None:
    """Register model-related commands with the CLI group."""
    commands = [
        ListModelsCommand,
        InstallModelCommand,
        UninstallModelCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        cli_group.add_command(cmd)
