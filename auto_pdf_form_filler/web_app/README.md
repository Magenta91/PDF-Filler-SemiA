# Interactive PDF Form Filler - Web Application

A web-based interface for filling PDF forms with drag-and-drop field positioning.

## Features

- 📤 **Upload PDF** - Drag & drop or browse
- 🤖 **Auto-Detection** - Automatically detect field positions using templates
- 🎯 **Interactive Editing** - Drag fields to adjust positions
- ➕ **Add/Delete Fields** - Full control over form fields
- 💾 **Download** - Generate and download filled PDF

## Installation

### 1. Install System Dependencies

Same as main project:
- Tesseract OCR
- Poppler utilities

### 2. Install Python Dependencies

```bash
cd web_app
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Step 1: Upload PDF
- Drag & drop a PDF file or click to browse
- PDF will be converted to images for preview

### Step 2: Enter Form Data
- Fill in the form fields in the sidebar
- Dates in ISO format (YYYY-MM-DD)
- Repairs as one per line

### Step 3: Auto-Detect Positions
- Click "Auto-Detect Positions"
- System will place fields based on template (if available)
- Or place at default positions for manual adjustment

### Step 4: Adjust Positions
- **Drag** fields to move them
- **Click** to select a field
- **Delete** button (×) to remove
- **Add Field** to create new fields

### Step 5: Generate PDF
- Click "Generate PDF"
- Download the filled form

## How It Works

### Backend (Flask)
- `/api/upload` - Upload PDF, convert to images
- `/api/process` - Process form data, auto-detect positions
- `/api/generate` - Generate filled PDF with user positions
- `/api/download/<pdf_id>` - Download filled PDF

### Frontend (Vanilla JS)
- PDF preview with image overlay
- Draggable field elements
- Real-time position updates
- Coordinate conversion (screen ↔ PDF points)

## Architecture

```
User uploads PDF
    ↓
Convert to images (150 DPI for preview)
    ↓
User enters form data
    ↓
Auto-detect positions (template or default)
    ↓
Render draggable overlays on PDF preview
    ↓
User adjusts positions by dragging
    ↓
Convert to high-res (300 DPI) for generation
    ↓
Generate overlay PDF with final positions
    ↓
Merge with original PDF
    ↓
Download filled PDF
```

## Coordinate System

### Screen Coordinates
- Origin: Top-left
- Units: Pixels (scaled to fit browser)
- Used for: Drag & drop UI

### PDF Coordinates
- Origin: Bottom-left
- Units: Points (72 DPI)
- Used for: PDF generation

### Conversion
```javascript
// Screen to PDF
pdfX = screenX / scale
pdfY = pdfHeight - (screenY / scale)

// PDF to Screen
screenX = pdfX * scale
screenY = (pdfHeight - pdfY) * scale
```

## File Structure

```
web_app/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   └── app.js            # Frontend JavaScript
├── uploads/              # Temporary PDF uploads
└── outputs/              # Generated PDFs
```

## API Endpoints

### POST /api/upload
Upload PDF file

**Request:**
- Form data with 'pdf' file

**Response:**
```json
{
  "success": true,
  "pdf_id": "unique_id",
  "pages": [
    {
      "page": 1,
      "width": 2550,
      "height": 3300,
      "data": "data:image/png;base64,..."
    }
  ],
  "template_detected": "request_for_repair"
}
```

### POST /api/process
Process form data and detect positions

**Request:**
```json
{
  "pdf_id": "unique_id",
  "form_data": {
    "date_prepared": "2025-12-06",
    "buyer_name": "John Doe",
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "placements": [
    {
      "page": 1,
      "x": 100,
      "y": 700,
      "text": "John Doe",
      "field_key": "buyer_name",
      "font_size": 10
    }
  ]
}
```

### POST /api/generate
Generate filled PDF

**Request:**
```json
{
  "pdf_id": "unique_id",
  "placements": [...]
}
```

**Response:**
```json
{
  "success": true,
  "download_url": "/api/download/unique_id"
}
```

### GET /api/download/<pdf_id>
Download filled PDF

**Response:**
- PDF file download

## Customization

### Add Custom Templates
Edit `../autofill/templates.py` to add new form templates

### Adjust UI
Edit `templates/index.html` and `static/app.js`

### Change Port
```python
app.run(debug=True, port=8000)
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables

```bash
export FLASK_ENV=production
export MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Security Considerations

- File upload size limits (16MB default)
- File type validation (PDF only)
- Temporary file cleanup
- CORS configuration for production
- Input sanitization

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Tesseract not found"
Install Tesseract OCR and add to PATH

### "Port already in use"
Change port in `app.py` or kill process using port 5000

### Fields not dragging
Check browser console for JavaScript errors

## Future Enhancements

- [ ] Multi-user support with sessions
- [ ] Save/load field configurations
- [ ] Undo/redo functionality
- [ ] Keyboard shortcuts
- [ ] Field validation
- [ ] Batch processing
- [ ] Cloud storage integration
- [ ] Real-time collaboration

## License

Same as main project
