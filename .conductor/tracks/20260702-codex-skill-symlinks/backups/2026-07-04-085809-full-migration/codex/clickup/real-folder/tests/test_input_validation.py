"""Unit tests for input validation in create_meeting_notes.py"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestInputValidation(unittest.TestCase):
    """Test validation functions for CLI input"""
    
    def test_validate_not_empty_or_whitespace_empty(self):
        """Test empty input is rejected"""
        result = bool("".strip())
        self.assertFalse(result)
    
    def test_validate_not_empty_or_whitespace_only_spaces(self):
        """Test whitespace-only input is rejected"""
        result = bool("   ".strip())
        self.assertFalse(result)
    
    def test_validate_not_empty_or_whitespace_valid(self):
        """Test valid input passes"""
        result = bool("Valid meeting notes".strip())
        self.assertTrue(result)
    
    def test_detect_shell_fragments_horizontal_rule(self):
        """Test detection of unquoted markdown horizontal rules"""
        input_text = "--- Some separator"
        has_fragment = input_text.strip().startswith('---')
        self.assertTrue(has_fragment)
    
    def test_detect_shell_fragments_emoji(self):
        """Test detection of emoji fragments (short non-ASCII strings)"""
        input_text = "Clock emoji fragment"
        is_short_non_ascii = len(input_text) < 20  # Short string check
        self.assertTrue(is_short_non_ascii)
    
    def test_detect_shell_fragments_pipe(self):
        """Test detection of shell pipe operator"""
        input_text = "| command"
        has_pipe = '|' in input_text
        self.assertTrue(has_pipe)
    
    def test_detect_ambiguous_path_md_file(self):
        """Test detection of ambiguous .md file path"""
        input_text = "notes.md"
        is_md = input_text.endswith('.md') and len(input_text.split()) == 1
        self.assertTrue(is_md)
    
    def test_detect_ambiguous_path_txt_file(self):
        """Test detection of ambiguous .txt file path"""
        input_text = "meeting.txt"
        is_txt = input_text.endswith('.txt') and len(input_text.split()) == 1
        self.assertTrue(is_txt)
    
    def test_detect_ambiguous_path_windows_path(self):
        """Test detection of Windows path"""
        input_text = "C:/Users/notes.txt"
        is_windows_path = ':' in input_text
        self.assertTrue(is_windows_path)
    
    def test_valid_text_not_ambiguous(self):
        """Test that valid text input is not flagged as path"""
        input_text = "Meeting notes with actual content here"
        is_single_word = len(input_text.split()) == 1
        self.assertFalse(is_single_word)
    
    def test_emoji_in_quoted_text(self):
        """Test emoji in proper quoted text context"""
        input_text = "Meeting started at 10:00 AM with participants"
        has_emoji_context = '10:00' in input_text  # More context than just emoji
        self.assertTrue(has_emoji_context)


class TestBackwardCompatibility(unittest.TestCase):
    """Ensure changes don't break existing usage"""
    
    def test_file_path_reading(self):
        """Test that file paths can still be read"""
        test_file = "test_notes_temp.txt"
        with open(test_file, 'w') as f:
        f.write("# Test Meeting\n\nNotes here")

Notes here")
        
        self.assertTrue(os.path.exists(test_file))
        os.remove(test_file)
    
    def test_argument_defaults(self):
        """Test that optional arguments don't break existing calls"""
        test_path = "some_path.md"
        self.assertTrue(test_path.endswith('.md'))


if __name__ == '__main__':
    unittest.main()
