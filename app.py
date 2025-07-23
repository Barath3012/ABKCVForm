from flask import Flask, render_template, request, flash, url_for, redirect, session
import os
from werkzeug.utils import secure_filename
import PyPDF2


app = Flask(__name__)
app.secret_key = 'boombayah'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

REQUIRED_SECTIONS = [
    "Key Skills",
    "Areas of Interest",
    "Technical Stack",
    "Projects worked"
]

def pdf_contains_required_sections(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() or ""

        # Normalize text
        full_text_lower = full_text.lower()

        # Check for all required sections
        for section in REQUIRED_SECTIONS:
            if section.lower() not in full_text_lower:
                return False, section  # Return the missing section
        return True, None

    except Exception as e:
        print("PDF parsing error:", e)
        return False, "PDF reading failed"


@app.route("/")
def index():
    form_data = session.pop('form_data', {})
    return render_template("index.html",form_data=form_data)
    
    
@app.route('/upload', methods=['POST'])
def upload():
    session['form_data'] = request.form.to_dict()
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Check for required content in PDF
    valid, missing_section = pdf_contains_required_sections(filepath)
    if not valid:
        flash(f"❌ CV must contain section: '{missing_section}'")
        os.remove(filepath)  # Clean up invalid file
        
        return redirect(url_for('index'))

    return ("✅ PDF uploaded and verified successfully!")
    
if __name__ == "__main__":
    app.run(debug=True)