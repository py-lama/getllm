"""Model-related CLI commands."""
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from ..commands.base import BaseCommand
from ..utils import (
    display_models,
    install_model_with_progress,
    uninstall_model_with_progress,
    display_model_info
)
from getllm import ModelManager, list_models

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
    
    def execute(
        self, 
        source: str, 
        installed: bool, 
        limit: Optional[int],
        **kwargs
    ) -> None:
        """Execute the list models command."""
        models = list_models()
        
        # Filter by source if not 'all'
        if source != 'all':
            models = [m for m in models if m.source.value.lower() == source.lower()]
        
        # Display the filtered models
        display_models(
            models=models,
            installed_only=installed,
            limit=limit
        )


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
        success = install_model_with_progress(model_id, force=force)
        
        if success:
            console = Console()
            console.print(f"[green]✓ Successfully installed {model_id}[/green]")


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
        success = uninstall_model_with_progress(model_id)
        
        if success:
            console = Console()
            console.print(f"[green]✓ Successfully uninstalled {model_id}[/green]")


class InfoModelCommand(BaseCommand):
    """Command to show detailed information about a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'info',
            'help': 'Show detailed information about a model',
            'options': [
                {
                    'param_decls': ['model_id'],
                    'kwargs': {
                        'type': str,
                        'help': 'ID of the model to show information for'
                    }
                }
            ]
        }
    
    def execute(self, model_id: str, **kwargs) -> None:
        """Execute the model info command."""
        display_model_info(model_id)


def register_commands(cli_group: click.Group) -> None:
    """Register model-related commands with the CLI group."""
    # Create a model command group
    model_group = click.Group('model', help='Manage models')
    
    # Register all model commands
    commands = [
        ListModelsCommand,
        InstallModelCommand,
        UninstallModelCommand,
        InfoModelCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        model_group.add_command(cmd)
    
    # Add the model group to the main CLI
    cli_group.add_command(model_group)
