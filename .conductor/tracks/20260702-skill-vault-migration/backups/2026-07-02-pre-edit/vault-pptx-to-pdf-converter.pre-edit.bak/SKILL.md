---
name: pptx-to-pdf-converter
description: Convert PowerPoint presentations (.pptx, .ppt) to PDF format using Microsoft PowerPoint COM automation. Use when converting presentations to PDF, batch processing PowerPoint files, or creating PDF versions of slides. Works on Windows with Microsoft Office installed.
---

# PowerPoint to PDF Converter

Convert PowerPoint presentations (.pptx, .ppt) to PDF format using native Microsoft PowerPoint rendering for highest quality output.

## Requirements

**Platform**: Windows only  
**Prerequisites**:
- Microsoft PowerPoint (Office 2016 or later recommended)
- Python 3.x
- pywin32 library (`pip install pywin32`)

## Quick Start

### Convert a Single File

```bash
python scripts/convert_pptx_to_pdf.py "path/to/presentation.pptx"
```

### Convert All Files in a Directory

```bash
python scripts/convert_pptx_to_pdf.py "path/to/directory"
```

### Batch Convert with Options

```bash
# Include subdirectories
python scripts/convert_pptx_to_pdf.py "path/to/directory" --recursive

# Overwrite existing PDFs
python scripts/convert_pptx_to_pdf.py "path/to/directory" --overwrite

# Custom output filename
python scripts/convert_pptx_to_pdf.py "presentation.pptx" --output "custom-name.pdf"
```

## Instructions for OpenCode

When the user asks to convert PowerPoint files to PDF:

1. **Verify Environment**: Check Windows OS and PowerPoint installation
2. **Install Dependencies**: Ensure pywin32 is installed (`pip install pywin32`)
3. **Run Conversion**: Use the conversion script with appropriate arguments
4. **Handle Results**: Report success/failure and any errors

### Example Workflow

```python
# Single file conversion
python scripts/convert_pptx_to_pdf.py "C:\Presentations\slides.pptx"

# Directory batch conversion
python scripts/convert_pptx_to_pdf.py "C:\Presentations" --recursive
```

## Features

- **High Quality**: Uses native PowerPoint rendering engine
- **Batch Processing**: Convert entire directories at once
- **Recursive Search**: Process subdirectories
- **Skip Existing**: Won't overwrite PDFs unless `--overwrite` flag is used
- **Progress Tracking**: Shows conversion progress and file sizes
- **Error Handling**: Graceful handling of missing files, permissions, etc.

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--overwrite` | | Overwrite existing PDF files |
| `--recursive` | `-r` | Process subdirectories recursively |
| `--output` | `-o` | Specify output filename (single file only) |
| `--help` | `-h` | Show help message |

## Common Use Cases

### 1. Convert All Presentations in a Folder

```bash
python scripts/convert_pptx_to_pdf.py "C:\Users\Username\Documents\Presentations"
```

### 2. Convert Including Subfolders

```bash
python scripts/convert_pptx_to_pdf.py "C:\Project\Docs" --recursive
```

### 3. Force Re-conversion (Overwrite)

```bash
python scripts/convert_pptx_to_pdf.py "C:\Presentations" --overwrite
```

### 4. Convert Single File with Custom Name

```bash
python scripts/convert_pptx_to_pdf.py "report.pptx" --output "Q4-Report.pdf"
```

## Troubleshooting

### "pywin32 module not found"

**Solution**: Install pywin32:
```bash
pip install pywin32
```

### "PowerPoint not found" or COM errors

**Solution**: Ensure Microsoft PowerPoint is installed and licensed.

### "Permission denied" errors

**Solution**: Run with appropriate file system permissions or choose a different output location.

### Conversion is slow

**Expected**: Large presentations or many files will take time. The script processes files sequentially to ensure stability.

## Limitations

- **Windows Only**: Requires Microsoft PowerPoint (Windows COM automation)
- **Office Required**: Microsoft PowerPoint must be installed and licensed
- **No Linux/Mac**: This method is Windows-specific
- **GUI Visible**: PowerPoint window may briefly appear during conversion (cannot be hidden in all environments)

## Alternative Approaches

If Microsoft PowerPoint is not available, consider:

1. **Aspose.Slides** (Commercial, cross-platform)
2. **Spire.Presentation** (Commercial, limited free version)
3. **LibreOffice** (Free, lower fidelity)

See [reference.md](reference.md) for more details.

## Testing

To test this skill is working:

1. Create a test PowerPoint file: `test.pptx`
2. Run: `python scripts/convert_pptx_to_pdf.py test.pptx`
3. Verify: `test.pdf` should be created in the same directory

For automated testing, see [scripts/test_conversion.py](scripts/test_conversion.py).
