# Auto PDF Form Filler

Automatically fill PDF forms using template-based coordinate mapping with intelligent field derivation.

## Features

- ✅ Template-based form filling with 100% accuracy
- ✅ Automatic field derivation (initials, signatures from names)
- ✅ Automatic date format conversion (ISO → MM/DD/YYYY)
- ✅ Multi-page PDF support
- ✅ Form template auto-detection
- ✅ Multi-line field support (repairs, notes, etc.)

## Quick Start

### Installation

1. **Install System Dependencies**

   **Windows:**
   - Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
   - Poppler: https://github.com/oschwartz10612/poppler-windows/releases
   - Add both to PATH

   **macOS:**
   ```bash
   brew install tesseract poppler
   ```

   **Linux:**
   ```bash
   sudo apt-get install tesseract-ocr poppler-utils
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python test_installation.py
   ```

### Usage

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
    "Replace broken window in master bedroom",
    "Fix leaking kitchen faucet",
    "Repair garage door opener"
  ]
}
```

### Automatic Field Derivation

The system automatically generates these fields:

| Derived Field | Source | Example |
|--------------|--------|---------|
| `buyer_initials` | `buyer_name` | "John Doe" → "JD" |
| `seller_initials` | `seller_name` | "Jane Smith" → "JS" |
| `buyer_signature_name` | `buyer_name` | "John Doe" |
| `seller_signature_name` | `seller_name` | "Jane Smith" |
| `signature_date` | `date_prepared` | "2025-12-06" → "12/06/2025" |

### Date Format Conversion

Dates are automatically converted from ISO format to MM/DD/YYYY:
- Input: `"2025-12-06"` (ISO 8601)
- Output: `"12/06/2025"` (US format)

Supported input formats:
- ISO: `2025-12-06`, `2025-12-06T10:30:00`
- US: `12/06/2025`, `12-06-2025`
- European: `06/12/2025`, `06-12-2025`

## Supported Forms

### California Request for Repair
- Template name: `request_for_repair`
- Auto-detected from form content
- 2 pages with multiple field types

## How It Works

1. **Load JSON data** - Parse input values
2. **Process fields** - Derive initials, format dates
3. **Convert PDF** - Convert to 300 DPI images
4. **Detect template** - Auto-identify form type using OCR
5. **Apply template** - Use predefined coordinates
6. **Generate overlay** - Create transparent PDF with text
7. **Merge** - Combine overlay with original PDF

## Project Structure

```
auto_pdf_form_filler/
├── fill_form.py              # Main entry point (recommended)
├── main_template.py          # Detailed template-based filler
├── main.py                   # Experimental auto-detection
├── autofill/
│   ├── ocr.py               # Text extraction
│   ├── detector.py          # Label matching
│   ├── layout.py            # Line detection
│   ├── renderer.py          # PDF overlay generation
│   ├── merger.py            # PDF merging
│   ├── templates.py         # Form templates
│   └── field_processor.py   # Field derivation & formatting
├── samples/
│   ├── input.json           # Example data
│   └── request_for_repair.pdf
└── output/                  # Generated PDFs
```

## Adding New Form Templates

To add support for a new form type:

1. **Create template definition** in `autofill/templates.py`:

```python
MY_FORM_TEMPLATE = {
    "name": "My Form Name",
    "pages": 1,
    "dpi": 72,
    "fields": {
        "field_name": [
            {"page": 1, "x": 100, "y": 700}
        ],
        "multi_line_field": {
            "page": 1,
            "x": 85,
            "y": 500,
            "line_spacing": 12
        }
    }
}
```

2. **Add to template registry**:

```python
TEMPLATES = {
    "request_for_repair": REQUEST_FOR_REPAIR_TEMPLATE,
    "my_form": MY_FORM_TEMPLATE
}
```

3. **Use the template**:

```bash
python fill_form.py data.json form.pdf output.pdf my_form
```

## Advanced Usage

### Specify Template Manually

```bash
python fill_form.py data.json form.pdf output.pdf request_for_repair
```

### Override Derived Fields

Include fields in your JSON to override auto-generation:

```json
{
  "buyer_name": "John Doe",
  "buyer_initials": "JRD",
  "signature_date": "2025-12-10"
}
```

### Debug Mode

Use `main_template.py` for detailed output:

```bash
python main_template.py samples/input.json samples/request_for_repair.pdf output/debug.pdf
```

## Limitations

- **Template Required**: Each form type needs a predefined template
- **Coordinate Precision**: Templates use exact PDF coordinates
- **Form Variations**: Layout changes require template updates
- **No Auto-Detection**: Pure automatic detection is 50-70% accurate (see `CURRENT_STATUS.md`)

## Why Template-Based?

Pure automatic form field detection is an unsolved problem in the industry. Even commercial solutions like Adobe Acrobat require manual corrections. Our template-based approach provides:

- ✅ 100% accuracy for known forms
- ✅ Fast processing (< 5 seconds)
- ✅ Reliable and maintainable
- ✅ Easy to extend with new forms

See `CURRENT_STATUS.md` for detailed analysis of auto-detection challenges.

## Troubleshooting

### "Tesseract not found"
- Ensure Tesseract is installed and in PATH
- Windows: Set `TESSERACT_CMD` environment variable

### "Poppler not found"
- Ensure Poppler bin folder is in PATH
- Verify with: `pdftoppm -v`

### "Template not found"
- Check available templates: `request_for_repair`
- Specify template name as 4th argument
- Create new template in `autofill/templates.py`

### Fields not appearing
- Verify template coordinates match your PDF
- Check `output/debug_info.json` for details
- Use `analyze_detection.py` to compare positions

## Documentation

- **README.md** - This file
- **CURRENT_STATUS.md** - Project status and challenges
- **QUICKSTART.md** - 5-minute setup guide
- **PROJECT_OVERVIEW.md** - Architecture details
- **CUSTOMIZATION.md** - Advanced customization

## License

This is a demonstration project for PDF form filling.
