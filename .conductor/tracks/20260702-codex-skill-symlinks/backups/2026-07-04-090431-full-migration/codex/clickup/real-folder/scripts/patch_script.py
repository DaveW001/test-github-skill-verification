import re

# Read original file
with open('create_meeting_notes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Validation functions to insert
validation_functions = '''
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
    shell_patterns = {
        r'^---\s*$': "Markdown horizontal rule appears unquoted",
        r'^-\s+$': "List item with only whitespace",
        r'^>': "Shell redirection operator",
        r'^<': "Shell input redirection",
        r'^\|': "Shell pipe operator",
        r'^&\s*$': "Shell background operator",
    }
    
    # Check for emoji appearing in what looks like a file path context
    first_line = lines[0].strip() if lines else ""
    if first_line and len(first_line) < 10 and any(ord(c) > 127 for c in first_line):
        warnings.append("⚠️  Input appears to contain emoji fragments that may indicate improper quoting")
    
    # Check each line for shell patterns
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if not stripped:
            continue
            
        # Skip valid markdown headings (### Heading)
        if stripped.startswith('###'):
            continue
            
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
        r'\.md$',
        r'\.txt$',
        r'\.json$',
        r'[\\/\]$|^[a-zA-Z]:[\\/]',
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


def read_meeting_notes_from_file(file_path: str) -> tuple[bool, str | None, str]:
    """
    Read meeting notes from a file.
    
    Returns:
        (success, error_message, notes_text)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notes_text = f.read()
        return True, None, notes_text
    except FileNotFoundError:
        return False, get_file_read_guidance(file_path, "File not found"), ""
    except PermissionError:
        return False, get_file_read_guidance(file_path, "Permission denied"), ""
    except Exception as e:
        return False, get_file_read_guidance(file_path, str(e)), ""


def process_input(file_path: str | None, notes_text: str | None) -> tuple[bool, str | None, str, bool]:
    """
    Process input from either file or direct text.
    
    Returns:
        (success, error_message, notes_content, was_ambiguous)
    """
    was_ambiguous = False
    
    # Case 1: Explicit file path with --file flag
    if file_path:
        click.echo(f"📄 Reading meeting notes from file: {file_path}")
        success, error, notes = read_meeting_notes_from_file(file_path)
        if not success:
            return False, error, "", False
        return True, None, notes, False
    
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
        if is_ambig:
            click.echo(click.style(warning, fg="yellow"))
            was_ambiguous = True
            # Still proceed - read the file if it exists
            if os.path.exists(notes_text.strip()):
                click.echo("📄 Detected file path, reading from file...")
                success, error, notes = read_meeting_notes_from_file(notes_text.strip())
                if success:
                    return True, None, notes, True
                return False, error, "", True
        
        click
