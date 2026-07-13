"""
Common utilities for ClickUp skill scripts.
Handles path resolution and external repo discovery.
"""

import sys
import os

# Ensure UTF-8 output on Windows (default console encoding is cp1252)
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass

from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml


def _is_placeholder_token(token: Optional[str]) -> bool:
    if not token:
        return False
    t = token.strip().lower()
    return t in {"your_token", "<your_token>", "changeme"}


def sanitize_clickup_env() -> None:
    """Remove placeholder env vars that break dotenv loading.

    python-dotenv does not override existing environment variables by default.
    If CLICKUP_API_TOKEN is set to a placeholder in the shell (e.g. 'your_token'),
    ClickUp API calls will fail with 401 even when a real token exists in .env.
    """
    raw = os.environ.get("CLICKUP_API_TOKEN")
    if _is_placeholder_token(raw):
        # Remove the placeholder so downstream dotenv loading can populate a real token.
        os.environ.pop("CLICKUP_API_TOKEN", None)

# Get the skill root directory
SKILL_ROOT = Path(__file__).parent.parent
CONFIG_FILE = SKILL_ROOT / "config.yaml"

def load_config() -> Dict[str, Any]:
    """Load the skill configuration from config.yaml."""
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
        return {}

def expand_path(path: str) -> Path:
    """Expand user home (~) and environment variables in path."""
    expanded = os.path.expanduser(os.path.expandvars(path))
    return Path(expanded).resolve()

def find_external_repo(config: Dict[str, Any]) -> Optional[Path]:
    """
    Find the external cursor-clickup-mcp repository.
    
    Checks in order:
    1. Primary path from config
    2. Fallback paths from config
    3. Parent directory search
    
    Returns the path if found, None otherwise.
    """
    external_repo_config = config.get('external_repo', {})
    primary_path = external_repo_config.get('path')
    
    # Build list of paths to check
    paths_to_check: List[str] = []
    
    if primary_path:
        paths_to_check.append(primary_path)
    
    # Add fallback paths
    fallback_paths = config.get('fallback_paths', [])
    paths_to_check.extend(fallback_paths)
    
    # Check each path
    for path_str in paths_to_check:
        try:
            path = expand_path(path_str)
            if is_valid_repo(path, external_repo_config):
                # Update config if auto-discovery is enabled and this wasn't the primary
                discovery_config = config.get('discovery', {})
                if (discovery_config.get('enabled', True) and 
                    discovery_config.get('update_config', True) and
                    path_str != primary_path):
                    update_config_path(path)
                
                return path
        except Exception:
            continue
    
    # Try parent directory search as last resort
    discovery_config = config.get('discovery', {})
    if discovery_config.get('enabled', True):
        max_depth = discovery_config.get('max_search_depth', 3)
        found_path = search_parent_directories(max_depth, external_repo_config)
        if found_path and discovery_config.get('update_config', True):
            update_config_path(found_path)
        return found_path
    
    return None

def is_valid_repo(path: Path, config: Dict[str, Any]) -> bool:
    """Check if a path contains a valid cursor-clickup-mcp repository."""
    if not path.exists():
        return False
    
    if not path.is_dir():
        return False
    
    # Check for required files
    required_files = config.get('required_files', [
        'clickup_api.py',
        'scripts/clickup_client.py'
    ])
    
    for file_path in required_files:
        full_path = path / file_path
        if not full_path.exists():
            return False
    
    return True

def search_parent_directories(max_depth: int, config: Dict[str, Any]) -> Optional[Path]:
    """Search parent directories for the repo."""
    current = SKILL_ROOT
    
    for _ in range(max_depth):
        parent = current.parent
        if parent == current:  # Reached root
            break
        
        # Check if cursor-clickup-mcp exists in this directory
        potential_repo = parent / 'cursor-clickup-mcp'
        if is_valid_repo(potential_repo, config):
            return potential_repo
        
        # Also check development folder
        dev_folder = parent / 'development' / 'cursor-clickup-mcp'
        if is_valid_repo(dev_folder, config):
            return dev_folder
        
        current = parent
    
    return None

def update_config_path(path: Path) -> None:
    """Update the config file with the discovered path."""
    try:
        config = load_config()
        if 'external_repo' not in config:
            config['external_repo'] = {}
        config['external_repo']['path'] = str(path)
        
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        print(f"Note: Could not update config.yaml with discovered path: {e}")

def setup_path() -> Optional[Path]:
    """
    Set up Python path to include the external cursor-clickup-mcp repository.
    
    Returns the path to the external repo (or None if not required and not found).
    
    Raises:
        RuntimeError: If the external repo cannot be found and is required.
    """
    config = load_config()
    external_repo_config = config.get('external_repo', {})
    
    # Find the repo
    repo_path = find_external_repo(config)
    
    if repo_path is None:
        if external_repo_config.get('required', True):
            raise RuntimeError(
                f"\n❌ External cursor-clickup-mcp repository not found!\n\n"
                f"Expected locations:\n"
                f"  - Primary: {external_repo_config.get('path', 'Not configured')}\n"
                f"  - Or in fallback paths (see config.yaml)\n\n"
                f"To fix:\n"
                f"  1. Ensure cursor-clickup-mcp exists at one of the expected locations\n"
                f"  2. Or update {CONFIG_FILE} with the correct path\n"
                f"  3. Or set the repo path in your environment: CLICKUP_REPO_PATH\n\n"
                f"Current config file: {CONFIG_FILE}\n"
            )
        else:
            print("Warning: External repo not found but not required. Some features may not work.")
            return None
    
    # Add to Python path if not already there
    repo_str = str(repo_path)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)
    
    # Also add scripts subdirectory
    scripts_path = repo_path / 'scripts'
    if scripts_path.exists():
        scripts_str = str(scripts_path)
        if scripts_str not in sys.path:
            sys.path.insert(0, scripts_str)

    # Finally, sanitize env var overrides (placeholder token blocks dotenv).
    sanitize_clickup_env()

    # Emit a small runtime hint so agents can tell which host mount is active.
    skill_root_str = str(SKILL_ROOT).replace("\\", "/").lower()
    if ".codex/skills/clickup" in skill_root_str:
        host_mount = "Codex Desktop"
    elif ".config/opencode/skill/clickup" in skill_root_str:
        host_mount = "OpenCode Desktop/CLI"
    else:
        host_mount = "Unknown host mount"
    print(f"[OK] Skill root: {SKILL_ROOT}")
    print(f"[OK] Host mount: {host_mount}")
    
    return repo_path

def get_repo_path() -> Optional[Path]:
    """Get the external repo path without modifying sys.path."""
    config = load_config()
    return find_external_repo(config)

# Legacy setup_path for backwards compatibility
def setup_path_legacy():
    """Legacy path setup - kept for backwards compatibility."""
    return setup_path()
