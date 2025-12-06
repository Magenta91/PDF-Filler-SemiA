"""
Interactive PDF Form Filler - Flask Web Application
Uses percentage-based coordinates for accurate positioning.
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import base64
from pathlib import Path
from pdf2image import convert_from_path
import io
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from autofill import extract_text_blocks, merge_overlay
from autofill.templates import get_template, detect_template
from autofill.field_processor import process_field_values
from autofill.renderer import FieldPlacement, create_overlay_pdf

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('outputs')
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    pdf_id = str(int(datetime.now().timestamp() * 1000))
    pdf_filename = f"{pdf_id}_{pdf_file.filename}"
    pdf_path = UPLOAD_FOLDER / pdf_filename
    pdf_file.save(pdf_path)
    
    try:
        images = convert_from_path(pdf_path, dpi=150)
        
        image_data = []
        for i, image in enumerate(images):
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            image_data.append({
                'page': i + 1,
                'width': image.width,
                'height': image.height,
                'data': f"data:image/png;base64,{img_base64}"
            })
        
        return jsonify({
            'success': True,
            'pdf_id': pdf_id,
            'pages': image_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_form():
    data = request.json
    pdf_id = data.get('pdf_id')
    form_data = data.get('form_data', {})
    
    if not pdf_id:
        return jsonify({'error': 'No PDF ID provided'}), 400
    
    pdf_files = list(UPLOAD_FOLDER.glob(f"{pdf_id}_*"))
    if not pdf_files:
        return jsonify({'error': 'PDF not found'}), 404
    
    pdf_path = pdf_files[0]
    
    try:
        processed_data = process_field_values(form_data)
        
        # Place fields at default positions (percentage-based)
        # User will adjust manually
        placements = []
        y_pct = 15  # Start at 15% from top
        
        for field_key, value in processed_data.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    placements.append({
                        'page': 1,
                        'x_pct': 10,
                        'y_pct': y_pct + (i * 2),
                        'text': f"• {item}",
                        'field_key': field_key,
                        'font_size': 8
                    })
                y_pct += len(value) * 2 + 3
            else:
                placements.append({
                    'page': 1,
                    'x_pct': 10,
                    'y_pct': y_pct,
                    'text': str(value),
                    'field_key': field_key,
                    'font_size': 10
                })
                y_pct += 4
        
        return jsonify({
            'success': True,
            'placements': placements,
            'processed_data': processed_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_pdf():
    data = request.json
    pdf_id = data.get('pdf_id')
    placements = data.get('placements', [])
    
    if not pdf_id:
        return jsonify({'error': 'No PDF ID provided'}), 400
    
    pdf_files = list(UPLOAD_FOLDER.glob(f"{pdf_id}_*"))
    if not pdf_files:
        return jsonify({'error': 'PDF not found'}), 404
    
    pdf_path = pdf_files[0]
    
    try:
        # Convert at 300 DPI for high quality output
        images = convert_from_path(pdf_path, dpi=300)
        
        # Group placements by page
        placements_by_page = {}
        for p in placements:
            page = p['page']
            if page not in placements_by_page:
                placements_by_page[page] = []
            placements_by_page[page].append(p)
        
        overlay_pdfs = []
        
        for page_idx, image in enumerate(images):
            page_num = page_idx + 1
            img_width = image.width   # pixels at 300 DPI
            img_height = image.height
            
            page_placements = placements_by_page.get(page_num, [])
            field_placements = []
            
            for p in page_placements:
                # Convert percentage to pixels
                pixel_x = (p['x_pct'] / 100) * img_width
                pixel_y = (p['y_pct'] / 100) * img_height
                
                print(f"[GEN] {p.get('field_key','?')}: ({p['x_pct']:.1f}%, {p['y_pct']:.1f}%) -> pixel ({int(pixel_x)}, {int(pixel_y)})")
                
                field_placements.append(
                    FieldPlacement(
                        int(pixel_x),
                        int(pixel_y),
                        p['text'],
                        p.get('font_size', 10),
                        p.get('bold', False)
                    )
                )
            
            if field_placements:
                overlay_bytes = create_overlay_pdf(
                    field_placements,
                    img_width,
                    img_height,
                    dpi=300
                )
                overlay_pdfs.append(overlay_bytes)
            else:
                overlay_pdfs.append(None)
        
        output_path = OUTPUT_FOLDER / f"{pdf_id}_filled.pdf"
        merge_overlay(str(pdf_path), overlay_pdfs, str(output_path))
        
        return jsonify({
            'success': True,
            'download_url': f'/api/download/{pdf_id}'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<pdf_id>')
def download_pdf(pdf_id):
    output_path = OUTPUT_FOLDER / f"{pdf_id}_filled.pdf"
    
    if not output_path.exists():
        return jsonify({'error': 'PDF not found'}), 404
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name='filled_form.pdf',
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
