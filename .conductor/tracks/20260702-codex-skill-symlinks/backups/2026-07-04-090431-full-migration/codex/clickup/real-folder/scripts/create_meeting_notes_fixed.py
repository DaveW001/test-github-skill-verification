import sys
import os

# Set UTF-8 encoding for stdout/stderr to handle emojis on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python < 3.7 or other environment

sys.path.append(sys.path[0])
from common import setup_path
setup_path()

import click
import re
from datetime import datetime
import pytz
import time
import requests

# Import from cursor-clickup-mcp repo
from clickup_client import ClickUpClient

# Constants
MEETING_NOTES_LIST_ID = "901107655225"
DAVE_USER_ID = "80264"

# Custom Field IDs for Meeting Notes list
CF_MEETING_DATE = "19408341-d116-45fc-b30e-8a3a2bbbadbf"
CF_FOLLOW_UP = "9ddd4ccd-5461-4105-af17-d106f64ceb7f"

# Follow Up options
FOLLOW_UP_YES = "904d53a4-615f-4876-9d39-3d3ac2f66fc6"
FOLLOW_UP_NO = "a3767735-31ae-4bde-9509-2e4aec952a1f"


# ============================================================================
# VALIDATION LAYER
# ============================================================================

def validate_not_empty_or_whitespace(input_text: str) -> tuple[bool, str | None]:
    """
    Validate that input is not empty or whitespace-only.
    
    Returns:
        (is_valid, error_message)
    """
    if not input_text or not input_text.strip():
        return False, "❌ No meeting notes content provided. Please provide text or use --file to specify a file."
    return True, None


def validate_input_for_shell_fragments(input_text: str) -> tuple[bool, list[str]]:
    """
    Detect shell command fragments in input that might indicate improper quoting.
    
    This detects patterns that commonly appear when bash interprets markdown
    or special characters as shell commands instead of string content.
    
    Args:
        input_text: The input text to validate
        
    Returns:
        (is_safe, warnings): 
            - is_safe: True if no shell fragments detected
            - warnings: List of warning messages (empty if is_safe is True)
    """
    warnings = []
    lines = input_text.split('\n')
    
    # Shell command patterns to detect
    # Note: We whitelist valid markdown patterns (e.g., ### headings)
    shell_patterns = {
        r'^---\s*$': "Markdown horizontal rule appears unquoted",
        r'^-\s+$': "List item with only whitespace",
        r'^>': "Shell redirection operator",
        r'^<': "Shell input redirection",
        r'^\|': "Shell pipe operator",
        r'^&\s*$': "Shell background operator",
    }
    
    # Check for emoji appearing in what looks like a file path context
    # (e.g., if the first line is just an emoji like 🕞)
    first_line = lines[0].strip() if lines else ""
    if first_line and len(first_line) < 10 and any(ord(c) > 127 for c in first_line):
        # Short string with non-ASCII - likely an emoji fragment
        warnings.append("⚠️  Input appears to contain emoji fragments that may indicate improper quoting")
    
    # Check each line for shell patterns
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
            
        # Skip valid markdown headings (### Heading)
        if stripped.startswith('###'):
            continue
            
        # Check for shell fragments
        for pattern, message in shell_patterns.items():
            if re.match(pattern, stripped):
                warnings.append(f"Line {i}: {message}")
                break
    
    return (len(warnings) == 0, warnings)


def detect_ambiguous_path(input_text: str) -> tuple[bool, str | None]:
    """
    Detect if input looks like a file path but wasn't provided via --file flag.
    
    Args:
        input_text: The input text to check
        
    Returns:
        (is_ambiguous, warning_message):
            - is_ambiguous: True if input looks like a file path
            - warning_message: Warning text (None if not ambiguous)
    """
    stripped = input_text.strip()
    
    # Check for common file patterns
    path_indicators = [
        r'\.md$',          # Markdown files
        r'\.txt$',         # Text files
        r'\.json$',        # JSON files
        r'[\/]$|^[a-zA-Z]:[\/]',  # Windows/Unix paths
    ]
    
    for pattern in path_indicators:
        if re.search(pattern, stripped) and len(stripped.split()) == 1:
            return True, f"⚠️  Input looks like a file path: {stripped}\n   Consider using --file flag for clarity"
    
    return False, None


def format_error_with_guidance(error: str, context: dict) -> str:
    """
    Format error message with actionable suggestions based on context.
    
    Args:
        error: The error message
        context: Dict with keys: input_type, suggestion, example
        
    Returns:
        Formatted error message with guidance
    """
    output = [f"\n{'='*60}", f"❌ {error}", f"{'='*60}"]
    
    if context.get('suggestion'):
        output.append(f"\n💡 Suggestion: {context['suggestion']}")
    
    if context.get('example'):
        output.append(f"\n📝 Example:")
        for line in context['example']:
            output.append(f"   {line}")
    
    output.append(f"\n{'='*60}\n")
    return '\n'.join(output)


def get_file_read_guidance(file_path: str, error_detail: str) -> str:
    """
    Generate helpful guidance for file reading errors.
    """
    context = {
        'suggestion': 'Ensure the file exists and you have read permissions.',
        'example': [
            f'Check if file exists: ls "{file_path}"',
            f'Or use --file flag: python create_meeting_notes.py --file "{file_path}"',
            'Or pass text directly: python create_meeting_notes.py "Your meeting notes text..."'
        ]
    }
    return format_error_with_guidance(f"Error reading file '{file_path}': {error_detail}", context)


def get_shell_fragment_guidance(detected_fragments: list[str]) -> str:
    """
    Generate guidance when shell fragments are detected.
    """
    fragments_list = '\n   '.join(detected_fragments)
    context = {
        'suggestion': 'Your input appears to be unquoted. Wrap your meeting notes in quotes to prevent shell parsing.',
        'example': [
            '❌ Incorrect (unquoted):',
            '   python create_meeting_notes.py 🕞 Started at 10:00 AM --- Some notes',
            '',
            '✅ Correct (with quotes):',
            '   python create_meeting_notes.py "🕞 Started at 10:00 AM --- Some notes"',
            '',
            '✅ Or use --file for files:',
            '   python create_meeting_notes.py --file notes.md'
        ]
    }
    return format_error_with_guidance(
        f"Detected {len(detected_fragments)} shell command fragment(s):\n   {fragments_list}",
        context
    )


# ============================================================================
# ORIGINAL MEETING NOTES PARSING (unchanged)
# ============================================================================

def parse_meeting_notes(text):
    """
    Parse meeting notes text to extract key information.

    Looks for:
    - Meeting date (from title, Started line, or Date line)
    - Attendees (from Attendees section)
    - Action items (presence check)
    """
    meeting_date = None
    attendees = None
    has_action_items = False

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Parse Attendees (check FIRST before # line detection)
        if '## Attendees' in line or '**Attendees:**' in line:
            content = line.replace('## Attendees', '').replace('**Attendees:**', '').strip()
            if content:
                attendees = content
            elif i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith(('-', '*', '#')):
                    attendees = next_line

       
