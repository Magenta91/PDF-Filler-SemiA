"""Test script to check repairs positioning."""
from pdf2image import convert_from_path
from autofill.templates import REQUEST_FOR_REPAIR_TEMPLATE
from autofill.renderer import FieldPlacement, create_overlay_pdf

# Convert PDF
images = convert_from_path('samples/request_for_repair.pdf', dpi=300)
image = images[0]  # Page 1

# Get PDF dimensions
scale = 72.0 / 300.0
pdf_width = image.width * scale
pdf_height = image.height * scale

print(f"Image size: {image.width} x {image.height} pixels")
print(f"PDF size: {pdf_width:.1f} x {pdf_height:.1f} points")

# Get repairs coordinates from template
repairs_data = REQUEST_FOR_REPAIR_TEMPLATE['fields']['repairs']
x, y = repairs_data['x'], repairs_data['y']
line_spacing = repairs_data['line_spacing']

print(f"\nRepairs template coordinates:")
print(f"  x: {x}, y: {y}")
print(f"  line_spacing: {line_spacing}")

# Test repairs
repairs = [
    "Replace broken window in master bedroom",
    "Fix leaking kitchen faucet",
    "Repair garage door opener"
]

placements = []
for i, item in enumerate(repairs):
    pixel_x = x / scale
    pixel_y = (pdf_height - y - (i * line_spacing)) / scale
    placements.append(FieldPlacement(int(pixel_x), int(pixel_y), f"• {item}", 8))
    print(f"\nRepair {i+1}:")
    print(f"  PDF coords: ({x}, {y - (i * line_spacing)})")
    print(f"  Pixel coords: ({int(pixel_x)}, {int(pixel_y)})")
    print(f"  Text: {item}")

# Generate test overlay
print(f"\nGenerating test overlay...")
create_overlay_pdf(placements, image.width, image.height, dpi=300, output_path='output/test_repairs_only.pdf')
print(f"✓ Saved to: output/test_repairs_only.pdf")

# Also test with different coordinates to find the right spot
print(f"\n" + "="*70)
print("Testing alternative positions...")
print("="*70)

# Try different Y positions
test_positions = [
    (85, 579, "Original"),
    (85, 550, "Higher (y=550)"),
    (85, 600, "Lower (y=600)"),
    (100, 579, "Right (x=100)"),
    (70, 579, "Left (x=70)"),
]

for test_x, test_y, label in test_positions:
    placements = []
    for i, item in enumerate(repairs):
        pixel_x = test_x / scale
        pixel_y = (pdf_height - test_y - (i * line_spacing)) / scale
        placements.append(FieldPlacement(int(pixel_x), int(pixel_y), f"• {item}", 8))
    
    output_path = f'output/test_repairs_{label.replace(" ", "_").replace("(", "").replace(")", "").replace("=", "")}.pdf'
    create_overlay_pdf(placements, image.width, image.height, dpi=300, output_path=output_path)
    print(f"✓ {label}: {output_path}")
