#!/usr/bin/env python3

# Direct wrapper script for getllm with support for the same interface as devlama
import sys
import os
import argparse
import platform
from getllm.ollama_integration import get_ollama_integration, OllamaIntegration
from getllm import models

# Template functions for code generation
def get_template(prompt, template_type, **kwargs):
    """Get a template for code generation based on the template type."""
    templates = {
        "basic": """Generate Python code for the following task: {prompt}""",
        
        "platform_aware": """Generate Python code for the following task: {prompt}

The code should run on {platform} operating system.
{dependencies}""",
        
        "dependency_aware": """Generate Python code for the following task: {prompt}

Use only the following dependencies: {dependencies}""",
        
        "testable": """Generate Python code for the following task: {prompt}

Include unit tests for the code.
{dependencies}""",
        
        "secure": """Generate secure Python code for the following task: {prompt}

Ensure the code follows security best practices and handles errors properly.
{dependencies}""",
        
        "performance": """Generate high-performance Python code for the following task: {prompt}

Optimize the code for performance.
{dependencies}""",
        
        "pep8": """Generate Python code for the following task: {prompt}

Ensure the code follows PEP 8 style guidelines.
{dependencies}""",
        
        "debug": """Debug the following Python code that has an error:

```python
{code}
```

Error message:
{error_message}

Fix the code to solve the problem and provide the corrected version."""
    }
    
    # Get the template or use basic if not found
    template = templates.get(template_type, templates["basic"])
    
    # Format dependencies if provided
    if "dependencies" in kwargs:
        if kwargs["dependencies"]:
            kwargs["dependencies"] = f"Use the following dependencies: {kwargs['dependencies']}"
        else:
            kwargs["dependencies"] = "Use standard Python libraries."
    else:
        kwargs["dependencies"] = "Use standard Python libraries."
    
    # Format the template with the provided arguments
    return template.format(prompt=prompt, **kwargs)

# Mock implementation for testing without Ollama
class MockOllamaIntegration:
    """Mock implementation of OllamaIntegration for testing."""
    def __init__(self, model=None):
        self.model = model or "mock-model"
    
    def query_ollama(self, prompt, template_type=None, **template_args):
        """Mock implementation of query_ollama."""
        if "hello world" in prompt.lower():
            return "print('Hello, World!')"
        elif "binary search tree" in prompt.lower():
            return """
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)
    
    def search(self, value):
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        if node is None or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

# Example usage
bst = BinarySearchTree()
bst.insert(5)
bst.insert(3)
bst.insert(7)
bst.insert(2)
bst.insert(4)

print("Searching for 4:", bst.search(4).value if bst.search(4) else "Not found")
print("Searching for 6:", bst.search(6).value if bst.search(6) else "Not found")
"""
        else:
            return f"# Mock code for: {prompt}\nprint('This is mock code generated for testing')\n"
    
    def extract_python_code(self, text):
        """Mock implementation of extract_python_code."""
        return text

def extract_python_code(text):
    """Extract Python code from the response."""
    # If the response already looks like code (no markdown), return it
    if text.strip().startswith("import ") or text.strip().startswith("#") or text.strip().startswith("def ") or text.strip().startswith("class ") or text.strip().startswith("print"):
        return text
        
    # Look for Python code blocks in markdown
    import re
    code_block_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    matches = re.findall(code_block_pattern, text)
    
    if matches:
        # Return the first code block found
        return matches[0].strip()
    
    # If no code blocks found but the text contains "print hello world" or similar
    if "print hello world" in text.lower() or "print(\"hello world\")" in text.lower() or "print('hello world')" in text.lower():
        return "print(\"Hello, World!\")"
    
    # If all else fails, return the original text with a warning
    return """# Could not extract Python code from the model response
# Here's a simple implementation:

print("Hello, World!")

# Original response:
# """ + text

def check_ollama():
    """Check if Ollama is installed and running, and return its version."""
    # First check if Ollama is installed
    try:
        import subprocess
        import os
        
        # Use the appropriate command based on the OS
        if os.name == 'nt':  # Windows
            which_cmd = 'where'
        else:  # Unix/Linux/MacOS
            which_cmd = 'which'
            
        result = subprocess.run(
            [which_cmd, 'ollama'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print("Ollama is not installed. Please install Ollama from https://ollama.com")
            print("Installation instructions:")
            print("  - Linux/macOS: curl -fsSL https://ollama.com/install.sh | sh")
            print("  - Windows: Visit https://ollama.com/download")
            return None
    except Exception as e:
        print(f"Error checking if Ollama is installed: {e}")
        return None
    
    # Then check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            return response.json().get("version")
    except Exception:
        pass
    return None

def save_code_to_file(code, filename=None):
    """Save the generated code to a file."""
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        package_dir = os.path.join(os.path.expanduser('~'), '.getllm')
        os.makedirs(package_dir, exist_ok=True)
        filename = os.path.join(package_dir, f"generated_script_{timestamp}.py")
    
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    
    return os.path.abspath(filename)

def execute_code(code):
    """Execute the generated code and return the result."""
    # Create a temporary file to store the code
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(code.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Run the code in a separate process
        import subprocess
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Return the result
        if result.returncode == 0:
            return {
                "output": result.stdout,
                "error": None
            }
        else:
            return {
                "output": result.stdout,
                "error": result.stderr
            }
    except Exception as e:
        return {
            "output": "",
            "error": str(e)
        }
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    """Main entry point for the getllm CLI."""
    parser = argparse.ArgumentParser(description="getllm CLI - LLM Model Management and Code Generation")
    
    # Global options
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no Ollama required)")
    parser.add_argument("-m", "--model", help="Name of the Ollama model to use")
    parser.add_argument("-t", "--template", 
                        choices=["basic", "platform_aware", "dependency_aware", "testable", "secure", "performance", "pep8"],
                        default="platform_aware",
                        help="Type of template to use")
    parser.add_argument("-d", "--dependencies", help="List of allowed dependencies (only for template=dependency_aware)")
    parser.add_argument("-s", "--save", action="store_true", help="Save the generated code to a file")
    parser.add_argument("-r", "--run", action="store_true", help="Run the generated code after creation")
    parser.add_argument("--search", metavar="QUERY", help="Search for models on Hugging Face matching the query")
    parser.add_argument("--update-hf", action="store_true", help="Update models list from Hugging Face")
    
    # Add a positional argument for the prompt
    parser.add_argument("prompt", nargs="*", help="Task to be performed by Python code (optional)")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Handle Hugging Face model search
    if args.search or args.update_hf:
        from getllm.models import update_models_from_huggingface, interactive_model_search
        
        if args.search:
            # Search for models on Hugging Face
            print(f"Searching for models matching '{args.search}' on Hugging Face...")
            
            # If in mock mode, skip Ollama checks entirely
            if args.mock:
                print("\nRunning in mock mode - Ollama checks bypassed")
                selected_model = interactive_model_search(args.search, check_ollama=False)
            else:
                selected_model = interactive_model_search(args.search, check_ollama=True)
            if selected_model:
                # Ask if the user wants to install the model
                import questionary
                install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                if install_now:
                    # Check if we're in mock mode
                    if args.mock:
                        print("\nUsing mock mode. Model installation is simulated.")
                        print(f"Model '{selected_model}' would be installed in normal mode.")
                        return 0
                    
                    # Try to install the model
                    from getllm.models import install_model
                    success = install_model(selected_model)
                    
                    # If installation failed, suggest mock mode
                    if not success:
                        print("\nIf you want to continue without Ollama, use the --mock flag:")
                        print("  getllm --mock --search <query>")
                        return 1
        else:  # args.update_hf
            # Update models from Hugging Face
            print("Updating models from Hugging Face...")
            update_models_from_huggingface()
        
        return 0
    
    # Handle interactive mode
    if args.interactive:
        from getllm.interactive_cli import interactive_shell
        interactive_shell(mock_mode=args.mock)
        return 0
    
    # Handle direct prompt if provided
    if args.prompt:
        prompt = " ".join(args.prompt)
        
        # Get model and template
        model = args.model
        template = args.template or "platform_aware"
        dependencies = args.dependencies
        save = args.save
        run = args.run
        mock_mode = args.mock
        
        # Check if Ollama is running (unless in mock mode)
        if not mock_mode:
            ollama_version = check_ollama()
            if not ollama_version:
                print("Ollama is not running. Please start Ollama with 'ollama serve' and try again.")
                print("Alternatively, use --mock for testing without Ollama.")
                return 1
        
        # Create OllamaIntegration or MockOllamaIntegration
        if mock_mode:
            print("Using mock mode (no Ollama required)")
            runner = MockOllamaIntegration(model=model)
        else:
            runner = get_ollama_integration(model=model)
        
        # Prepare template arguments
        template_args = {}
        if dependencies:
            template_args["dependencies"] = dependencies
        
        # Add platform information for platform_aware template
        if template == "platform_aware":
            template_args["platform"] = platform.system()
        
        # Generate code
        print(f"\nGenerating code with model: {runner.model}")
        print(f"Using template: {template}")
        
        # Format the prompt with the template
        formatted_prompt = get_template(prompt, template, **template_args)
        
        # Query the model
        code = runner.query_ollama(formatted_prompt)
        
        # Extract Python code if needed
        if hasattr(runner, "extract_python_code") and callable(getattr(runner, "extract_python_code")):
            code = runner.extract_python_code(code)
        else:
            code = extract_python_code(code)
        
        # Display the generated code
        print("\nGenerated Python code:")
        print("-" * 40)
        print(code)
        print("-" * 40)
        
        # Save the code if requested
        if save:
            code_file = save_code_to_file(code)
            print(f"\nCode saved to: {code_file}")
        
        # Run the code if requested
        if run:
            print("\nRunning the generated code...")
            result = execute_code(code)
            if result["error"]:
                print(f"Error running code: {result['error']}")
            else:
                print("Code execution result:")
                print(result["output"])
        
        return 0
    
    # If no prompt, show help
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
