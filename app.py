from flask import Flask, render_template, request, send_file
import os
import fitz
import matplotlib.pyplot as plt
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CHART_FOLDER = "static/charts"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)


# =========================
# EXTRACT TEXT FROM PDF
# =========================

def extract_text_from_pdf(pdf_path):

    text = ""

    pdf = fitz.open(pdf_path)

    for page in pdf:
        text += page.get_text()

    return text.lower()


# =========================
# ANALYZE RESUME
# =========================

def analyze_resume(resume_text, job_description):

    jd = job_description.lower()

    skills = [
        "python",
        "java",
        "c++",
        "machine learning",
        "deep learning",
        "data science",
        "flask",
        "django",
        "react",
        "node.js",
        "sql",
        "mongodb",
        "git",
        "docker",
        "html",
        "css",
        "javascript"
    ]

    matched_skills = []
    missing_skills = []

    for skill in skills:

        if skill in resume_text and skill in jd:
            matched_skills.append(skill)

        elif skill in jd:
            missing_skills.append(skill)

    total = len(matched_skills) + len(missing_skills)

    if total == 0:
        score = 0
    else:
        score = int((len(matched_skills) / total) * 100)

    return score, matched_skills, missing_skills


# =========================
# FEEDBACK
# =========================

def generate_feedback(score):

    suggestions = []

    if score >= 80:
        suggestions.append("Excellent resume for this role.")
        suggestions.append("Keep improving project portfolio.")
        suggestions.append("Add certifications for extra impact.")

    elif score >= 50:
        suggestions.append("Resume has good potential.")
        suggestions.append("Add more relevant technical skills.")
        suggestions.append("Improve project descriptions.")
        suggestions.append("Add deployment experience.")

    else:
        suggestions.append("Resume needs major improvements.")
        suggestions.append("Add more technical projects.")
        suggestions.append("Learn missing skills from job description.")
        suggestions.append("Improve resume formatting.")
        suggestions.append("Add GitHub and LinkedIn links.")

    return suggestions


# =========================
# CREATE CHART
# =========================

def generate_chart(score):

    matched = score
    missing = 100 - score

    labels = ["Matched", "Missing"]

    sizes = [matched, missing]

    colors = ["green", "red"]

    plt.figure(figsize=(5, 5))

    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.axis("equal")

    chart_path = os.path.join(CHART_FOLDER, "chart.png")

    plt.savefig(chart_path)

    plt.close()

    return chart_path


# =========================
# PDF REPORT
# =========================

def create_pdf(score, matched_skills, missing_skills, suggestions):

    doc = SimpleDocTemplate("resume_report.pdf")

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Resume Analysis Report", styles['Title']))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"<b>Resume Score:</b> {score}%", styles['BodyText'])
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"<b>Matched Skills:</b> {', '.join(matched_skills)}",
            styles['BodyText']
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"<b>Missing Skills:</b> {', '.join(missing_skills)}",
            styles['BodyText']
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Suggestions:</b>", styles['Heading2']))

    for suggestion in suggestions:
        elements.append(
            Paragraph(f"• {suggestion}", styles['BodyText'])
        )

    elements.append(Spacer(1, 20))

    chart_path = "static/charts/chart.png"

    if os.path.exists(chart_path):
        elements.append(Image(chart_path, width=300, height=300))

    doc.build(elements)


# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["resume"]

    job_description = request.form["job_description"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(filepath)

    resume_text = extract_text_from_pdf(filepath)

    score, matched_skills, missing_skills = analyze_resume(
        resume_text,
        job_description
    )

    suggestions = generate_feedback(score)

    generate_chart(score)

    create_pdf(
        score,
        matched_skills,
        missing_skills,
        suggestions
    )

    if score >= 80:
        message = "Excellent Resume"
        color_class = "green"

    elif score >= 50:
        message = "Good Resume"
        color_class = "yellow"

    else:
        message = "Resume Needs Improvement"
        color_class = "red"

    return render_template(
        "report.html",
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
        message=message,
        color_class=color_class
    )


@app.route("/download")
def download():

    return send_file(
        "resume_report.pdf",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)