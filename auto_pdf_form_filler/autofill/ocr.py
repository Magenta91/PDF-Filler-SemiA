"""OCR text extraction with bounding boxes."""
import pytesseract
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple


class TextBlock:
    """Represents a detected text block with spatial information."""
    
    def __init__(self, text: str, bbox: Tuple[int, int, int, int], confidence: float):
        self.text = text.strip()
        self.bbox = bbox  # (x, y, width, height)
        self.confidence = confidence
        self.x, self.y, self.w, self.h = bbox
        self.center_x = self.x + self.w / 2
        self.center_y = self.y + self.h / 2
    
    def __repr__(self):
        return f"TextBlock('{self.text}', bbox={self.bbox}, conf={self.confidence:.2f})"


def extract_text_blocks(image: Image.Image, min_confidence: float = 30) -> List[TextBlock]:
    """
    Extract text blocks from image using Tesseract OCR.
    
    Args:
        image: PIL Image object
        min_confidence: Minimum confidence threshold (0-100)
    
    Returns:
        List of TextBlock objects
    """
    # Convert to numpy array for pytesseract
    img_array = np.array(image)
    
    # Get detailed OCR data
    ocr_data = pytesseract.image_to_data(img_array, output_type=pytesseract.Output.DICT)
    
    blocks = []
    n_boxes = len(ocr_data['text'])
    
    for i in range(n_boxes):
        text = ocr_data['text'][i]
        conf = float(ocr_data['conf'][i])
        
        # Filter out empty text and low confidence
        if text.strip() and conf >= min_confidence:
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            
            blocks.append(TextBlock(text, (x, y, w, h), conf))
    
    return blocks


def group_text_blocks_by_line(blocks: List[TextBlock], y_tolerance: int = 10) -> List[List[TextBlock]]:
    """
    Group text blocks that appear on the same horizontal line.
    
    Args:
        blocks: List of TextBlock objects
        y_tolerance: Maximum vertical distance to consider blocks on same line
    
    Returns:
        List of lists, where each inner list contains blocks on the same line
    """
    if not blocks:
        return []
    
    # Sort by y-coordinate
    sorted_blocks = sorted(blocks, key=lambda b: b.y)
    
    lines = []
    current_line = [sorted_blocks[0]]
    
    for block in sorted_blocks[1:]:
        # Check if block is on same line as current line
        if abs(block.y - current_line[0].y) <= y_tolerance:
            current_line.append(block)
        else:
            # Sort current line by x-coordinate and start new line
            current_line.sort(key=lambda b: b.x)
            lines.append(current_line)
            current_line = [block]
    
    # Add last line
    if current_line:
        current_line.sort(key=lambda b: b.x)
        lines.append(current_line)
    
    return lines


def merge_line_text(line_blocks: List[TextBlock]) -> str:
    """Merge text blocks on same line into single string."""
    return ' '.join(block.text for block in line_blocks)
