"""Advanced form understanding using visual analysis."""
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Optional
from .ocr import TextBlock


def detect_form_fields_visual(image: Image.Image) -> List[Tuple[int, int, int, int]]:
    """
    Detect form fields using visual analysis (underlines, boxes, etc.).
    
    Args:
        image: PIL Image object
    
    Returns:
        List of (x, y, width, height) tuples for detected fields
    """
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Detect horizontal lines (underlines)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Find contours of horizontal lines
    _, thresh = cv2.threshold(detect_horizontal, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    fields = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter for reasonable field sizes (underlines are typically wide and thin)
        if w > 50 and h < 20:
            # The field is above the underline
            fields.append((x, y - 20, w, 25))
    
    return fields


def match_labels_to_fields(text_blocks: List[TextBlock], 
                           fields: List[Tuple[int, int, int, int]],
                           label_patterns: Dict[str, List[str]]) -> Dict[str, Tuple[int, int]]:
    """
    Match detected labels to nearby form fields.
    
    Args:
        text_blocks: List of TextBlock objects from OCR
        fields: List of detected field regions (x, y, w, h)
        label_patterns: Dictionary of label patterns to match
    
    Returns:
        Dictionary mapping label keys to (x, y) fill positions
    """
    from .detector import normalize_text, LABEL_PATTERNS
    from Levenshtein import ratio as levenshtein_ratio
    
    if not label_patterns:
        label_patterns = LABEL_PATTERNS
    
    matches = {}
    
    for label_key, patterns in label_patterns.items():
        best_match = None
        best_score = 0
        
        # Find text blocks that match this label
        for block in text_blocks:
            normalized_text = normalize_text(block.text)
            
            for pattern in patterns:
                normalized_pattern = normalize_text(pattern)
                similarity = levenshtein_ratio(normalized_text, normalized_pattern)
                
                if normalized_pattern in normalized_text or normalized_text in normalized_pattern:
                    similarity = max(similarity, 0.8)
                
                if similarity > best_score and similarity >= 0.6:
                    best_score = similarity
                    best_match = block
        
        if best_match:
            # Find nearest field to this label
            nearest_field = find_nearest_field_to_label(best_match, fields)
            if nearest_field:
                x, y, w, h = nearest_field
                # Position text at start of field, slightly above bottom
                matches[label_key] = (x + 5, y + h - 8)
    
    return matches


def find_nearest_field_to_label(label: TextBlock, 
                               fields: List[Tuple[int, int, int, int]],
                               max_distance: int = 200) -> Optional[Tuple[int, int, int, int]]:
    """
    Find the nearest form field to a label.
    
    Args:
        label: TextBlock representing the label
        fields: List of field regions (x, y, w, h)
        max_distance: Maximum distance to search
    
    Returns:
        Nearest field tuple or None
    """
    label_right = label.x + label.w
    label_center_y = label.center_y
    
    candidates = []
    
    for field in fields:
        fx, fy, fw, fh = field
        field_center_y = fy + fh / 2
        
        # Check if field is to the right and roughly on same line
        if fx > label_right and abs(field_center_y - label_center_y) < 30:
            distance = fx - label_right
            if distance <= max_distance:
                candidates.append((distance, field))
        
        # Also check if field is below the label
        elif fy > label.y + label.h and abs(fx - label.x) < 100:
            distance = fy - (label.y + label.h)
            if distance <= max_distance:
                candidates.append((distance, field))
    
    if not candidates:
        return None
    
    # Return closest field
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def analyze_form_structure(image: Image.Image, text_blocks: List[TextBlock]) -> Dict:
    """
    Analyze overall form structure to understand layout.
    
    Args:
        image: PIL Image object
        text_blocks: List of TextBlock objects
    
    Returns:
        Dictionary with form structure information
    """
    # Detect columns by clustering x-coordinates
    x_coords = [block.x for block in text_blocks]
    
    # Simple column detection: find gaps in x-coordinates
    x_sorted = sorted(set(x_coords))
    columns = []
    current_column = [x_sorted[0]]
    
    for x in x_sorted[1:]:
        if x - current_column[-1] > 100:  # Gap indicates new column
            columns.append(current_column)
            current_column = [x]
        else:
            current_column.append(x)
    
    if current_column:
        columns.append(current_column)
    
    # Detect rows by clustering y-coordinates
    y_coords = [block.y for block in text_blocks]
    y_sorted = sorted(set(y_coords))
    rows = []
    current_row = [y_sorted[0]]
    
    for y in y_sorted[1:]:
        if y - current_row[-1] > 30:  # Gap indicates new row
            rows.append(current_row)
            current_row = [y]
        else:
            current_row.append(y)
    
    if current_row:
        rows.append(current_row)
    
    return {
        'num_columns': len(columns),
        'num_rows': len(rows),
        'columns': columns,
        'rows': rows
    }
