"""
OCR Service — extracts text from documents and images.

Supports:
- Text files (.txt): direct read
- Images (.png, .jpg, .jpeg, .tiff, .bmp): Tesseract OCR via pytesseract
- PDFs (.pdf): PyMuPDF (fitz) text extraction
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Supported file extensions grouped by type
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
TEXT_EXTENSIONS = {".txt"}
PDF_EXTENSIONS = {".pdf"}

SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | TEXT_EXTENSIONS | PDF_EXTENSIONS


def _extract_from_text(file_path: str) -> str:
    """Read a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _extract_from_image(file_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image

        # Use TESSERACT_CMD env var if set
        tesseract_cmd = os.getenv("TESSERACT_CMD")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()

    except ImportError:
        logger.error("pytesseract or Pillow not installed.")
        raise RuntimeError("pytesseract or Pillow is not installed. Run: pip install pytesseract Pillow")

    except Exception as e:
        if "tesseract" in str(e).lower() or "not installed" in str(e).lower():
            logger.error("Tesseract OCR is not installed or not on PATH.")
            raise RuntimeError(
                "Tesseract OCR is not installed or not found on PATH. "
                "Install it from: https://github.com/tesseract-ocr/tesseract"
            )
        logger.error(f"OCR failed for {file_path}: {e}")
        raise RuntimeError(f"OCR extraction failed: {e}")


def _extract_from_pdf(file_path: str) -> str:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        return "\n\n".join(pages_text).strip()

    except ImportError:
        logger.error("PyMuPDF not installed.")
        raise RuntimeError("PyMuPDF is not installed. Run: pip install PyMuPDF")

    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
        raise RuntimeError(f"PDF text extraction failed: {e}")


def get_file_type(file_path: str) -> str:
    """Return the lowercase extension without the dot."""
    return Path(file_path).suffix.lower().lstrip(".")


def is_supported(file_path: str) -> bool:
    """Check if the file extension is supported."""
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS


def extract_text(file_path: str) -> str:
    """
    Extract text from a file.

    Automatically detects the file type and uses the appropriate extraction
    method (direct read, Tesseract OCR, or PyMuPDF).

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the file.

    Returns
    -------
    str
        Extracted text content.

    Raises
    ------
    ValueError
        If the file type is not supported.
    FileNotFoundError
        If the file does not exist.
    RuntimeError
        If extraction fails (e.g., Tesseract not installed).
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    if ext in TEXT_EXTENSIONS:
        logger.info(f"Reading text file: {file_path}")
        return _extract_from_text(file_path)

    elif ext in IMAGE_EXTENSIONS:
        logger.info(f"Running OCR on image: {file_path}")
        return _extract_from_image(file_path)

    elif ext in PDF_EXTENSIONS:
        logger.info(f"Extracting text from PDF: {file_path}")
        return _extract_from_pdf(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
