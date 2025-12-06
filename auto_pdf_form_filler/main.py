"""Main entry point for auto PDF form filler."""
import sys
import json
import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from typing import Dict, List, Tuple

from autofill import (
    extract_text_blocks,
    find_all_labels,
    detect_horizontal_lines,
    compute_fill_position,
    draw_text_overlay,
    merge_overlay
)


def process_pdf_page(image: Image.Image, field_values: Dict) -> Tuple[Dict[str, Tuple[int, int]], List]:
    """
    Process a single PDF page to detect fields and compute positions.
    
    Args:
        image: PIL Image of the PDF page
        field_values: Dictionary of field values to fill
    
    Returns:
        Tuple of (detected_fields dict, debug_info list)
    """
    print(f"  Extracting text blocks...")
    text_blocks = extract_text_blocks(image, min_confidence=30)
    print(f"  Found {len(text_blocks)} text blocks")
    
    print(f"  Detecting horizontal lines...")
    lines = detect_horizontal_lines(image, min_line_length=50)
    print(f"  Found {len(lines)} horizontal lines")
    
    print(f"  Matching labels...")
    label_keys = list(field_values.keys())
    label_matches = find_all_labels(text_blocks, label_keys)
    print(f"  Matched {len(label_matches)} labels")
    
    # Compute fill positions
    detected_fields = {}
    debug_info = []
    
    for label_key, label_match in label_matches.items():
        position = compute_fill_position(label_match, lines)
        if position:
            detected_fields[label_key] = position
            debug_info.append({
                'field': label_key,
                'label_text': label_match.block.text,
                'label_bbox': tuple(int(x) for x in label_match.block.bbox),
                'fill_position': tuple(int(x) for x in position),
                'similarity': float(label_match.similarity)
            })
            print(f"    {label_key}: '{label_match.block.text}' -> {position}")
        else:
            print(f"    {label_key}: No suitable position found")
    
    return detected_fields, debug_info


def main():
    """Main execution function."""
    if len(sys.argv) != 4:
        print("Usage: python main.py <input_json> <template_pdf> <output_pdf>")
        print("Example: python main.py samples/input.json samples/request_for_repair.pdf output/filled.pdf")
        sys.exit(1)
    
    input_json_path = sys.argv[1]
    template_pdf_path = sys.argv[2]
    output_pdf_path = sys.argv[3]
    
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
        field_values = json.load(f)
    
    print(f"Converting PDF to images...")
    images = convert_from_path(template_pdf_path, dpi=300)
    print(f"Converted {len(images)} pages")
    
    # Process each page
    overlay_pdfs = []
    all_debug_info = []
    
    for page_idx, image in enumerate(images):
        print(f"\nProcessing page {page_idx + 1}/{len(images)}...")
        
        detected_fields, debug_info = process_pdf_page(image, field_values)
        all_debug_info.extend(debug_info)
        
        # Generate overlay for this page
        if detected_fields:
            print(f"  Generating overlay...")
            overlay_bytes = draw_text_overlay(
                page_idx,
                detected_fields,
                field_values,
                image.width,
                image.height
            )
            overlay_pdfs.append(overlay_bytes)
        else:
            print(f"  No fields detected on this page")
            overlay_pdfs.append(None)
    
    # Merge overlays with template
    print(f"\nMerging overlays with template...")
    merge_overlay(template_pdf_path, overlay_pdfs, output_pdf_path)
    
    print(f"\n✓ Successfully created: {output_pdf_path}")
    print(f"  Total fields filled: {len([d for d in all_debug_info if d])}")
    
    # Save debug info
    debug_output_path = output_dir / "debug_info.json"
    with open(debug_output_path, 'w') as f:
        json.dump(all_debug_info, f, indent=2)
    print(f"  Debug info saved to: {debug_output_path}")


if __name__ == "__main__":
    main()
