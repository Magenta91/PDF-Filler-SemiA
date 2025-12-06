# Auto PDF Form Filler - Project Overview

## Architecture

This project implements an intelligent PDF form filling system that automatically detects form fields without manual coordinate specification.

### Pipeline Flow

```
Input PDF + JSON Data
        ↓
[1] PDF → High-Res Images (300 DPI)
        ↓
[2] OCR Text Extraction (Tesseract)
        ↓
[3] Label Detection (Fuzzy Matching)
        ↓
[4] Line Detection (OpenCV)
        ↓
[5] Coordinate Computation
        ↓
[6] Overlay Generation (ReportLab)
        ↓
[7] PDF Merge (PyPDF)
        ↓
Output: Filled PDF
```

## Module Breakdown

### autofill/ocr.py
- Extracts text blocks with bounding boxes using Tesseract
- Groups text blocks by horizontal lines
- Returns structured TextBlock objects with spatial information

### autofill/detector.py
- Implements fuzzy label matching using Levenshtein distance
- Maintains dictionary of common form field patterns
- Handles label variations ("Date:" vs "Date Prepared:")
- Returns LabelMatch objects with similarity scores

### autofill/layout.py
- Detects horizontal lines using OpenCV Canny edge detection
- Finds nearest line below or to the right of labels
- Computes optimal fill positions based on spatial relationships
- Returns Line objects and coordinate tuples

### autofill/renderer.py
- Creates transparent PDF overlays using ReportLab
- Handles multi-line fields (lists)
- Formats values based on field type (dates, initials, signatures)
- Converts image coordinates to PDF coordinates

### autofill/merger.py
- Merges overlay PDFs with original template
- Supports multi-page documents
- Uses PyPDF for PDF manipulation

### main.py
- Orchestrates the entire pipeline
- Processes each page independently
- Generates debug information
- Command-line interface

## Key Algorithms

### Label Detection
Uses fuzzy string matching with multiple strategies:
1. Levenshtein distance for similarity scoring
2. Substring matching for partial matches
3. Pattern library for common variations
4. Confidence threshold filtering

### Line Detection
OpenCV-based approach:
1. Convert to grayscale
2. Apply Canny edge detection
3. Hough line transform
4. Filter for horizontal lines (aspect ratio)
5. Spatial proximity search

### Coordinate Computation
Heuristic-based positioning:
1. Prefer line to the right (inline fields)
2. Fallback to line below (multi-line fields)
3. Fallback to right of label (no lines)
4. Offset adjustments for visual alignment

## Extensibility Points

### Adding New Form Types
1. Add label patterns to `LABEL_PATTERNS` in `detector.py`
2. Adjust line detection thresholds in `layout.py`
3. Customize rendering styles in `renderer.py`

### Improving Detection
1. Train custom LayoutParser models
2. Add preprocessing (deskew, denoise)
3. Implement checkbox/radio detection
4. Add field validation logic

### Performance Optimization
1. Cache OCR results
2. Parallel page processing
3. Adaptive DPI selection
4. Region-of-interest detection

## Testing Strategy

### Unit Tests
- OCR text extraction accuracy
- Label matching precision/recall
- Line detection robustness
- Coordinate computation correctness

### Integration Tests
- End-to-end pipeline on sample forms
- Multi-page document handling
- Edge cases (rotated, skewed, low quality)

### Validation
- Visual inspection of filled forms
- Coordinate accuracy metrics
- Field detection coverage

## Known Limitations

1. **Handwritten Forms**: OCR struggles with handwriting
2. **Complex Layouts**: Multi-column forms may need tuning
3. **No Lines**: Forms without underlines are harder to detect
4. **Checkboxes**: Not yet implemented
5. **Scanned Quality**: Requires 300+ DPI for best results

## Future Enhancements

1. **ML-Based Detection**: Train models on form datasets
2. **Template Library**: Reusable patterns for common forms
3. **Interactive Mode**: GUI for manual corrections
4. **Batch Processing**: Process multiple forms at once
5. **Cloud Integration**: API for form filling service
6. **Multi-Language**: Support international forms
7. **Field Validation**: Semantic checks for data types
8. **Adaptive Learning**: Improve detection from user feedback
