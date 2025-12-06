"""Debug script to test overlay generation separately."""
import json
from pdf2image import convert_from_path
from autofill import (
    extract_text_blocks,
    find_all_labels,
    detect_horizontal_lines,
    compute_fill_position,
    draw_text_overlay
)

# Load data
with open('samples/input.json', 'r') as f:
    field_values = json.load(f)

# Convert first page
images = convert_from_path('samples/request_for_repair.pdf', dpi=300)
image = images[0]

print(f"Image size: {image.width} x {image.height}")

# Extract and detect
text_blocks = extract_text_blocks(image, min_confidence=30)
lines = detect_horizontal_lines(image, min_line_length=50)
label_matches = find_all_labels(text_blocks, list(field_values.keys()))

print(f"\nDetected fields:")
detected_fields = {}
for label_key, label_match in label_matches.items():
    position = compute_fill_position(label_match, lines)
    if position:
        detected_fields[label_key] = position
        print(f"  {label_key}: {position}")

# Generate standalone overlay
print(f"\nGenerating standalone overlay...")
overlay_bytes = draw_text_overlay(
    0,
    detected_fields,
    field_values,
    image.width,
    image.height,
    dpi=300,
    output_path='output/debug_overlay_page1.pdf'
)

print("✓ Overlay saved to: output/debug_overlay_page1.pdf")
print("\nField values being written:")
for key, value in field_values.items():
    if key in detected_fields:
        print(f"  {key}: '{value}'")
