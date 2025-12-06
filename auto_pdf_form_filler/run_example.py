"""
Quick example runner to test the auto PDF form filler.
This script demonstrates the basic usage without command-line arguments.
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import main as run_main


def run_example():
    """Run the example with predefined paths."""
    
    # Define paths
    input_json = "samples/input.json"
    template_pdf = "samples/request_for_repair.pdf"
    output_pdf = "output/filled_example.pdf"
    
    # Check if files exist
    if not os.path.exists(input_json):
        print(f"❌ Error: Sample input not found: {input_json}")
        print("   Make sure you're running this from the auto_pdf_form_filler directory")
        return False
    
    if not os.path.exists(template_pdf):
        print(f"❌ Error: Sample PDF not found: {template_pdf}")
        print("   Make sure you're running this from the auto_pdf_form_filler directory")
        return False
    
    print("=" * 70)
    print("Auto PDF Form Filler - Example Run")
    print("=" * 70)
    print(f"Input JSON: {input_json}")
    print(f"Template PDF: {template_pdf}")
    print(f"Output PDF: {output_pdf}")
    print("=" * 70)
    print()
    
    # Set up sys.argv for main()
    sys.argv = ["main.py", input_json, template_pdf, output_pdf]
    
    try:
        run_main()
        print()
        print("=" * 70)
        print("✓ Example completed successfully!")
        print(f"  Check the output at: {output_pdf}")
        print("=" * 70)
        return True
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error during execution: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_example()
    sys.exit(0 if success else 1)
