"""Label detection and fuzzy matching for form fields."""
from typing import List, Optional, Dict
from Levenshtein import ratio as levenshtein_ratio
from .ocr import TextBlock


class LabelMatch:
    """Represents a matched label with its text block."""
    
    def __init__(self, label_key: str, block: TextBlock, similarity: float):
        self.label_key = label_key
        self.block = block
        self.similarity = similarity
    
    def __repr__(self):
        return f"LabelMatch('{self.label_key}' -> '{self.block.text}', sim={self.similarity:.2f})"


# Common form field label patterns
LABEL_PATTERNS = {
    'date_prepared': ['date prepared', 'date', 'prepared date', 'prep date'],
    'agreement_date': ['dated', 'agreement dated', 'date of agreement', 'contract date'],
    'property_address': ['property', 'property known as', 'address', 'property address', 'located at'],
    'buyer_name': ['buyer', 'buyer name', 'purchaser', 'buyer(s)'],
    'seller_name': ['seller', 'seller name', 'vendor', 'seller(s)'],
    'repairs': ['repairs', 'repair items', 'work to be completed', 'items'],
    'buyer_initials': ['buyer initials', 'initials', 'buyer initial'],
    'buyer_signature': ['buyer signature', 'signature', 'buyer sign', 'signed'],
    'signature_date': ['date', 'signature date', 'signed date'],
}


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    return text.lower().strip().replace(':', '').replace('_', ' ')


def find_label_blocks(blocks: List[TextBlock], target_label: str, 
                      patterns: Dict[str, List[str]] = None,
                      similarity_threshold: float = 0.6) -> List[LabelMatch]:
    """
    Find text blocks that match a target label using fuzzy matching.
    
    Args:
        blocks: List of TextBlock objects from OCR
        target_label: Key of the label to find (e.g., 'date_prepared')
        patterns: Dictionary of label patterns (defaults to LABEL_PATTERNS)
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of LabelMatch objects, sorted by similarity (best first)
    """
    if patterns is None:
        patterns = LABEL_PATTERNS
    
    if target_label not in patterns:
        return []
    
    label_variants = patterns[target_label]
    matches = []
    
    for block in blocks:
        normalized_text = normalize_text(block.text)
        
        # Check against all pattern variants
        for pattern in label_variants:
            normalized_pattern = normalize_text(pattern)
            
            # Calculate similarity
            similarity = levenshtein_ratio(normalized_text, normalized_pattern)
            
            # Also check if pattern is contained in text
            if normalized_pattern in normalized_text or normalized_text in normalized_pattern:
                similarity = max(similarity, 0.8)
            
            if similarity >= similarity_threshold:
                matches.append(LabelMatch(target_label, block, similarity))
                break  # Found a match for this block
    
    # Sort by similarity (best first)
    matches.sort(key=lambda m: m.similarity, reverse=True)
    return matches


def find_best_label(blocks: List[TextBlock], target_label: str, 
                   patterns: Dict[str, List[str]] = None) -> Optional[LabelMatch]:
    """
    Find the best matching label block for a target label.
    
    Args:
        blocks: List of TextBlock objects
        target_label: Key of the label to find
        patterns: Dictionary of label patterns
    
    Returns:
        Best LabelMatch or None if no match found
    """
    matches = find_label_blocks(blocks, target_label, patterns)
    return matches[0] if matches else None


def find_all_labels(blocks: List[TextBlock], 
                   label_keys: List[str] = None,
                   patterns: Dict[str, List[str]] = None) -> Dict[str, LabelMatch]:
    """
    Find all specified labels in the text blocks.
    
    Args:
        blocks: List of TextBlock objects
        label_keys: List of label keys to find (defaults to all in LABEL_PATTERNS)
        patterns: Dictionary of label patterns
    
    Returns:
        Dictionary mapping label keys to their best matches
    """
    if patterns is None:
        patterns = LABEL_PATTERNS
    
    if label_keys is None:
        label_keys = list(patterns.keys())
    
    results = {}
    for label_key in label_keys:
        match = find_best_label(blocks, label_key, patterns)
        if match:
            results[label_key] = match
    
    return results
