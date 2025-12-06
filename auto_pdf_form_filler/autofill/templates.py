"""Form template definitions with known coordinates."""
from typing import Dict, List, Tuple, Optional

# Template for California Request for Repair form
REQUEST_FOR_REPAIR_TEMPLATE = {
    "name": "California Request for Repair",
    "pages": 2,
    "dpi": 72,  # Coordinates are in PDF points
    "fields": {
        "date_prepared": [
            {"page": 1, "x": 102, "y": 689},
            {"page": 1, "x": 300, "y": 590},
            {"page": 2, "x": 480, "y": 726},
            {"page": 2, "x": 480, "y": 709}
        ],
        "agreement_date": [
            {"page": 1, "x": 63, "y": 657}
        ],
        "property_address": [
            {"page": 1, "x": 227, "y": 657}
        ],
        "buyer_name": [
            {"page": 1, "x": 100, "y": 647},
            {"page": 2, "x": 80, "y": 726},
            {"page": 2, "x": 80, "y": 709}
        ],
        "seller_name": [
            {"page": 1, "x": 155, "y": 635}
        ],
        "repairs": {
            "page": 1,
            "x": 85,
            "y": 579,
            "line_spacing": 11
        },
        "buyer_initials": [
            {"page": 1, "x": 359, "y": 70}
        ],
        "seller_initials": [
            {"page": 1, "x": 500, "y": 70}
        ]
    }
}

# Template registry
TEMPLATES = {
    "request_for_repair": REQUEST_FOR_REPAIR_TEMPLATE
}


def get_template(template_name: str) -> Optional[Dict]:
    """Get a template by name."""
    return TEMPLATES.get(template_name)


def get_field_positions(template: Dict, field_key: str, page: int) -> List[Tuple[int, int]]:
    """
    Get all positions for a field on a specific page.
    
    Args:
        template: Template dictionary
        field_key: Field key (e.g., 'buyer_name')
        page: Page number (1-based)
    
    Returns:
        List of (x, y) tuples in PDF points
    """
    if field_key not in template['fields']:
        return []
    
    field_data = template['fields'][field_key]
    positions = []
    
    # Handle list of positions
    if isinstance(field_data, list):
        for pos in field_data:
            if pos['page'] == page:
                positions.append((pos['x'], pos['y']))
    
    # Handle single position with page
    elif isinstance(field_data, dict) and 'page' in field_data:
        if field_data['page'] == page:
            positions.append((field_data['x'], field_data['y']))
    
    return positions


def detect_template(text_blocks, form_name: str = None) -> Optional[str]:
    """
    Detect which template to use based on OCR text.
    
    Args:
        text_blocks: List of TextBlock objects from OCR
        form_name: Optional hint for form name
    
    Returns:
        Template name or None
    """
    # Extract all text
    all_text = ' '.join([block.text.lower() for block in text_blocks])
    
    # Check for Request for Repair indicators
    if 'request for repair' in all_text or 'buyer' in all_text and 'seller' in all_text and 'repairs' in all_text:
        return 'request_for_repair'
    
    return None
