import sys
# Add current directory to path so we can import common
sys.path.append(sys.path[0])
from common import setup_path
setup_path()

# Import the CLI function from the repo script
try:
    from get_task_cli import get_task_cli
except ImportError as e:
    print(f"Error importing from repository: {e}")
    sys.exit(1)

if __name__ == "__main__":
    get_task_cli()

