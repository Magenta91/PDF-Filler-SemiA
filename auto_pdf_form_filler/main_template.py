"""Template-based PDF form filler with auto-detection fallback."""
import sys
import json
import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from typing import Dict, List, Tuple

from autofill import (
    extract_text_blocks,
    merge_overlay
)
from autofill.templates import get_template, get_field_positions, detect_template
from autofill.renderer import FieldPlacement, create_overlay_pdf, format_field_value
from autofill.field_processor import process_field_values, validate_required_fields, REQUEST_FOR_REPAIR_REQUIRED


def fill_using_template(template: Dict, field_values: Dict, images: List[Image.Image]) -> List[bytes]:
    """
    Fill form using template coordinates.
    
    Args:
        template: Template dictionary with field positions
        field_values: Dictionary of values to fill
        images: List of PIL Images (one per page)
    
    Returns:
        List of overlay PDF bytes (one per page)
    """
    overlay_pdfs = []
    
    for page_idx, image in enumerate(images):
        page_num = page_idx + 1
        placements = []
        
        print(f"\nProcessing page {page_num}/{len(images)} using template...")
        
        # Get PDF dimensions
        scale = 72.0 / 300.0  # Assuming 300 DPI images
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
                        # Convert PDF points to pixels for FieldPlacement
                        pixel_x = x / scale
                        pixel_y = (pdf_height - y - (i * line_spacing)) / scale
                        placements.append(FieldPlacement(int(pixel_x), int(pixel_y), f"• {item}", 8))
                    
                    print(f"  {field_key}: {len(value)} items at ({x}, {y})")
            else:
                # Regular fields - place at each position
                text_value = format_field_value(field_key, value)
                for x, y in positions:
                    # Convert PDF points to pixels for FieldPlacement
                    pixel_x = x / scale
                    pixel_y = (pdf_height - y) / scale
                    placements.append(FieldPlacement(int(pixel_x), int(pixel_y), text_value, 10))
                    print(f"  {field_key}: '{text_value}' at ({x}, {y})")
        
        # Generate overlay for this page
        if placements:
            overlay_bytes = create_overlay_pdf(placements, image.width, image.height, dpi=300)
            overlay_pdfs.append(overlay_bytes)
        else:
            overlay_pdfs.append(None)
    
    return overlay_pdfs


def main():
    """Main execution function."""
    if len(sys.argv) < 4:
        print("Usage: python main_template.py <input_json> <template_pdf> <output_pdf> [template_name]")
        print("Example: python main_template.py samples/input.json samples/request_for_repair.pdf output/filled.pdf request_for_repair")
        sys.exit(1)
    
    input_json_path = sys.argv[1]
    template_pdf_path = sys.argv[2]
    output_pdf_path = sys.argv[3]
    template_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Validate inputs
    if not os.path.exists(input_json_path):
        print(f"Error: Input JSON not found: {input_json_path}")
        sys.exit(1)
    
    if not os.path.exists(template_pdf_path):
        print(f"Error: Template PDF not found: {template_pdf_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(output_pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load field values
    print(f"Loading field values from {input_json_path}...")
    with open(input_json_path, 'r') as f:
        raw_values = json.load(f)
    
    # Process and enrich field values
    print(f"Processing field values...")
    field_values = process_field_values(raw_values)
    
    # Validate required fields
    is_valid, missing = validate_required_fields(field_values, REQUEST_FOR_REPAIR_REQUIRED)
    if not is_valid:
        print(f"Warning: Missing required fields: {', '.join(missing)}")
    
    # Show derived fields
    print(f"Derived fields:")
    if 'buyer_initials' in field_values and 'buyer_initials' not in raw_values:
        print(f"  buyer_initials: {field_values['buyer_initials']}")
    if 'seller_initials' in field_values and 'seller_initials' not in raw_values:
        print(f"  seller_initials: {field_values['seller_initials']}")
    if 'buyer_signature_name' in field_values and 'buyer_signature_name' not in raw_values:
        print(f"  buyer_signature_name: {field_values['buyer_signature_name']}")
    if 'signature_date' in field_values and 'signature_date' not in raw_values:
        print(f"  signature_date: {field_values['signature_date']}")
    
    print(f"Converting PDF to images...")
    images = convert_from_path(template_pdf_path, dpi=300)
    print(f"Converted {len(images)} pages")
    
    # Detect or use specified template
    if not template_name:
        print(f"\nDetecting form template...")
        text_blocks = extract_text_blocks(images[0], min_confidence=30)
        template_name = detect_template(text_blocks)
        if template_name:
            print(f"  Detected template: {template_name}")
        else:
            print(f"  Could not detect template, using auto-detection")
    
    # Get template
    template = get_template(template_name) if template_name else None
    
    if template:
        print(f"\nUsing template: {template['name']}")
        overlay_pdfs = fill_using_template(template, field_values, images)
    else:
        print(f"\nError: Template '{template_name}' not found")
        print(f"Available templates: {list(get_template.__globals__['TEMPLATES'].keys())}")
        sys.exit(1)
    
    # Merge overlays with template
    print(f"\nMerging overlays with template...")
    merge_overlay(template_pdf_path, overlay_pdfs, output_pdf_path)
    
    print(f"\n✓ Successfully created: {output_pdf_path}")
    print(f"  Template used: {template['name']}")


if __name__ == "__main__":
    main()
