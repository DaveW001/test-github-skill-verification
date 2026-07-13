import sys
import os
import json
# Add current directory to path so we can import common
sys.path.append(sys.path[0])
from common import setup_path
setup_path()

# Import the TemplateManager from the repo scripts
try:
    from scripts.template_manager import TemplateManager
except ImportError:
    # Fallback if we cannot import directly
    repo_scripts = os.path.join("C:/development/cursor-clickup", "scripts")
    sys.path.append(repo_scripts)
    try:
        from template_manager import TemplateManager
    except ImportError:
        print("Error: Could not import TemplateManager from repo.")
        sys.exit(1)

import click

@click.group()
def cli():
    """Manage ClickUp templates."""
    pass

@cli.command("list-tasks")
def list_tasks():
    """List available task templates."""
    manager = TemplateManager()
    manager.list_task_templates()

@cli.command("list-projects")
def list_projects():
    """List available project templates."""
    manager = TemplateManager()
    manager.list_project_templates()

@cli.command("create-task")
@click.argument("category")
@click.argument("index", type=int)
@click.argument("list_name")
def create_task(category, index, list_name):
    """Create a task from a template.
    
    Usage: python templates.py create-task <category> <index> <list_name>
    """
    manager = TemplateManager()
    result = manager.create_task_from_template(category, index, list_name)
    if result:
        print(f"✅ Task created successfully: {result.get("id")}")
    else:
        print("❌ Failed to create task")
        sys.exit(1)

@cli.command("create-project")
@click.argument("template")
@click.argument("project_name")
@click.argument("space_name")
def create_project(template, project_name, space_name):
    """Create a project from a template.
    
    Usage: python templates.py create-project <template> <project_name> <space_name>
    """
    manager = TemplateManager()
    result = manager.create_project_from_template(template, project_name, space_name)
    if result:
        print("✅ Project created successfully")
    else:
        print("❌ Failed to create project")
        sys.exit(1)

if __name__ == "__main__":
    cli()

