"""
Simple form filler - Main entry point for production use.
Uses template-based approach with automatic field derivation.
"""
import sys
import json
import os
from pathlib import Path
from pdf2image import convert_from_path

from autofill import extract_text_blocks, merge_overlay
from autofill.templates import get_template, get_field_positions, detect_template
from autofill.renderer import FieldPlacement, create_overlay_pdf, format_field_value
from autofill.field_processor import process_field_values, validate_required_fields, REQUEST_FOR_REPAIR_REQUIRED


def fill_form(template, field_values, images):
    """Fill form using template coordinates."""
    overlay_pdfs = []
    
    for page_idx, image in enumerate(images):
        page_num = page_idx + 1
        placements = []
        
        # Get PDF dimensions
        scale = 72.0 / 300.0
        pdf_width = image.width * scale
        pdf_height = image.height * scale
        
        # Process each field
        for field_key, value in field_values.items():
            positions = get_field_positions(template, field_key, page_num)
            
            if not positions:
                continue
            
            # Handle repairs specially (multi-line with spacing)
            if field_key == 'repairs' and isinstance(value, list):
                field_data = template['fields'][field_key]
                if field_data['page'] == page_num:
                    x, y = field_data['x'], field_data['y']
                    line_spacing = field_data.get('line_spacing', 11)
                    
                    for i, item in enumerate(value):
                        pixel_x = x / scale
                        pixel_y = (pdf_height - y - (i * line_spacing)) / scale
                        placements.append(FieldPlacement(int(pixel_x), int(pixel_y), f"• {item}", 8))
            else:
                # Regular fields
                text_value = format_field_value(field_key, value)
                for x, y in positions:
                    pixel_x = x / scale
                    pixel_y = (pdf_height - y) / scale
                    placements.append(FieldPlacement(int(pixel_x), int(pixel_y), text_value, 10))
        
        # Generate overlay
        if placements:
            overlay_bytes = create_overlay_pdf(placements, image.width, image.height, dpi=300)
            overlay_pdfs.append(overlay_bytes)
        else:
            overlay_pdfs.append(None)
    
    return overlay_pdfs


def main():
    """Main execution function."""
    if len(sys.argv) < 4:
        print("Usage: python fill_form.py <input_json> <template_pdf> <output_pdf> [template_name]")
        print("\nExample:")
        print("  python fill_form.py data.json form.pdf output.pdf")
        print("  python fill_form.py data.json form.pdf output.pdf request_for_repair")
        print("\nInput JSON format:")
        print("  {")
        print('    "date_prepared": "2025-12-06",')
        print('    "agreement_date": "2025-11-15",')
        print('    "property_address": "123 Main St, LA, CA 90001",')
        print('    "buyer_name": "John Doe",')
        print('    "seller_name": "Jane Smith",')
        print('    "repairs": ["Fix window", "Fix door"]')
        print("  }")
        print("\nNote: Initials and signature fields are auto-generated from names.")
        print("      Dates are auto-converted from ISO format to MM/DD/YYYY.")
        sys.exit(1)
    
    input_json_path = sys.argv[1]
    template_pdf_path = sys.argv[2]
    output_pdf_path = sys.argv[3]
    template_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Validate inputs
    if not os.path.exists(input_json_path):
        print(f"❌ Error: Input JSON not found: {input_json_path}")
        sys.exit(1)
    
    if not os.path.exists(template_pdf_path):
        print(f"❌ Error: Template PDF not found: {template_pdf_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(output_pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("PDF Form Filler")
    print("=" * 70)
    
    # Load and process field values
    print(f"\n📄 Loading: {input_json_path}")
    with open(input_json_path, 'r') as f:
        raw_values = json.load(f)
    
    print(f"✓ Processing field values...")
    field_values = process_field_values(raw_values)
    
    # Show derived fields
    derived = []
    for key in ['buyer_initials', 'seller_initials', 'buyer_signature_name', 'signature_date']:
        if key in field_values and key not in raw_values:
            derived.append(f"{key}: {field_values[key]}")
    
    if derived:
        print(f"✓ Auto-generated fields:")
        for item in derived:
            print(f"  • {item}")
    
    # Validate
    is_valid, missing = validate_required_fields(field_values, REQUEST_FOR_REPAIR_REQUIRED)
    if not is_valid:
        print(f"⚠️  Warning: Missing required fields: {', '.join(missing)}")
    
    # Convert PDF
    print(f"\n📄 Converting PDF to images...")
    images = convert_from_path(template_pdf_path, dpi=300)
    print(f"✓ Converted {len(images)} page(s)")
    
    # Detect or use specified template
    if not template_name:
        print(f"\n🔍 Detecting form template...")
        text_blocks = extract_text_blocks(images[0], min_confidence=30)
        template_name = detect_template(text_blocks)
        if template_name:
            print(f"✓ Detected: {template_name}")
        else:
            print(f"❌ Could not detect template")
            print(f"   Available templates: request_for_repair")
            print(f"   Specify template name as 4th argument")
            sys.exit(1)
    
    # Get template
    template = get_template(template_name)
    if not template:
        print(f"❌ Error: Template '{template_name}' not found")
        print(f"   Available templates: request_for_repair")
        sys.exit(1)
    
    print(f"✓ Using template: {template['name']}")
    
    # Fill form
    print(f"\n✍️  Filling form...")
    overlay_pdfs = fill_form(template, field_values, images)
    
    # Count filled fields
    filled_count = sum(1 for v in field_values.values() if v)
    print(f"✓ Filled {filled_count} field(s)")
    
    # Merge
    print(f"\n🔗 Merging with original PDF...")
    merge_overlay(template_pdf_path, overlay_pdfs, output_pdf_path)
    
    print(f"\n" + "=" * 70)
    print(f"✅ Success!")
    print(f"   Output: {output_pdf_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
