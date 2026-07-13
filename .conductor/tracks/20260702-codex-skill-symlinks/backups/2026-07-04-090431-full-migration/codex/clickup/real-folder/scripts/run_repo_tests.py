import sys
import os
import unittest
from pathlib import Path

# Resolve the external repo via the shared ClickUp skill helper.
from common import setup_path
REPO_ROOT = setup_path()

# Add test directory to path
TEST_DIR = str(Path(REPO_ROOT) / "tests")
sys.path.append(TEST_DIR)

# We need to make sure the scripts/utils dirs are in path for the tests to work
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, os.path.join(str(REPO_ROOT), "scripts"))
sys.path.insert(0, os.path.join(str(REPO_ROOT), "utils"))

def run_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover all tests in the test directory
    suite.addTests(loader.discover(TEST_DIR, pattern="test_*.py"))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    print("Running ClickUp MCP Repo Tests...")
    run_suite()
