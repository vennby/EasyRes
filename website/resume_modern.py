import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def register_fonts():
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'EBGaramond-Regular.ttf')
    try:
        pdfmetrics.registerFont(TTFont('EBGaramond', font_path))
        return "EBGaramond", "EBGaramond"
    except:
        return "Helvetica", "Helvetica-Bold"

def generate_modern_resume(resume):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = 40
    right_margin = width - 40
    y = height - 50
    line_height = 20
    section_gap = 36
    min_y = 80

    font_main, font_bold = register_fonts()

    def draw_section(title, y):
        p.setFont(font_bold, 16)
        p.setFillColor(colors.HexColor('#005f73'))
        p.drawString(left_margin, y, title)
        y -= line_height
        p.setFillColor(colors.black)
        return y

    def check_page_break(y, needed=0):
        if y - needed < min_y:
            p.showPage()
            p.setFont(font_main, 12)
            return height - 50
        return y

    # Name
    person_name = getattr(resume.user.personal_info, 'full_name', None) if getattr(resume.user, 'personal_info', None) else getattr(resume, 'name', '')
    p.setFont(font_bold, 28)
    p.setFillColor(colors.HexColor('#005f73'))
    p.drawString(left_margin, y, person_name)
    y -= line_height + 10
    p.setFillColor(colors.black)

    # Contact Info
    personal_info = getattr(resume.user, 'personal_info', None)
    if personal_info:
        p.setFont(font_main, 12)
        contact = f"{personal_info.email or ''} | {personal_info.phone or ''} | {personal_info.linkedin or ''}"
        p.drawString(left_margin, y, contact)
        y -= line_height
    y -= section_gap

    # Bio
    if resume.bios:
        y = draw_section("About", y)
        p.setFont(font_main, 12)
        for bio in resume.bios:
            p.drawString(left_margin + 10, y, bio.bio)
            y -= line_height
        y -= section_gap

    # Education
    if resume.educations:
        y = draw_section("Education", y)
        for edu in resume.educations:
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{edu.uni}, {edu.location}")
            p.setFont(font_main, 11)
            p.drawString(left_margin + 10, y - line_height, f"{edu.degree} ({edu.start_year}-{edu.end_year})")
            y -= line_height * 2
        y -= section_gap

    # Experience
    if resume.experiences:
        y = draw_section("Experience", y)
        for exp in resume.experiences:
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, f"{exp.role} at {exp.comp}")
            p.setFont(font_main, 11)
            p.drawString(left_margin + 10, y - line_height, exp.desc or '')
            y -= line_height * 2
        y -= section_gap

    # Projects
    if resume.projects:
        y = draw_section("Projects", y)
        for proj in resume.projects:
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, proj.proj)
            p.setFont(font_main, 10)
            p.drawString(left_margin + 10, y - line_height, f"Tools: {proj.tool}")
            p.drawString(left_margin + 10, y - line_height * 2, proj.desc or '')
            y -= line_height * 3
        y -= section_gap

    # Skills
    if resume.skills:
        y = draw_section("Skills", y)
        grouped = {}
        for skill in resume.skills:
            group = skill.group or 'Other'
            grouped.setdefault(group, []).append(skill.data)
        for group, skills in grouped.items():
            p.setFont(font_bold, 12)
            y = check_page_break(y, 2 * line_height)
            p.drawString(left_margin + 10, y, group + ':')
            y -= line_height
            p.setFont(font_main, 12)
            p.drawString(left_margin + 30, y, ', '.join(skills))
            y -= line_height
        y -= section_gap

    p.save()
    buffer.seek(0)
    return buffer
