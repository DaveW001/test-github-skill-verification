"""
PowerPoint to PDF Converter
Converts .pptx files to PDF using Microsoft PowerPoint COM automation via pywin32
"""

import win32com.client
import os
import glob
import sys
import time
from pathlib import Path
from datetime import datetime

# PowerPoint save format constant for PDF
PP_SAVE_AS_PDF = 32


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def convert_pptx_to_pdf(pptx_path, pdf_path=None):
    """
    Convert a single PowerPoint file to PDF.
    
    Args:
        pptx_path: Path to the .pptx file
        pdf_path: Optional output path for PDF (defaults to same name with .pdf extension)
    
    Returns:
        tuple: (success: bool, message: str, pdf_path: str or None)
    """
    pptx_path = Path(pptx_path)
    
    if not pptx_path.exists():
        return False, f"File not found: {pptx_path}", None
    
    if pptx_path.suffix.lower() not in ['.pptx', '.ppt']:
        return False, f"Not a PowerPoint file: {pptx_path}", None
    
    # Determine PDF output path
    if pdf_path is None:
        pdf_path = pptx_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)
    
    powerpoint = None
    presentation = None
    
    try:
        log(f"Starting conversion: {pptx_path.name}")
        
        # Create PowerPoint application instance
        log("  Initializing PowerPoint COM object...")
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        # Note: Cannot hide PowerPoint window in restricted environments
        # Just disable alerts to prevent dialogs
        powerpoint.DisplayAlerts = False
        
        # Open the presentation
        log(f"  Opening presentation...")
        presentation = powerpoint.Presentations.Open(str(pptx_path.absolute()))
        
        # Save as PDF
        log(f"  Saving as PDF: {pdf_path.name}")
        presentation.SaveAs(str(pdf_path.absolute()), PP_SAVE_AS_PDF)
        
        # Close presentation
        log("  Closing presentation...")
        presentation.Close()
        presentation = None
        
        # Quit PowerPoint
        log("  Quitting PowerPoint...")
        powerpoint.Quit()
        powerpoint = None
        
        # Verify PDF was created
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            log(f"  [OK] Success! PDF created: {pdf_path.name} ({file_size_mb:.2f} MB)")
            return True, f"Converted successfully ({file_size_mb:.2f} MB)", str(pdf_path)
        else:
            return False, "PDF file was not created", None
            
    except Exception as e:
        error_msg = f"Error converting {pptx_path.name}: {str(e)}"
        log(f"  [ERROR] {error_msg}")
        return False, error_msg, None
        
    finally:
        # Cleanup - ensure COM objects are released
        if presentation:
            try:
                presentation.Close()
            except:
                pass
        if powerpoint:
            try:
                powerpoint.Quit()
            except:
                pass
        powerpoint = None
        presentation = None


def batch_convert_directory(directory_path):
    """
    Convert all PowerPoint files in a directory to PDF.
    
    Args:
        directory_path: Path to directory containing .pptx files
    
    Returns:
        dict: Summary of conversion results
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        log(f"ERROR: Directory not found: {directory}")
        return {"error": "Directory not found"}
    
    if not directory.is_dir():
        log(f"ERROR: Path is not a directory: {directory}")
        return {"error": "Not a directory"}
    
    # Find all PowerPoint files
    pptx_files = list(directory.glob("*.pptx"))
    ppt_files = list(directory.glob("*.ppt"))
    all_powerpoint_files = pptx_files + ppt_files
    
    if not all_powerpoint_files:
        log(f"No PowerPoint files found in: {directory}")
        return {"error": "No PowerPoint files found"}
    
    log(f"\n{'='*70}")
    log(f"BATCH CONVERSION STARTED")
    log(f"Directory: {directory}")
    log(f"Files found: {len(all_powerpoint_files)}")
    log(f"{'='*70}\n")
    
    results = {
        "total": len(all_powerpoint_files),
        "successful": 0,
        "failed": 0,
        "conversions": [],
        "start_time": datetime.now().isoformat()
    }
    
    # Process each file
    for i, pptx_file in enumerate(all_powerpoint_files, 1):
        log(f"\n[{i}/{len(all_powerpoint_files)}] Processing: {pptx_file.name}")
        
        # Check if PDF already exists
        pdf_file = pptx_file.with_suffix('.pdf')
        if pdf_file.exists():
            log(f"  [WARN] PDF already exists, skipping: {pdf_file.name}")
            results["conversions"].append({
                "file": str(pptx_file),
                "status": "skipped",
                "reason": "PDF already exists"
            })
            continue
        
        # Convert file
        success, message, pdf_path = convert_pptx_to_pdf(pptx_file)
        
        if success:
            results["successful"] += 1
            results["conversions"].append({
                "file": str(pptx_file),
                "status": "success",
                "pdf": pdf_path,
                "message": message
            })
        else:
            results["failed"] += 1
            results["conversions"].append({
                "file": str(pptx_file),
                "status": "failed",
                "message": message
            })
        
        # Small delay between files to ensure cleanup
        time.sleep(1)
    
    # Summary
    results["end_time"] = datetime.now().isoformat()
    
    log(f"\n{'='*70}")
    log(f"BATCH CONVERSION COMPLETE")
    log(f"{'='*70}")
    log(f"Total files: {results['total']}")
    log(f"Successful: {results['successful']}")
    log(f"Failed: {results['failed']}")
    log(f"{'='*70}\n")
    
    return results


def main():
    """Main entry point"""
    
    # Default target directory
    default_dir = r"C:\Users\DaveWitkin\OneDrive - Packaged Agile\Desktop\Army C2"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = default_dir
    
    log("\n" + "="*70)
    log("PowerPoint to PDF Converter")
    log("="*70)
    log(f"Target: {target}")
    log("="*70 + "\n")
    
    # Check if pywin32 is available
    try:
        import win32com.client
        log("[OK] pywin32 module loaded successfully")
    except ImportError:
        log("[ERROR] ERROR: pywin32 module not found. Please install: pip install pywin32")
        sys.exit(1)
    
    # Run conversion
    results = batch_convert_directory(target)
    
    # Exit with appropriate code
    failed_count = int(results.get("failed", 0))
    if results.get("error"):
        sys.exit(1)
    elif failed_count > 0:
        log(f"\n[ERROR] {failed_count} conversion(s) failed")
        sys.exit(1)
    else:
        log("\n[OK] All conversions completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
