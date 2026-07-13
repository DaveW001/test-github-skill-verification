import sys
import os
import json
# Add current directory to path so we can import common
sys.path.append(sys.path[0])
from common import setup_path
setup_path()

# Import the context manager
try:
    from utils.context_manager import ContextManager
except ImportError:
    # Fallback path
    repo_utils = os.path.join("C:/development/cursor-clickup", "utils")
    sys.path.append(os.path.dirname(repo_utils)) # Add repo root
    try:
        from utils.context_manager import ContextManager
    except ImportError:
        print("Error: Could not import ContextManager from repo.")
        sys.exit(1)

import click

@click.command()
@click.argument("phrase")
@click.option("--context", default=None, help="Additional context")
def interpret(phrase, context):
    """Interpret a natural language phrase into ClickUp filters."""
    manager = ContextManager()
    result = manager.interpret_phrase(phrase, context)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    interpret()

