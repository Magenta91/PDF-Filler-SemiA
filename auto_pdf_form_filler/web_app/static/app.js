// Global state
let pdfId = null;
let pages = [];
let placements = [];
let selectedField = null;
let draggedField = null;
let dragOffset = { x: 0, y: 0 };
let fieldsLocked = false;

// DOM elements
const uploadArea = document.getElementById('upload-area');
const pdfInput = document.getElementById('pdf-input');
const formSection = document.getElementById('form-section');
const editSection = document.getElementById('edit-section');
const pdfContainer = document.getElementById('pdf-container');
const processBtn = document.getElementById('process-btn');
const generateBtn = document.getElementById('generate-btn');
const addFieldBtn = document.getElementById('add-field-btn');
const resetBtn = document.getElementById('reset-btn');
const lockBtn = document.getElementById('lock-btn');
const statusDiv = document.getElementById('status');

// Upload handling
uploadArea.addEventListener('click', () => pdfInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') handleFileUpload(file);
});
pdfInput.addEventListener('change', (e) => {
    if (e.target.files[0]) handleFileUpload(e.target.files[0]);
});

async function handleFileUpload(file) {
    showStatus('Uploading PDF...', 'info');
    const formData = new FormData();
    formData.append('pdf', file);
    
    try {
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            pdfId = data.pdf_id;
            pages = data.pages;
            showStatus(`✓ PDF uploaded (${pages.length} pages)`, 'success');
            formSection.classList.remove('hidden');
            displayPDF();
        } else {
            showStatus('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

function displayPDF() {
    pdfContainer.innerHTML = '';
    pages.forEach((page) => {
        const pageDiv = document.createElement('div');
        pageDiv.className = 'pdf-page';
        pageDiv.id = `page-${page.page}`;
        pageDiv.dataset.page = page.page;
        pageDiv.dataset.width = page.width;
        pageDiv.dataset.height = page.height;
        
        const img = document.createElement('img');
        img.src = page.data;
        img.alt = `Page ${page.page}`;
        
        pageDiv.appendChild(img);
        pdfContainer.appendChild(pageDiv);
    });
}

processBtn.addEventListener('click', async () => {
    if (!pdfId) { showStatus('Error: No PDF uploaded', 'error'); return; }
    showStatus('Processing...', 'info');
    
    const formData = {
        date_prepared: document.getElementById('date_prepared').value,
        agreement_date: document.getElementById('agreement_date').value,
        property_address: document.getElementById('property_address').value,
        buyer_name: document.getElementById('buyer_name').value,
        seller_name: document.getElementById('seller_name').value,
        repairs: document.getElementById('repairs').value.split('\n').filter(r => r.trim())
    };
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pdf_id: pdfId, form_data: formData })
        });
        const data = await response.json();
        
        if (data.success) {
            placements = data.placements;
            showStatus(`✓ ${placements.length} fields ready`, 'success');
            editSection.classList.remove('hidden');
            renderFieldOverlays();
        } else {
            showStatus('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
});

function renderFieldOverlays() {
    document.querySelectorAll('.field-overlay').forEach(el => el.remove());
    
    placements.forEach((p, index) => {
        const pageDiv = document.getElementById(`page-${p.page}`);
        if (!pageDiv) return;
        
        const img = pageDiv.querySelector('img');
        const screenX = (p.x_pct / 100) * img.clientWidth;
        const screenY = (p.y_pct / 100) * img.clientHeight;
        
        const overlay = document.createElement('div');
        overlay.className = 'field-overlay' + (fieldsLocked ? ' locked' : '');
        overlay.dataset.index = index;
        overlay.style.left = screenX + 'px';
        overlay.style.top = screenY + 'px';
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (e) => { e.stopPropagation(); deleteField(index); };
        
        // Label
        const label = document.createElement('div');
        label.className = 'field-label';
        label.textContent = p.field_key;
        
        // Text
        const text = document.createElement('div');
        text.className = 'field-text';
        text.textContent = p.text;
        text.style.fontSize = (p.font_size || 10) + 'px';
        text.style.fontWeight = p.bold ? 'bold' : 'normal';
        
        // Controls
        const controls = document.createElement('div');
        controls.className = 'field-controls';
        
        // Font size buttons
        const fontMinus = document.createElement('button');
        fontMinus.textContent = 'A-';
        fontMinus.onclick = (e) => { e.stopPropagation(); changeFontSize(index, -1); };
        
        const fontPlus = document.createElement('button');
        fontPlus.textContent = 'A+';
        fontPlus.onclick = (e) => { e.stopPropagation(); changeFontSize(index, 1); };
        
        // Bold button
        const boldBtn = document.createElement('button');
        boldBtn.textContent = 'B';
        boldBtn.style.fontWeight = 'bold';
        boldBtn.className = p.bold ? 'active' : '';
        boldBtn.onclick = (e) => { e.stopPropagation(); toggleBold(index); };
        
        controls.appendChild(fontMinus);
        controls.appendChild(fontPlus);
        controls.appendChild(boldBtn);
        
        overlay.appendChild(deleteBtn);
        overlay.appendChild(label);
        overlay.appendChild(text);
        overlay.appendChild(controls);
        
        if (!fieldsLocked) {
            overlay.addEventListener('mousedown', startDrag);
        }
        overlay.addEventListener('click', () => selectField(index));
        
        pageDiv.appendChild(overlay);
    });
}

function changeFontSize(index, delta) {
    placements[index].font_size = Math.max(6, Math.min(24, (placements[index].font_size || 10) + delta));
    renderFieldOverlays();
}

function toggleBold(index) {
    placements[index].bold = !placements[index].bold;
    renderFieldOverlays();
}

function startDrag(e) {
    if (fieldsLocked || e.target.tagName === 'BUTTON') return;
    
    draggedField = e.currentTarget;
    selectField(parseInt(draggedField.dataset.index));
    
    const rect = draggedField.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;
    
    draggedField.style.position = 'fixed';
    draggedField.style.left = rect.left + 'px';
    draggedField.style.top = rect.top + 'px';
    draggedField.style.zIndex = '1000';
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    e.preventDefault();
}

function drag(e) {
    if (!draggedField) return;
    draggedField.style.left = (e.clientX - dragOffset.x) + 'px';
    draggedField.style.top = (e.clientY - dragOffset.y) + 'px';
    
    document.querySelectorAll('.pdf-page').forEach(page => {
        const rect = page.getBoundingClientRect();
        page.classList.toggle('drag-over', 
            e.clientX >= rect.left && e.clientX <= rect.right &&
            e.clientY >= rect.top && e.clientY <= rect.bottom);
    });
}

function stopDrag(e) {
    if (draggedField) {
        const index = parseInt(draggedField.dataset.index);
        document.querySelectorAll('.pdf-page').forEach(p => p.classList.remove('drag-over'));
        
        for (const page of document.querySelectorAll('.pdf-page')) {
            const rect = page.getBoundingClientRect();
            if (e.clientX >= rect.left && e.clientX <= rect.right &&
                e.clientY >= rect.top && e.clientY <= rect.bottom) {
                
                const img = page.querySelector('img');
                let x = e.clientX - rect.left - dragOffset.x;
                let y = e.clientY - rect.top - dragOffset.y;
                
                x = Math.max(0, Math.min(x, img.clientWidth - 10));
                y = Math.max(0, Math.min(y, img.clientHeight - 10));
                
                placements[index].x_pct = (x / img.clientWidth) * 100;
                placements[index].y_pct = (y / img.clientHeight) * 100;
                placements[index].page = parseInt(page.dataset.page);
                
                console.log(`Moved to page ${placements[index].page}: ${placements[index].x_pct.toFixed(2)}%, ${placements[index].y_pct.toFixed(2)}%`);
                break;
            }
        }
        
        draggedField = null;
        renderFieldOverlays();
    }
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', stopDrag);
}

function selectField(index) {
    document.querySelectorAll('.field-overlay').forEach(el => el.classList.remove('selected'));
    const overlay = document.querySelector(`[data-index="${index}"]`);
    if (overlay) { overlay.classList.add('selected'); selectedField = index; }
}

function deleteField(index) {
    placements.splice(index, 1);
    renderFieldOverlays();
    showStatus('Field deleted', 'info');
}

addFieldBtn.addEventListener('click', () => {
    const text = prompt('Enter field text:');
    if (!text) return;
    const fieldKey = prompt('Enter field key:') || 'custom';
    
    placements.push({
        page: 1, x_pct: 10, y_pct: 10,
        text: text, field_key: fieldKey,
        font_size: 10, bold: false
    });
    renderFieldOverlays();
    showStatus('Field added', 'success');
});

lockBtn.addEventListener('click', () => {
    fieldsLocked = !fieldsLocked;
    lockBtn.textContent = fieldsLocked ? '🔓 Unlock' : '🔒 Lock';
    lockBtn.classList.toggle('locked', fieldsLocked);
    renderFieldOverlays();
    showStatus(fieldsLocked ? 'Fields locked' : 'Fields unlocked', 'info');
});

resetBtn.addEventListener('click', () => {
    if (confirm('Reset all fields?')) processBtn.click();
});

generateBtn.addEventListener('click', async () => {
    showStatus('Generating PDF...', 'info');
    
    console.log('Sending placements:', JSON.stringify(placements, null, 2));
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pdf_id: pdfId, placements: placements })
        });
        const data = await response.json();
        
        if (data.success) {
            showStatus('✓ PDF generated!', 'success');
            window.location.href = data.download_url;
        } else {
            showStatus('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
});

function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    if (type !== 'error') setTimeout(() => statusDiv.className = 'status hidden', 3000);
}
