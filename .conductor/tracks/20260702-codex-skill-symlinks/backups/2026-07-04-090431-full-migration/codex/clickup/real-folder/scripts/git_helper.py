import sys
import os
import subprocess
# Add current directory to path so we can import common
sys.path.append(sys.path[0])
from common import setup_path
setup_path()

import click

REPO_SCRIPTS = "C:/development/cursor-clickup/scripts"

@click.group()
def cli():
    """Universal Git Helper for ClickUp Repo."""
    pass

@cli.command()
@click.option("--message", "-m", required=True, help="Commit message")
def push(message):
    """Run git-push-universal.py"""
    script = os.path.join(REPO_SCRIPTS, "git-push-universal.py")
    subprocess.run([sys.executable, script, "--message", message])

@cli.command()
def inspect():
    """Run git-inspect.py"""
    script = os.path.join(REPO_SCRIPTS, "git-inspect.py")
    subprocess.run([sys.executable, script])

if __name__ == "__main__":
    cli()

