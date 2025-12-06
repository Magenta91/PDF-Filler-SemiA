"""PDF overlay rendering using ReportLab."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from typing import Dict, Tuple, List
import io


class FieldPlacement:
    """Represents a field to be rendered at a specific position."""
    
    def __init__(self, x: int, y: int, text: str, font_size: int = 10, bold: bool = False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.bold = bold
    
    def __repr__(self):
        return f"FieldPlacement({self.x}, {self.y}, '{self.text}')"


def create_overlay_pdf(placements: List[FieldPlacement], 
                      page_width: int, page_height: int,
                      dpi: int = 300,
                      output_path: str = None) -> bytes:
    """
    Create a transparent PDF overlay with text at specified positions.
    
    Args:
        placements: List of FieldPlacement objects
        page_width: Width of the page in pixels
        page_height: Height of the page in pixels
        dpi: DPI of the source image (default 300)
        output_path: Optional path to save PDF file
    
    Returns:
        PDF bytes
    """
    # Convert pixel dimensions to points (72 DPI is PDF standard)
    scale_factor = 72.0 / dpi
    pdf_width = page_width * scale_factor
    pdf_height = page_height * scale_factor
    
    # Create PDF in memory or file
    if output_path:
        pdf_canvas = canvas.Canvas(output_path, pagesize=(pdf_width, pdf_height))
    else:
        buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=(pdf_width, pdf_height))
    
    # Set font
    pdf_canvas.setFont("Helvetica", 10)
    
    # Draw each field
    for placement in placements:
        font_name = "Helvetica-Bold" if placement.bold else "Helvetica"
        pdf_canvas.setFont(font_name, placement.font_size)
        # Convert from image coordinates (pixels, top-left origin) to PDF coordinates (points, bottom-left origin)
        pdf_x = placement.x * scale_factor
        pdf_y = pdf_height - (placement.y * scale_factor)
        pdf_canvas.drawString(pdf_x, pdf_y, placement.text)
    
    pdf_canvas.save()
    
    if output_path:
        return None
    else:
        buffer.seek(0)
        return buffer.read()


def draw_text_overlay(page_idx: int, detected_fields: Dict[str, Tuple[int, int]], 
                     field_values: Dict[str, any],
                     page_width: int, page_height: int,
                     dpi: int = 300,
                     output_path: str = None) -> bytes:
    """
    Generate overlay PDF for a single page with detected fields.
    
    Args:
        page_idx: Page index (0-based)
        detected_fields: Dict mapping field keys to (x, y) positions
        field_values: Dict mapping field keys to their values
        page_width: Page width in pixels
        page_height: Page height in pixels
        dpi: DPI of the source image (default 300)
        output_path: Optional path to save overlay PDF
    
    Returns:
        PDF bytes
    """
    placements = []
    
    for field_key, position in detected_fields.items():
        if field_key in field_values:
            value = field_values[field_key]
            x, y = position
            
            # Handle different value types
            if isinstance(value, list):
                # Multi-line field (e.g., repairs)
                for i, item in enumerate(value):
                    placements.append(FieldPlacement(x, y + (i * 40), f"• {item}", 8))
            else:
                # Single-line field
                text_value = format_field_value(field_key, value)
                placements.append(FieldPlacement(x, y, text_value, 10))
    
    return create_overlay_pdf(placements, page_width, page_height, dpi, output_path)


def format_field_value(field_key: str, value: any) -> str:
    """
    Format field value based on field type.
    
    Args:
        field_key: Key identifying the field
        value: Raw value to format
    
    Returns:
        Formatted string
    """
    if value is None:
        return ""
    
    # Date fields
    if 'date' in field_key.lower():
        return str(value)
    
    # Initials - uppercase
    if 'initial' in field_key.lower():
        return str(value).upper()
    
    # Signature - title case
    if 'signature' in field_key.lower() and 'name' in field_key.lower():
        return str(value).title()
    
    # Default
    return str(value)
