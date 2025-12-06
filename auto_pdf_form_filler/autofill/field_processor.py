"""Field processing and data transformation utilities."""
from datetime import datetime
from typing import Dict, Any


def get_initials(name: str) -> str:
    """
    Extract initials from a full name.
    
    Args:
        name: Full name (e.g., "John Doe")
    
    Returns:
        Initials (e.g., "JD")
    """
    if not name:
        return ""
    
    parts = name.strip().split()
    initials = ''.join([part[0].upper() for part in parts if part])
    return initials


def format_date(date_str: str, output_format: str = "%m/%d/%Y") -> str:
    """
    Convert date from various formats to specified output format.
    
    Args:
        date_str: Date string in various formats (ISO, MM/DD/YYYY, etc.)
        output_format: Desired output format (default: MM/DD/YYYY)
    
    Returns:
        Formatted date string
    """
    if not date_str:
        return ""
    
    # Try various input formats
    input_formats = [
        "%Y-%m-%d",           # ISO format: 2025-12-06
        "%Y-%m-%dT%H:%M:%S",  # ISO with time: 2025-12-06T10:30:00
        "%Y-%m-%dT%H:%M:%SZ", # ISO with timezone: 2025-12-06T10:30:00Z
        "%m/%d/%Y",           # US format: 12/06/2025
        "%d/%m/%Y",           # European format: 06/12/2025
        "%m-%d-%Y",           # US with dashes: 12-06-2025
        "%d-%m-%Y",           # European with dashes: 06-12-2025
    ]
    
    for fmt in input_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime(output_format)
        except ValueError:
            continue
    
    # If no format matches, return original
    return date_str


def process_field_values(raw_values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and enrich field values with derived fields.
    
    Args:
        raw_values: Raw input values from JSON
    
    Returns:
        Processed values with derived fields
    """
    processed = raw_values.copy()
    
    # Format dates to MM/DD/YYYY
    date_fields = ['date_prepared', 'agreement_date', 'signature_date']
    for field in date_fields:
        if field in processed:
            processed[field] = format_date(processed[field])
    
    # Derive buyer initials from buyer name
    if 'buyer_name' in processed and 'buyer_initials' not in processed:
        processed['buyer_initials'] = get_initials(processed['buyer_name'])
    
    # Derive seller initials from seller name
    if 'seller_name' in processed and 'seller_initials' not in processed:
        processed['seller_initials'] = get_initials(processed['seller_name'])
    
    # Derive buyer signature name from buyer name
    if 'buyer_name' in processed and 'buyer_signature_name' not in processed:
        processed['buyer_signature_name'] = processed['buyer_name']
    
    # Derive seller signature name from seller name
    if 'seller_name' in processed and 'seller_signature_name' not in processed:
        processed['seller_signature_name'] = processed['seller_name']
    
    # Use date_prepared as signature_date if not provided
    if 'date_prepared' in processed and 'signature_date' not in processed:
        processed['signature_date'] = processed['date_prepared']
    
    # Use date_prepared as buyer_signature_date if not provided
    if 'date_prepared' in processed and 'buyer_signature_date' not in processed:
        processed['buyer_signature_date'] = processed['date_prepared']
    
    # Use date_prepared as seller_signature_date if not provided
    if 'date_prepared' in processed and 'seller_signature_date' not in processed:
        processed['seller_signature_date'] = processed['date_prepared']
    
    return processed


def validate_required_fields(values: Dict[str, Any], required_fields: list) -> tuple[bool, list]:
    """
    Validate that required fields are present.
    
    Args:
        values: Field values dictionary
        required_fields: List of required field names
    
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if field not in values or not values[field]]
    return len(missing) == 0, missing


# Common required fields for Request for Repair form
REQUEST_FOR_REPAIR_REQUIRED = [
    'date_prepared',
    'agreement_date',
    'property_address',
    'buyer_name',
    'seller_name'
]
