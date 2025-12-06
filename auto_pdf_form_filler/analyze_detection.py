"""Analyze the detection results vs correct coordinates."""
import json
from pdf2image import convert_from_path
from autofill import extract_text_blocks, find_all_labels, detect_horizontal_lines, compute_fill_position

# Correct coordinates (in PDF points, 72 DPI)
correct_coords = {
    "date_prepared": [
        {"page": 1, "x": 102, "y": 689},
        {"page": 1, "x": 300, "y": 590},
        {"page": 2, "x": 480, "y": 726},
        {"page": 2, "x": 480, "y": 709}
    ],
    "agreement_date": [{"page": 1, "x": 63, "y": 657}],
    "property_address": [{"page": 1, "x": 227, "y": 657}],
    "buyer_name": [
        {"page": 1, "x": 100, "y": 647},
        {"page": 2, "x": 80, "y": 726},
        {"page": 2, "x": 80, "y": 709}
    ],
    "seller_name": [{"page": 1, "x": 155, "y": 635}],
    "repairs_start": {"page": 1, "x": 85, "y": 579},
    "buyer_initials": [{"page": 1, "x": 359, "y": 70}],
    "seller_initials": [{"page": 1, "x": 500, "y": 70}]
}

# Load data
with open('samples/input.json', 'r') as f:
    field_values = json.load(f)

# Convert PDF
images = convert_from_path('samples/request_for_repair.pdf', dpi=300)

print("=" * 80)
print("DETECTION ANALYSIS")
print("=" * 80)

for page_idx, image in enumerate(images[:1]):  # Just analyze page 1
    print(f"\nPAGE {page_idx + 1}")
    print(f"Image size: {image.width} x {image.height} pixels @ 300 DPI")
    
    # Convert to PDF dimensions
    scale = 72.0 / 300.0
    pdf_width = image.width * scale
    pdf_height = image.height * scale
    print(f"PDF size: {pdf_width:.1f} x {pdf_height:.1f} points")
    
    # Extract
    text_blocks = extract_text_blocks(image, min_confidence=30)
    lines = detect_horizontal_lines(image, min_line_length=50)
    label_matches = find_all_labels(text_blocks, list(field_values.keys()))
    
    print(f"\nDETECTED LABELS:")
    for label_key, label_match in label_matches.items():
        position = compute_fill_position(label_match, lines)
        
        # Convert detected position to PDF points
        if position:
            pdf_x = position[0] * scale
            pdf_y = pdf_height - (position[1] * scale)
            
            print(f"\n  {label_key}:")
            print(f"    Label text: '{label_match.block.text}'")
            print(f"    Label bbox (pixels): {label_match.block.bbox}")
            print(f"    Detected position (pixels): {position}")
            print(f"    Detected position (PDF points): ({pdf_x:.1f}, {pdf_y:.1f})")
            
            # Compare with correct
            if label_key in correct_coords:
                correct = correct_coords[label_key]
                if isinstance(correct, list):
                    correct = correct[0]  # First occurrence
                if isinstance(correct, dict) and 'page' in correct:
                    print(f"    Correct position (PDF points): ({correct['x']}, {correct['y']})")
                    print(f"    Difference: Δx={pdf_x - correct['x']:.1f}, Δy={pdf_y - correct['y']:.1f}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
