"""Utility functions for model-related operations in the CLI."""
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from getllm import ModelManager, ModelInfo

console = Console()

def display_models(
    models: List[ModelInfo],
    installed_only: bool = False,
    source: Optional[str] = None,
    limit: Optional[int] = None
) -> None:
    """Display a list of models in a formatted table.
    
    Args:
        models: List of ModelInfo objects to display
        installed_only: If True, only show installed models
        source: Filter models by source (e.g., 'huggingface', 'ollama')
        limit: Maximum number of models to display
    """
    if not models:
        console.print("[yellow]No models found.[/yellow]")
        return
    
    # Apply filters
    if installed_only:
        manager = ModelManager()
        models = [m for m in models if manager.is_model_installed(m.id)]
    
    if source:
        models = [m for m in models if m.source.value.lower() == source.lower()]
    
    if limit is not None:
        models = models[:limit]
    
    # Create and display table
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


def install_model_with_progress(
    model_id: str,
    force: bool = False,
    **kwargs
) -> bool:
    """Install a model with a progress indicator.
    
    Args:
        model_id: ID of the model to install
        force: Whether to force reinstallation if already installed
        **kwargs: Additional arguments to pass to install_model
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    manager = ModelManager()
    
    if not force and manager.is_model_installed(model_id):
        console.print(f"[yellow]Model {model_id} is already installed. Use --force to reinstall.[/yellow]")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]Installing {model_id}...", total=None)
        
        try:
            success = manager.install_model(model_id, force=force, **kwargs)
            if success:
                progress.update(task, description=f"[green]✓ Installed {model_id}[/green]")
                return True
            else:
                progress.update(task, description=f"[red]Failed to install {model_id}[/red]")
                return False
        except Exception as e:
            progress.update(task, description=f"[red]Error installing {model_id}: {str(e)}[/red]")
            return False


def uninstall_model_with_progress(model_id: str) -> bool:
    """Uninstall a model with a progress indicator.
    
    Args:
        model_id: ID of the model to uninstall
        
    Returns:
        bool: True if uninstallation was successful, False otherwise
    """
    manager = ModelManager()
    
    if not manager.is_model_installed(model_id):
        console.print(f"[yellow]Model {model_id} is not installed.[/yellow]")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]Uninstalling {model_id}...", total=None)
        
        try:
            success = manager.uninstall_model(model_id)
            if success:
                progress.update(task, description=f"[green]✓ Uninstalled {model_id}[/green]")
                return True
            else:
                progress.update(task, description=f"[red]Failed to uninstall {model_id}[/red]")
                return False
        except Exception as e:
            progress.update(task, description=f"[red]Error uninstalling {model_id}: {str(e)}[/red]")
            return False


def display_model_info(model_id: str) -> None:
    """Display detailed information about a model.
    
    Args:
        model_id: ID of the model to display information for
    """
    manager = ModelManager()
    
    try:
        model_info = manager.get_model_info(model_id)
        if not model_info:
            console.print(f"[red]Model not found: {model_id}[/red]")
            return
        
        console.print(f"[bold cyan]Model:[/bold cyan] {model_info.id}")
        console.print(f"[bold]Name:[/bold] {model_info.name}")
        console.print(f"[bold]Source:[/bold] {model_info.source.value}")
        console.print(f"[bold]Type:[/bold] {model_info.model_type.value if model_info.model_type else 'N/A'}")
        console.print(f"[bold]Installed:[/bold] {'✓' if manager.is_model_installed(model_id) else '✗'}")
        
        if model_info.description:
            console.print("\n[bold]Description:[/bold]")
            console.print(model_info.description)
            
        if model_info.tags:
            console.print("\n[bold]Tags:[/bold]", ", ".join(f"[yellow]{tag}[/yellow]" for tag in model_info.tags))
            
        if model_info.metadata:
            console.print("\n[bold]Metadata:[/bold]")
            for key, value in model_info.metadata.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")
                
    except Exception as e:
        console.print(f"[red]Error getting model info: {str(e)}[/red]")
        return
