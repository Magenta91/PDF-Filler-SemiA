# Customization Guide

## Adding Support for New Form Types

### Step 1: Identify Form Labels

Look at your PDF form and identify the text labels for fields you want to fill. For example:
- "Applicant Name:"
- "Date of Birth:"
- "Social Security Number:"

### Step 2: Add Label Patterns

Edit `autofill/detector.py` and add your patterns to `LABEL_PATTERNS`:

```python
LABEL_PATTERNS = {
    # Existing patterns...
    
    # Your new patterns
    'applicant_name': ['applicant name', 'applicant', 'name of applicant'],
    'date_of_birth': ['date of birth', 'dob', 'birth date', 'birthdate'],
    'ssn': ['social security', 'ssn', 'social security number', 'ss#'],
}
```

### Step 3: Create Input JSON

Create a JSON file with your data:

```json
{
  "applicant_name": "John Smith",
  "date_of_birth": "01/15/1985",
  "ssn": "XXX-XX-1234"
}
```

### Step 4: Run the Filler

```bash
python main.py your_data.json your_form.pdf output/filled.pdf
```

## Adjusting Detection Parameters

### OCR Confidence Threshold

In `autofill/ocr.py`, adjust `min_confidence`:

```python
# More lenient (may include false positives)
text_blocks = extract_text_blocks(image, min_confidence=20)

# More strict (may miss some text)
text_blocks = extract_text_blocks(image, min_confidence=50)
```

### Line Detection Sensitivity

In `autofill/layout.py`, adjust line detection parameters:

```python
# Detect shorter lines
lines = detect_horizontal_lines(image, min_line_length=30)

# Only detect longer lines
lines = detect_horizontal_lines(image, min_line_length=100)

# Allow more gaps in lines
lines = detect_horizontal_lines(image, min_line_length=50, max_line_gap=20)
```

### Search Distance

Adjust how far to search for lines:

```python
# In layout.py, find_nearest_line_below()
line = find_nearest_line_below(label_block, lines, max_distance=150)

# In layout.py, find_nearest_line_right()
line = find_nearest_line_right(label_block, lines, max_distance=300)
```

### Fuzzy Matching Threshold

In `autofill/detector.py`, adjust similarity threshold:

```python
# More lenient matching
matches = find_label_blocks(blocks, target_label, similarity_threshold=0.5)

# Stricter matching
matches = find_label_blocks(blocks, target_label, similarity_threshold=0.8)
```

## Custom Rendering

### Font and Size

In `autofill/renderer.py`, customize text appearance:

```python
# Change default font size
placements.append(FieldPlacement(x, y, str(value), 12))  # Larger

# Use different font
pdf_canvas.setFont("Helvetica-Bold", 10)
pdf_canvas.setFont("Times-Roman", 10)
```

### Text Color

```python
# In renderer.py, create_overlay_pdf()
pdf_canvas.setFillColorRGB(0, 0, 0)  # Black (default)
pdf_canvas.setFillColorRGB(0, 0, 1)  # Blue
pdf_canvas.setFillColorRGB(1, 0, 0)  # Red
```

### Multi-line Spacing

```python
# In renderer.py, draw_text_overlay()
for i, item in enumerate(value):
    # Adjust spacing between lines (default: 15)
    placements.append(FieldPlacement(x, y + (i * 20), f"• {item}", 9))
```

## Image Quality

### DPI Settings

In `main.py`, adjust image resolution:

```python
# Higher quality (slower, more accurate)
images = convert_from_path(template_pdf_path, dpi=400)

# Lower quality (faster, less accurate)
images = convert_from_path(template_pdf_path, dpi=200)
```

## Advanced: Custom Field Types

### Adding Checkbox Support

```python
# In renderer.py
class CheckboxPlacement:
    def __init__(self, x: int, y: int, checked: bool):
        self.x = x
        self.y = y
        self.checked = checked

def draw_checkbox(pdf_canvas, placement):
    if placement.checked:
        pdf_canvas.drawString(placement.x, placement.y, "☑")
    else:
        pdf_canvas.drawString(placement.x, placement.y, "☐")
```

### Adding Signature Images

```python
# In renderer.py
from reportlab.lib.utils import ImageReader

def draw_signature(pdf_canvas, x, y, signature_path):
    img = ImageReader(signature_path)
    pdf_canvas.drawImage(img, x, y, width=100, height=30, mask='auto')
```

## Debugging

### Enable Verbose Output

Add debug prints in `main.py`:

```python
# After OCR
for block in text_blocks[:10]:  # Show first 10 blocks
    print(f"  Block: '{block.text}' at {block.bbox}")

# After line detection
for line in lines[:10]:  # Show first 10 lines
    print(f"  Line: {line}")
```

### Visualize Detection

```python
# In main.py, add visualization
import cv2
import numpy as np

def visualize_detection(image, text_blocks, lines):
    img_array = np.array(image)
    
    # Draw text blocks
    for block in text_blocks:
        cv2.rectangle(img_array, 
                     (block.x, block.y),
                     (block.x + block.w, block.y + block.h),
                     (0, 255, 0), 2)
    
    # Draw lines
    for line in lines:
        cv2.line(img_array, (line.x1, line.y1), (line.x2, line.y2), (255, 0, 0), 2)
    
    cv2.imwrite('debug_visualization.png', img_array)
```

### Save Intermediate Results

```python
# In main.py
# Save OCR results
with open('debug_ocr.json', 'w') as f:
    json.dump([{'text': b.text, 'bbox': b.bbox} for b in text_blocks], f, indent=2)

# Save detected lines
with open('debug_lines.json', 'w') as f:
    json.dump([{'x1': l.x1, 'y1': l.y1, 'x2': l.x2, 'y2': l.y2} for l in lines], f, indent=2)
```

## Performance Optimization

### Parallel Processing

```python
# In main.py
from concurrent.futures import ProcessPoolExecutor

def process_page_wrapper(args):
    return process_pdf_page(*args)

with ProcessPoolExecutor() as executor:
    results = executor.map(process_page_wrapper, 
                          [(img, field_values) for img in images])
```

### Caching OCR Results

```python
import pickle

# Save OCR results
with open('ocr_cache.pkl', 'wb') as f:
    pickle.dump(text_blocks, f)

# Load cached results
with open('ocr_cache.pkl', 'rb') as f:
    text_blocks = pickle.load(f)
```

## Example: Custom Form Type

Here's a complete example for a job application form:

```python
# 1. Add to detector.py
LABEL_PATTERNS = {
    'full_name': ['full name', 'name', 'applicant name'],
    'email': ['email', 'e-mail', 'email address'],
    'phone': ['phone', 'telephone', 'phone number', 'contact number'],
    'position': ['position', 'job title', 'applying for'],
    'experience': ['years of experience', 'experience', 'work experience'],
}

# 2. Create input JSON
{
  "full_name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "(555) 123-4567",
  "position": "Software Engineer",
  "experience": "5 years"
}

# 3. Run
python main.py job_data.json job_application.pdf output/filled_application.pdf
```
