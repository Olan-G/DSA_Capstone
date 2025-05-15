# John Olan S. Gomez
# Data Analyst Specialist
# Python Programming Class
# This program creates a web app that contains a form that creates a resume in pdf

# app.py
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    professional_summary = request.form.get('professional_summary')
    
    # Get work experience data (sent as JSON)
    work_experiences = json.loads(request.form.get('work_experiences'))
    
    # Get education data
    education_institution = request.form.get('education_institution')
    education_degree = request.form.get('education_degree')
    education_field = request.form.get('education_field')
    education_start_date = request.form.get('education_start_date')
    education_end_date = request.form.get('education_end_date')
    education_current = request.form.get('education_current') == 'true'
    
    # Generate PDF
    pdf_path = create_resume_pdf(
        name, email, mobile, professional_summary,
        work_experiences,
        education_institution, education_degree, education_field,
        education_start_date, education_end_date, education_current
    )
    
    return send_file(pdf_path, as_attachment=True, download_name=f"{name.replace(' ', '_')}_Resume.pdf")

def create_resume_pdf(name, email, mobile, summary, work_experiences,
                     edu_institution, edu_degree, edu_field, edu_start, edu_end, edu_current):
    # Create a temporary file path
    output_path = "resume.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=1*inch,
        bottomMargin=1*inch,
        leftMargin=1*inch,
        rightMargin=1*inch
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Name',
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=6
    ))
    # Modify the existing 'Normal' style instead of adding a new one
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 10
    styles['Normal'].spaceAfter = 3
    
    styles.add(ParagraphStyle(
        name='JobTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        spaceAfter=2
    ))
    
    # Build document content
    content = []
    
    # Name and contact info
    content.append(Paragraph(name, styles['Name']))
    content.append(Paragraph(f"Email: {email} | Mobile: {mobile}", styles['Normal']))
    content.append(Spacer(1, 0.1*inch))
    
    # Professional Summary
    content.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionTitle']))
    content.append(Paragraph(summary, styles['Normal']))
    content.append(Spacer(1, 0.1*inch))
    
    # Professional Experience
    content.append(Paragraph("WORK EXPERIENCE", styles['SectionTitle']))
    
    for exp in work_experiences:
        job_line = f"{exp['position']}"
        content.append(Paragraph(job_line, styles['JobTitle']))
        company_line = f"{exp['company']}, {exp['address']}"
        content.append(Paragraph(company_line, styles['JobTitle']))
        
        # Handle date formatting
        if exp['current'] == True:
            date_line = f"{exp['start_date']} - Present"
        else:
            date_line = f"{exp['start_date']} - {exp['end_date']}"
        
        content.append(Paragraph(date_line, styles['Normal']))
        content.append(Paragraph(exp['description'] if 'description' in exp else "", styles['Normal']))
        content.append(Spacer(1, 0.1*inch))
    
    # Education
    content.append(Paragraph("EDUCATION", styles['SectionTitle']))
    
    degree_line = f"{edu_degree} in {edu_field}"
    content.append(Paragraph(degree_line, styles['JobTitle']))
    
    school_line = f"{edu_institution}"
    content.append(Paragraph(school_line, styles['Normal']))
    
    # Handle date formatting for education
    if edu_current:
        edu_date_line = f"{edu_start} - Present"
    else:
        edu_date_line = f"{edu_start} - {edu_end}"
    
    content.append(Paragraph(edu_date_line, styles['Normal']))
    
    # Build the PDF
    doc.build(content)
    
    return output_path

if __name__ == '__main__':
    app.run(debug=True)