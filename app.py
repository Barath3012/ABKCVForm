from flask import Flask, render_template, request, flash, url_for, redirect, session
import os
from werkzeug.utils import secure_filename
import PyPDF2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'  # or a cloud URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
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
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)


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
    form_data = request.form.to_dict()
    session['form_data'] = form_data
    email = form_data.get("email")
    if Submission.query.filter_by(email=email).first():
        flash("❌ This email has already submitted a CV.")
        return redirect(url_for('index'))
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