import unittest
import subprocess
import sys
import os
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")

class TestSkillLogic(unittest.TestCase):
    
    def test_create_task_patterns(self):
        """Test that create_task.py enforces specific patterns in its help text/logic."""
        script_path = os.path.join(SCRIPTS_DIR, "create_task.py")
        result = subprocess.run(
            [sys.executable, script_path, "--help"],
            capture_output=True,
            text=True
        )
        output = result.stdout
        
        # Normalize whitespace (replace newlines and multiple spaces with single space)
        normalized_output = re.sub(r'\s+', ' ', output)
        
        # Check for enforced defaults in help text
        self.assertIn("Priority (1=Urgent, 2=High, 3=Normal, 4=Low). Default: 3", normalized_output)
        self.assertIn("Dave Witkin", normalized_output)
        self.assertIn("Default Assignee: Dave Witkin", normalized_output)

    def test_task_numbering_import(self):
        """Test that task_numbering.py can be imported (verifies path setup)."""
        script_path = os.path.join(SCRIPTS_DIR, "task_numbering.py")
        result = subprocess.run(
            [sys.executable, script_path, "--help"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Import Error Output: {result.stderr}")
        self.assertEqual(result.returncode, 0, "task_numbering.py failed to import/run")

    def test_prioritization_import(self):
        """Test that run_prioritization.py can be imported."""
        script_path = os.path.join(SCRIPTS_DIR, "run_prioritization.py")
        self.assertTrue(os.path.exists(script_path))
        with open(script_path, 'r') as f:
            content = f.read()
            self.assertIn("from run_prioritization import main", content)

if __name__ == '__main__':
    unittest.main()
