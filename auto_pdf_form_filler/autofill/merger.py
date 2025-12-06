"""PDF merging utilities using PyPDF."""
from pypdf import PdfReader, PdfWriter
from typing import List
import io


def merge_overlay(template_pdf_path: str, overlay_pdfs: List[bytes], 
                 output_pdf_path: str) -> None:
    """
    Merge overlay PDFs with template PDF.
    
    Args:
        template_pdf_path: Path to original PDF template
        overlay_pdfs: List of overlay PDF bytes (one per page)
        output_pdf_path: Path to save merged PDF
    """
    # Read template PDF
    template_reader = PdfReader(template_pdf_path)
    writer = PdfWriter()
    
    # Process each page
    for page_idx, page in enumerate(template_reader.pages):
        # If we have an overlay for this page, merge it
        if page_idx < len(overlay_pdfs) and overlay_pdfs[page_idx]:
            overlay_reader = PdfReader(io.BytesIO(overlay_pdfs[page_idx]))
            overlay_page = overlay_reader.pages[0]
            
            # Merge overlay onto template page
            page.merge_page(overlay_page)
        
        writer.add_page(page)
    
    # Write output
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)


def merge_single_overlay(template_pdf_path: str, overlay_pdf_bytes: bytes,
                        page_idx: int, output_pdf_path: str) -> None:
    """
    Merge a single overlay PDF onto a specific page of template.
    
    Args:
        template_pdf_path: Path to original PDF template
        overlay_pdf_bytes: Overlay PDF bytes
        page_idx: Page index to merge overlay onto (0-based)
        output_pdf_path: Path to save merged PDF
    """
    template_reader = PdfReader(template_pdf_path)
    overlay_reader = PdfReader(io.BytesIO(overlay_pdf_bytes))
    writer = PdfWriter()
    
    for idx, page in enumerate(template_reader.pages):
        if idx == page_idx:
            # Merge overlay onto this page
            overlay_page = overlay_reader.pages[0]
            page.merge_page(overlay_page)
        
        writer.add_page(page)
    
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)
