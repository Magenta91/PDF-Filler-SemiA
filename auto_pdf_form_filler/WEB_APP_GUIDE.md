# 🌐 Interactive PDF Form Filler - Web Application

## Overview

We've created a **web-based interactive PDF form filler** that solves the positioning accuracy problem by letting users visually adjust field positions!

### Key Features

✅ **Drag & Drop PDF Upload**  
✅ **Auto-Detection** - Uses templates when available  
✅ **Visual Editor** - Drag fields to adjust positions  
✅ **Add/Delete Fields** - Full control  
✅ **Real-Time Preview** - See changes instantly  
✅ **Download Filled PDF** - One-click download  

---

## Quick Start

### 1. Install Dependencies

```bash
cd web_app
pip install -r requirements.txt
```

### 2. Run the Server

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly:**
```bash
python app.py
```

### 3. Open Browser

Navigate to: **http://localhost:5000**

---

## How to Use

### Step 1: Upload PDF
1. Drag & drop a PDF file onto the upload area
2. Or click to browse and select a file
3. PDF will be converted to images for preview

### Step 2: Enter Form Data
Fill in the form fields:
- **Date Prepared**: ISO format (YYYY-MM-DD)
- **Agreement Date**: ISO format
- **Property Address**: Full address
- **Buyer Name**: Full name (initials auto-generated)
- **Seller Name**: Full name (initials auto-generated)
- **Repairs**: One per line

### Step 3: Auto-Detect Positions
1. Click "Auto-Detect Positions"
2. System will:
   - Detect form template (if known)
   - Place fields at template coordinates
   - Or place at default positions for manual adjustment

### Step 4: Adjust Positions Visually
- **Drag** any field to move it
- **Click** a field to select it
- **Delete** button (×) to remove a field
- **Add Field** button to create new fields

### Step 5: Generate & Download
1. Click "Generate PDF"
2. PDF will be created with your adjusted positions
3. Download automatically starts

---

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Interactive PDF Form Filler                        │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│  Sidebar     │         PDF Preview                  │
│              │                                       │
│  1. Upload   │    ┌──────────────────┐             │
│  2. Form     │    │  [Draggable      │             │
│  3. Adjust   │    │   Field]         │             │
│  4. Download │    │                  │             │
│              │    │  [Another Field] │             │
│              │    └──────────────────┘             │
└──────────────┴──────────────────────────────────────┘
```

### Field Overlay

Each field appears as a draggable box:
```
┌─────────────────────────┐
│ × (delete button)       │
│ field_key               │ ← Field identifier
│ John Doe                │ ← Field value
└─────────────────────────┘
```

- **Green border**: Normal field
- **Blue border**: Selected field
- **Hover**: Shows delete button

---

## Technical Details

### Architecture

```
Frontend (HTML/CSS/JS)
    ↓
Flask Backend (Python)
    ↓
PDF Processing (pdf2image, PyPDF)
    ↓
Template System (autofill/templates.py)
    ↓
Overlay Generation (ReportLab)
    ↓
Final PDF
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main page |
| `/api/upload` | POST | Upload PDF |
| `/api/process` | POST | Process form data |
| `/api/generate` | POST | Generate filled PDF |
| `/api/download/<id>` | GET | Download PDF |

### Coordinate System

The app handles two coordinate systems:

**Screen Coordinates** (for UI):
- Origin: Top-left
- Units: Pixels (scaled)
- Used for: Drag & drop

**PDF Coordinates** (for generation):
- Origin: Bottom-left
- Units: Points (72 DPI)
- Used for: PDF rendering

Conversion happens automatically when dragging!

---

## Advantages Over CLI

| Feature | CLI | Web App |
|---------|-----|---------|
| **Visual Feedback** | ❌ No | ✅ Yes |
| **Position Adjustment** | ❌ Manual coordinates | ✅ Drag & drop |
| **User-Friendly** | ❌ Technical | ✅ Intuitive |
| **Preview** | ❌ No | ✅ Real-time |
| **Accessibility** | ❌ Command line | ✅ Browser |
| **Learning Curve** | ❌ Steep | ✅ Minimal |

---

## Use Cases

### 1. First-Time Form Setup
- Upload new form type
- Let system auto-detect positions
- Adjust visually
- Save configuration for future use

### 2. Quick Form Filling
- Upload known form
- Enter data
- Auto-detect uses saved template
- Minor adjustments if needed
- Download

### 3. Template Creation
- Upload form
- Manually place all fields
- Export coordinates
- Add to template library

### 4. Batch Processing
- Upload form once
- Fill multiple times with different data
- Same positions each time

---

## Customization

### Change Port

Edit `app.py`:
```python
app.run(debug=True, port=8000)
```

### Add Custom Styling

Edit `templates/index.html` CSS section

### Add New Features

Edit `static/app.js` for frontend logic  
Edit `app.py` for backend logic

---

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

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads outputs

# Run
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t pdf-filler-web .
docker run -p 5000:5000 pdf-filler-web
```

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your-secret-key
export MAX_CONTENT_LENGTH=16777216
```

---

## Security Considerations

### Current Implementation
- ✅ File type validation (PDF only)
- ✅ File size limits (16MB)
- ✅ Temporary file storage
- ✅ CORS enabled for development

### Production Recommendations
- 🔒 Add authentication
- 🔒 Use HTTPS
- 🔒 Implement rate limiting
- 🔒 Add CSRF protection
- 🔒 Sanitize file names
- 🔒 Clean up old files
- 🔒 Use secure session storage

---

## Troubleshooting

### Server won't start

**Error**: "Port 5000 already in use"  
**Solution**: Change port or kill process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

### PDF not uploading

**Error**: "File too large"  
**Solution**: Increase `MAX_CONTENT_LENGTH` in `app.py`

**Error**: "Invalid file type"  
**Solution**: Ensure file is actually a PDF

### Fields not dragging

**Check**: Browser console for JavaScript errors  
**Solution**: Refresh page, clear cache

### Tesseract not found

**Solution**: Install Tesseract OCR and add to PATH

---

## Future Enhancements

### Planned Features
- [ ] **Save Templates** - Save field positions for reuse
- [ ] **Undo/Redo** - Undo position changes
- [ ] **Keyboard Shortcuts** - Arrow keys to nudge fields
- [ ] **Zoom Controls** - Zoom in/out on PDF
- [ ] **Field Validation** - Validate field values
- [ ] **Batch Upload** - Process multiple PDFs
- [ ] **User Accounts** - Save personal templates
- [ ] **Collaboration** - Share templates with team
- [ ] **API Access** - RESTful API for integration
- [ ] **Mobile Support** - Touch-friendly interface

### Advanced Features
- [ ] **OCR Improvement** - Better text detection
- [ ] **Smart Suggestions** - AI-powered field placement
- [ ] **Form Recognition** - Identify form type automatically
- [ ] **Multi-Language** - Support international forms
- [ ] **Signature Support** - Add signature images
- [ ] **Checkbox Detection** - Handle checkboxes
- [ ] **Table Support** - Fill table cells

---

## Comparison with Other Solutions

### vs. Adobe Acrobat
- ✅ Free and open source
- ✅ Customizable
- ❌ Less features
- ❌ No OCR form recognition

### vs. DocuSign
- ✅ Self-hosted
- ✅ No per-document cost
- ❌ No e-signature workflow
- ❌ No audit trail

### vs. PDFtk / CLI Tools
- ✅ Visual interface
- ✅ No coordinate calculation
- ✅ User-friendly
- ❌ Requires web server

---

## Summary

The **Interactive PDF Form Filler Web App** provides the best of both worlds:

1. **Automatic Detection** - Uses templates when available
2. **Visual Adjustment** - Drag & drop for precision
3. **User-Friendly** - No technical knowledge required
4. **Production-Ready** - Can be deployed immediately

This is the **industry-standard approach** used by commercial solutions, now available as an open-source tool!

---

## Getting Help

- **Documentation**: See `web_app/README.md`
- **Main Project**: See `../README.md`
- **Technical Details**: See `../CURRENT_STATUS.md`
- **API Reference**: See `web_app/README.md` API section

---

**Status**: ✅ Ready to Use  
**Technology**: Flask + Vanilla JavaScript  
**Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)  
**Mobile**: Partially supported (desktop recommended)
