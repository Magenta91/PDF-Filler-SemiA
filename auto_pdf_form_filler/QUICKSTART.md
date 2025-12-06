# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install System Dependencies

#### Windows
1. **Tesseract OCR**
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Run installer
   - Add to PATH or note installation directory

2. **Poppler**
   - Download: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract to `C:\Program Files\poppler`
   - Add `C:\Program Files\poppler\Library\bin` to PATH

#### macOS
```bash
brew install tesseract poppler
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

### Step 2: Install Python Dependencies
```bash
cd auto_pdf_form_filler
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python test_installation.py
```

## Usage (2 minutes)

### Basic Example
```bash
python main.py samples/input.json samples/request_for_repair.pdf output/filled.pdf
```

### Custom Form
1. Create your JSON data file:
```json
{
  "date_prepared": "12/06/2025",
  "buyer_name": "John Doe",
  "property_address": "123 Main St"
}
```

2. Run the filler:
```bash
python main.py your_data.json your_form.pdf output/result.pdf
```

3. Check the output:
   - `output/result.pdf` - Filled form
   - `output/debug_info.json` - Detection details

## Troubleshooting

### "Tesseract not found"
- Windows: Set environment variable `TESSERACT_CMD` to tesseract.exe path
- Verify: `tesseract --version`

### "Poppler not found"
- Windows: Ensure poppler bin folder is in PATH
- Verify: `pdftoppm -v`

### "No fields detected"
- Check PDF quality (should be 300+ DPI)
- Review `debug_info.json` for detection details
- Adjust label patterns in `autofill/detector.py`

### "Poor positioning"
- Increase image DPI in main.py (line: `convert_from_path(..., dpi=300)`)
- Adjust line detection thresholds in `autofill/layout.py`

## Next Steps

- Read `PROJECT_OVERVIEW.md` for architecture details
- Read `WRITEUP.md` for technical background
- Customize label patterns for your forms
- Adjust detection parameters for better accuracy
