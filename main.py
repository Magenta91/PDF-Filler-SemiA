"""
Dwello PDF Form Filler

Usage: python main.py <input_json> <output_pdf>
"""

import json
import sys
from pathlib import Path


def load_json(json_path):
    """Load JSON data from file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def fill_pdf(json_data, template_path, output_path):
    """
    Fill PDF form with JSON data.
    
    TODO: Implement this function
    - Open template PDF
    - Map JSON fields to PDF locations
    - Fill the fields
    - Save to output_path
    """
    pass


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <input_json> <output_pdf>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    template_path = "resources/request_for_repair.pdf"
    
    # Load data
    data = load_json(json_path)
    
    # Fill PDF
    fill_pdf(data, template_path, output_path)
    
    print(f"✓ Filled PDF saved to: {output_path}")


if __name__ == "__main__":
    main()
