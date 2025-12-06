# Quick Reference Guide

## Installation (One-Time Setup)

```bash
# 1. Install system dependencies
# Windows: Download and install Tesseract + Poppler, add to PATH
# macOS: brew install tesseract poppler
# Linux: sudo apt-get install tesseract-ocr poppler-utils

# 2. Install Python packages
pip install -r requirements.txt

# 3. Verify
python test_installation.py
```

## Basic Usage

```bash
python fill_form.py <input_json> <template_pdf> <output_pdf>
```

**Example:**
```bash
python fill_form.py samples/input.json samples/request_for_repair.pdf output/filled.pdf
```

## Input JSON Format

```json
{
  "date_prepared": "2025-12-06",
  "agreement_date": "2025-11-15",
  "property_address": "123 Main Street, Los Angeles, CA 90001",
  "buyer_name": "John Doe",
  "seller_name": "Jane Smith",
  "repairs": [
    "Replace broken window",
    "Fix leaking faucet"
  ]
}
```

## Auto-Generated Fields

✅ **buyer_initials** - From buyer_name ("John Doe" → "JD")  
✅ **seller_initials** - From seller_name ("Jane Smith" → "JS")  
✅ **buyer_signature_name** - Same as buyer_name  
✅ **seller_signature_name** - Same as seller_name  
✅ **signature_date** - From date_prepared (formatted to MM/DD/YYYY)  

## Date Formats

**Input** (any of these):
- ISO: `2025-12-06`
- US: `12/06/2025`
- European: `06/12/2025`

**Output**: Always `MM/DD/YYYY` (e.g., `12/06/2025`)

## Supported Forms

- **California Request for Repair** (`request_for_repair`)

## Common Commands

```bash
# Fill form with auto-detection
python fill_form.py data.json form.pdf output.pdf

# Fill form with specific template
python fill_form.py data.json form.pdf output.pdf request_for_repair

# Test installation
python test_installation.py

# Run example
python fill_form.py samples/input.json samples/request_for_repair.pdf output/test.pdf
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Tesseract not found" | Install Tesseract, add to PATH |
| "Poppler not found" | Install Poppler, add bin folder to PATH |
| "Template not found" | Specify template name or add to templates.py |
| Fields not appearing | Verify template coordinates |

## File Locations

- **Main script**: `fill_form.py`
- **Templates**: `autofill/templates.py`
- **Sample data**: `samples/input.json`
- **Sample form**: `samples/request_for_repair.pdf`
- **Output**: `output/`

## Documentation

- **README.md** - Full documentation
- **FINAL_SOLUTION.md** - Complete solution overview
- **CURRENT_STATUS.md** - Project status & challenges
- **QUICKSTART.md** - Installation guide

## Support

Check documentation files for detailed information:
1. Installation issues → QUICKSTART.md
2. Usage examples → README.md
3. Adding forms → FINAL_SOLUTION.md
4. Technical details → CURRENT_STATUS.md
