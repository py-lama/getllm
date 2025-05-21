#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyllm: A package for managing LLM models with Ollama integration.

This package provides functionality for managing, installing, and configuring
LLM models for use with the Ollama API.
"""

# Import from the pyllm subpackage
from pyllm.pyllm.models import (
    get_models, 
    get_default_model, 
    set_default_model, 
    install_model,
    list_installed_models,
    update_models_from_ollama
)

__all__ = [
    'get_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'update_models_from_ollama'
]
