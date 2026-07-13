import sys
import os
import json
# Add current directory to path so we can import common
sys.path.append(sys.path[0])
from common import setup_path
setup_path()

# Import the TaskNumberMapper from the repo scripts
try:
    from scripts.task_number_mapper import TaskNumberMapper
except ImportError:
    # Fallback if we cannot import directly
    repo_scripts = os.path.join("C:/development/cursor-clickup", "scripts")
    sys.path.append(repo_scripts)
    try:
        from task_number_mapper import TaskNumberMapper
    except ImportError:
        print("Error: Could not import TaskNumberMapper from repo.")
        sys.exit(1)

import click

@click.group()
def cli():
    """Manage ClickUp task numbering."""
    pass

@cli.command()
@click.argument("input_str")
def parse(input_str):
    """Parse task numbers from string (e.g. "1, 2, 5-7")."""
    try:
        numbers = TaskNumberMapper.parse_task_numbers(input_str)
        click.echo(json.dumps(numbers))
    except Exception as e:
        click.echo(f"Error parsing numbers: {e}", err=True)

@cli.command()
@click.argument("numbers", nargs=-1)
def get_ids(numbers):
    """Get Task IDs for given numbers (space separated)."""
    mapper = TaskNumberMapper()
    try:
        nums = [int(n) for n in numbers]
        mapping = mapper.get_task_ids_from_numbers(nums)
        click.echo(json.dumps(mapping, indent=2))
    except Exception as e:
        click.echo(f"Error getting IDs: {e}", err=True)

if __name__ == "__main__":
    cli()
