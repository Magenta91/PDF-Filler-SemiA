"""Line detection and blank region identification using OpenCV."""
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
from .ocr import TextBlock
from .detector import LabelMatch


class Line:
    """Represents a detected horizontal line."""
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.length = abs(x2 - x1)
        self.center_x = (x1 + x2) / 2
        self.center_y = (y1 + y2) / 2
        self.y = y1  # Approximate y position
    
    def __repr__(self):
        return f"Line(({self.x1}, {self.y1}) -> ({self.x2}, {self.y2}), len={self.length})"


def detect_horizontal_lines(image: Image.Image, 
                           min_line_length: int = 100,
                           max_line_gap: int = 5) -> List[Line]:
    """
    Detect horizontal lines in image using OpenCV.
    
    Args:
        image: PIL Image object
        min_line_length: Minimum length of line to detect
        max_line_gap: Maximum gap between line segments to connect
    
    Returns:
        List of Line objects
    """
    # Convert PIL to OpenCV format
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply edge detection with adjusted thresholds
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect lines using Hough transform with stricter parameters
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=150,
                           minLineLength=min_line_length, maxLineGap=max_line_gap)
    
    horizontal_lines = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Filter for horizontal lines (very small vertical difference)
            if abs(y2 - y1) < 5:  # Nearly horizontal
                # Ensure x1 < x2
                if x1 > x2:
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
                
                horizontal_lines.append(Line(x1, y1, x2, y2))
    
    # Merge nearby lines (within 5 pixels vertically)
    horizontal_lines = merge_nearby_lines(horizontal_lines, y_tolerance=5)
    
    # Sort by y-coordinate
    horizontal_lines.sort(key=lambda l: l.y)
    
    return horizontal_lines


def merge_nearby_lines(lines: List[Line], y_tolerance: int = 5) -> List[Line]:
    """
    Merge lines that are very close to each other vertically.
    
    Args:
        lines: List of Line objects
        y_tolerance: Maximum vertical distance to merge
    
    Returns:
        List of merged Line objects
    """
    if not lines:
        return []
    
    # Sort by y-coordinate
    sorted_lines = sorted(lines, key=lambda l: l.y)
    merged = []
    
    current_group = [sorted_lines[0]]
    
    for line in sorted_lines[1:]:
        # Check if line is close to current group
        if abs(line.y - current_group[0].y) <= y_tolerance:
            current_group.append(line)
        else:
            # Merge current group and start new one
            if current_group:
                # Take the longest line or average position
                longest = max(current_group, key=lambda l: l.length)
                avg_y = int(sum(l.y for l in current_group) / len(current_group))
                merged.append(Line(longest.x1, avg_y, longest.x2, avg_y))
            current_group = [line]
    
    # Merge last group
    if current_group:
        longest = max(current_group, key=lambda l: l.length)
        avg_y = int(sum(l.y for l in current_group) / len(current_group))
        merged.append(Line(longest.x1, avg_y, longest.x2, avg_y))
    
    return merged


def find_nearest_line_below(label_block: TextBlock, lines: List[Line], 
                           max_distance: int = 100) -> Optional[Line]:
    """
    Find the nearest horizontal line below a label block.
    
    Args:
        label_block: TextBlock representing the label
        lines: List of detected Line objects
        max_distance: Maximum vertical distance to search
    
    Returns:
        Nearest Line below the label, or None
    """
    label_bottom = label_block.y + label_block.h
    
    candidates = []
    for line in lines:
        # Line must be below the label
        if line.y > label_bottom:
            distance = line.y - label_bottom
            if distance <= max_distance:
                candidates.append((distance, line))
    
    if not candidates:
        return None
    
    # Return closest line
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def detect_blank_regions(image: Image.Image, min_width: int = 100) -> List[Tuple[int, int, int, int]]:
    """
    Detect blank (white) regions in the image that might be form fields.
    
    Args:
        image: PIL Image object
        min_width: Minimum width of blank region to detect
    
    Returns:
        List of (x, y, width, height) tuples representing blank regions
    """
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Threshold to find white regions
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    blank_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter for reasonable field sizes
        if w >= min_width and 10 <= h <= 100:
            blank_regions.append((x, y, w, h))
    
    return blank_regions


def find_nearest_line_right(label_block: TextBlock, lines: List[Line],
                           max_distance: int = 200,
                           y_tolerance: int = 20) -> Optional[Line]:
    """
    Find the nearest horizontal line to the right of a label block (on same line).
    
    Args:
        label_block: TextBlock representing the label
        lines: List of detected Line objects
        max_distance: Maximum horizontal distance to search
        y_tolerance: Maximum vertical difference to consider "same line"
    
    Returns:
        Nearest Line to the right, or None
    """
    label_right = label_block.x + label_block.w
    label_center_y = label_block.center_y
    
    candidates = []
    for line in lines:
        # Line must be roughly on same horizontal level
        if abs(line.y - label_center_y) <= y_tolerance:
            # Line must be to the right
            if line.x1 > label_right:
                distance = line.x1 - label_right
                if distance <= max_distance:
                    candidates.append((distance, line))
    
    if not candidates:
        return None
    
    # Return closest line
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def compute_fill_position(label_match: LabelMatch, lines: List[Line],
                         prefer_right: bool = True) -> Optional[Tuple[int, int]]:
    """
    Compute the (x, y) position where text should be filled.
    
    Args:
        label_match: LabelMatch object with detected label
        lines: List of detected Line objects
        prefer_right: If True, prefer line to the right; otherwise prefer below
    
    Returns:
        (x, y) tuple for fill position, or None if no suitable line found
    """
    label_block = label_match.block
    label_key = label_match.label_key
    
    # Special handling for initials (usually at bottom of page)
    if 'initial' in label_key.lower():
        # Look for lines near bottom of page
        line = find_nearest_line_right(label_block, lines, max_distance=300, y_tolerance=30)
        if line:
            return (line.x1 + 5, line.y - 8)
    
    # Try to find line to the right first (common for inline fields)
    line = find_nearest_line_right(label_block, lines, max_distance=150, y_tolerance=15)
    if line:
        # Position text slightly above the line, at start of line
        return (line.x1 + 5, line.y - 8)
    
    # Try to find line below (common for multi-line fields)
    line = find_nearest_line_below(label_block, lines, max_distance=50)
    if line:
        # Position text slightly above the line, aligned with label or slightly offset
        x_pos = max(label_block.x, line.x1 + 5)
        return (x_pos, line.y - 8)
    
    # Fallback: position to the right of label
    return (label_block.x + label_block.w + 15, int(label_block.center_y) - 5)
