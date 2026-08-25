import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def convert_docx_to_pdf(docx_path: str, output_dir: str) -> Optional[str]:
    """
    Converts a DOCX file to PDF.
    Tries docx2pdf (Windows/Mac with MS Word) first.
    Falls back to LibreOffice (Linux VPS).
    
    Returns the path to the generated PDF, or None if conversion failed.
    """
    if not os.path.exists(docx_path):
        logger.error(f"DOCX file not found: {docx_path}")
        return None
        
    filename = os.path.basename(docx_path)
    base_name = os.path.splitext(filename)[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    # Try 1: docx2pdf (Requires MS Word, Windows/macOS)
    try:
        logger.info(f"Attempting to convert {filename} using docx2pdf...")
        # Local import to prevent crashing on Linux where pywin32 isn't available
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        
        if os.path.exists(pdf_path):
            logger.info(f"Successfully converted {filename} to PDF using docx2pdf")
            return pdf_path
    except Exception as e:
        logger.warning(f"docx2pdf conversion failed or unavailable: {e}")
        
    # Try 2: LibreOffice Headless (Linux Server / VPS Fallback)
    try:
        logger.info(f"Attempting to convert {filename} using LibreOffice fallback...")
        # The command: soffice --headless --convert-to pdf <file> --outdir <dir>
        process = subprocess.run(
            ['soffice', '--headless', '--convert-to', 'pdf', docx_path, '--outdir', output_dir],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        if process.returncode == 0 and os.path.exists(pdf_path):
            logger.info(f"Successfully converted {filename} to PDF using LibreOffice")
            return pdf_path
        else:
            logger.warning(f"LibreOffice conversion failed. Return code: {process.returncode}")
            logger.warning(f"LibreOffice stderr: {process.stderr.decode('utf-8', errors='ignore')}")
    except FileNotFoundError:
        logger.warning("LibreOffice 'soffice' command not found on this system.")
    except Exception as e:
        logger.error(f"LibreOffice fallback error: {e}")
        
    logger.error(f"All conversion methods failed for {filename}")
    return None
