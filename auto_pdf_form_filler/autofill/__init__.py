"""Auto PDF Form Filler - Automatic form field detection and filling."""

from .ocr import extract_text_blocks, TextBlock
from .detector import find_all_labels, find_best_label, LabelMatch
from .layout import detect_horizontal_lines, compute_fill_position, Line
from .renderer import draw_text_overlay, FieldPlacement
from .merger import merge_overlay

__all__ = [
    'extract_text_blocks',
    'TextBlock',
    'find_all_labels',
    'find_best_label',
    'LabelMatch',
    'detect_horizontal_lines',
    'compute_fill_position',
    'Line',
    'draw_text_overlay',
    'FieldPlacement',
    'merge_overlay',
]
