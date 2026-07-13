"""
Input validation for ClickUp meeting notes CLI.
Prevents shell command parsing errors and provides helpful error messages.
"""

import re
import os


def validate_not_empty_or_whitespace(input_text):
    """Validate input is not empty or whitespace-only."""
    if not input_text or not input_text.strip():
        return False, "No meeting notes content provided. Please provide text or use --file to specify a file."
    return True, None


def validate_input_for_shell_fragments(input_text):
    """
    Detect shell command fragments that indicate improper quoting.
    
    Returns (is_safe, warnings_list)
    """
    warnings = []
    lines = input_text.split('
')
    
    # Shell command patterns to detect
    shell_patterns = {
        r'^---\s*$': "Markdown horizontal rule appears unquoted",
        r'^-\s+$': "List item with only whitespace",
        r'^>': "Shell redirection operator",
        r'^<': "Shell input redirection", 
        r'^\|': "Shell pipe operator",
        r'^&\s*$': "Shell background operator",
    }
    
    # Check for emoji fragments (appears as separate args when unquoted)
    first_line = lines[0].strip() if lines else ""
    if first_line and len(first_line) < 10 and any(ord(c) > 127 for c in first_line):
        warnings.append("Input appears to contain emoji fragments (indicates improper quoting)")
    
    # Check each line for shell patterns
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip valid markdown headings
        if stripped.startswith('###'):
            continue
        for pattern, message in shell_patterns.items():
            if re.match(pattern, stripped):
                warnings.append(f"Line {i}: {message}")
                break
    
    return (len(warnings) == 0, warnings)


def detect_ambiguous_path(input_text):
    """
    Detect if input looks like a file path without --file flag.
    
    Returns (is_ambiguous, warning_message)
    """
    stripped = input_text.strip()
    path_indicators = [
        r'\.md$', r'\.txt$', r'\.json$',
        r'[\/]$|^[a-zA-Z]:[\/]',  # Windows/Unix paths
    ]
    
    for pattern in path_indicators:
        if re.search(pattern, stripped) and len(stripped.split()) == 1:
            return True, f"Input looks like a file path: {stripped}
Consider using --file flag for clarity"
    
    return False, None


def format_error_with_guidance(error, context):
    """Format error with actionable suggestions."""
    lines = [f"
{'='*60}", f"ERROR: {error}", f"{'='*60}"]
    if context.get('suggestion'):
        lines.append(f"
Suggestion: {context['suggestion']}")
    if context.get('example'):
        lines.append("
Example:")
        for ex in context['example']:
            lines.append(f"   {ex}")
    lines.append(f"
{'='*60}
")
    return '
'.join(lines)


def get_file_read_guidance(file_path, error_detail):
    """Generate guidance for file reading errors."""
    return format_error_with_guidance(
        f"Error reading file '{file_path}': {error_detail}",
        {
            'suggestion': 'Ensure the file exists and you have read permissions.',
            'example': [
                f'python create_meeting_notes.py --file "{file_path}"',
                'python create_meeting_notes.py "Your notes text..."'
            ]
        }
    )


def get_shell_fragment_guidance(detected_fragments):
    """Generate guidance when shell fragments detected."""
    fragments = '
   '.join(detected_fragments)
    return format_error_with_guidance(
        f"Detected {len(detected_fragments)} shell command fragment(s):
   {fragments}",
        {
            'suggestion': 'Your input appears to be unquoted. Wrap meeting notes in quotes.',
            'example': [
                'Incorrect: python create_meeting_notes.py 🕞 Started at 10:00 AM --- Some notes',
                'Correct: python create_meeting_notes.py "🕞 Started at 10:00 AM --- Some notes"',
                'Or use --file: python create_meeting_notes.py --file notes.md'
            ]
        }
    )


def read_meeting_notes_from_file(file_path):
    """Read meeting notes from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return True, None, f.read()
    except FileNotFoundError:
        return False, get_file_read_guidance(file_path, "File not found"), ""
    except PermissionError:
        return False, get_file_read_guidance(file_path, "Permission denied"), ""
    except Exception as e:
        return False, get_file_read_guidance(file_path, str(e)), ""


def process_input(file_path, notes_text):
    """
    Process input from either file or direct text.
    
    Returns (success, error_message, notes_content, was_ambiguous)
    """
    was_ambiguous = False
    
    # Case 1: Explicit file path with --file flag
    if file_path:
        return read_meeting_notes_from_file(file_path) + (False,)
    
    # Case 2: Direct text provided
    if notes_text:
        # Validate not empty
        is_valid, error = validate_not_empty_or_whitespace(notes_text)
        if not is_valid:
            return False, error, "", False
        
        # Check for shell fragments
        is_safe, warnings = validate_input_for_shell_fragments(notes_text)
        if not is_safe:
            return False, get_shell_fragment_guidance(warnings), "", False
        
        # Check for ambiguous path
        is_ambig, warning = detect_ambiguous_path(notes_text)
        if is_ambig and os.path.exists(notes_text.strip()):
            # It's actually a file path - read it
            return read_meeting_notes_from_file(notes_text.strip()) + (True,)
        
        return True, None, notes_text, is_ambig
    
    # Case 3: No input provided
    return False, format_error_with_guidance(
        "No input provided",
        {
            'suggestion': 'Provide meeting notes as text or specify a file path.',
            'example': [
                'python create_meeting_notes.py "Your meeting notes..."',
                'python create_meeting_notes.py --file notes.md'
            ]
        }
    ), "", False
