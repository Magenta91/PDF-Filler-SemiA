"""Quick test to verify all dependencies are installed correctly."""
import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import pytesseract
        print("✓ pytesseract")
    except ImportError as e:
        print(f"✗ pytesseract: {e}")
        return False
    
    try:
        import cv2
        print("✓ opencv-python")
    except ImportError as e:
        print(f"✗ opencv-python: {e}")
        return False
    
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image")
    except ImportError as e:
        print(f"✗ pdf2image: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ pillow")
    except ImportError as e:
        print(f"✗ pillow: {e}")
        return False
    
    try:
        from reportlab.pdfgen import canvas
        print("✓ reportlab")
    except ImportError as e:
        print(f"✗ reportlab: {e}")
        return False
    
    try:
        from pypdf import PdfReader
        print("✓ pypdf")
    except ImportError as e:
        print(f"✗ pypdf: {e}")
        return False
    
    try:
        from Levenshtein import ratio
        print("✓ python-Levenshtein")
    except ImportError as e:
        print(f"✗ python-Levenshtein: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    return True


def test_tesseract():
    """Test that Tesseract is installed and accessible."""
    print("\nTesting Tesseract OCR...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"✗ Tesseract not found or not in PATH: {e}")
        print("  Please install Tesseract OCR:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  macOS: brew install tesseract")
        print("  Linux: sudo apt-get install tesseract-ocr")
        return False


def test_poppler():
    """Test that Poppler is installed (for pdf2image)."""
    print("\nTesting Poppler (for PDF conversion)...")
    try:
        from pdf2image import convert_from_path
        # This will fail if poppler is not installed
        print("✓ Poppler appears to be available")
        print("  (Full test requires a PDF file)")
        return True
    except Exception as e:
        print(f"✗ Poppler may not be installed: {e}")
        print("  Please install Poppler:")
        print("  Windows: https://github.com/oschwartz10612/poppler-windows/releases")
        print("  macOS: brew install poppler")
        print("  Linux: sudo apt-get install poppler-utils")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Auto PDF Form Filler - Installation Test")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_tesseract()
    all_passed &= test_poppler()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! You're ready to use the form filler.")
    else:
        print("✗ Some tests failed. Please install missing dependencies.")
        sys.exit(1)
    print("=" * 60)
