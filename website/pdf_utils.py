import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file

# Colors for subtle lines and section titles
from reportlab.lib import colors

def generate_resume_pdf(resume):
    if getattr(resume, 'format', 'classic') == 'modern':
        return generate_resume_pdf_modern(resume)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = 50
    right_margin = width - 50
    y = height - 60
    line_height = 18
    section_gap = 32
    min_y = 80  # Minimum y before page break

    # Register EB Garamond font (ensure the TTF file exists at the specified path)
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'EBGaramond-Regular.ttf')
    try:
        pdfmetrics.registerFont(TTFont('EBGaramond', font_path))
        font_main = "EBGaramond"
        font_bold = "EBGaramond"
    except Exception as e:
        font_main = "Helvetica"
        font_bold = "Helvetica-Bold"

    def draw_wrapped_text(text, x, y, max_width, font, font_size, bullet=None):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line = ''
        first_line = True
        bullet_width = stringWidth('• ', font, font_size) if bullet else 0
        while words:
            test_line = f'{line} {words[0]}'.strip()
            if stringWidth(test_line, font, font_size) + (bullet_width if first_line else 0) < max_width:
                line = test_line
                words.pop(0)
            else:
                if bullet and first_line:
                    p.drawString(x, y, f'{bullet} {line}')
                else:
                    p.drawString(x + (bullet_width if bullet and not first_line else 0), y, line)
                y -= line_height
                line = ''
                first_line = False
        if line:
            if bullet and first_line:
                p.drawString(x, y, f'{bullet} {line}')
            else:
                p.drawString(x + (bullet_width if bullet and not first_line else 0), y, line)
            y -= line_height
        return y

    def check_page_break(y, needed=0):
        if y - needed < min_y:
            p.showPage()
            p.setFont(font_main, 12)
            return height - 60
        return y

    def section_title(title, y):
        y = check_page_break(y, 2*line_height)
        p.setFont(font_bold, 15)
        p.setFillColor(colors.HexColor('#222222'))
        p.drawString(left_margin, y, title.upper())
        y -= 8
        p.setStrokeColor(colors.HexColor('#cccccc'))
        p.setLineWidth(1)
        p.line(left_margin, y, right_margin, y)
        y -= line_height
        p.setFillColor(colors.black)
        return y

    # Name (centered, large, elegant)
    person_name = getattr(resume.user.personal_info, 'full_name', None) if getattr(resume.user, 'personal_info', None) else None
    display_name = person_name or getattr(resume, 'name', '')
    p.setFont(font_bold, 30)
    p.setFillColor(colors.HexColor('#1a1a1a'))
    p.drawCentredString(width/2, y, display_name)
    y -= line_height + 10
    p.setStrokeColor(colors.HexColor('#bbbbbb'))
    p.setLineWidth(1)
    p.line(left_margin, y, right_margin, y)
    y -= section_gap
    p.setFillColor(colors.black)

    # Contact Info (single line, spaced, with hyperlinks)
    personal_info = getattr(resume.user, 'personal_info', None)
    if personal_info:
        p.setFont(font_main, 12)
        # Prepare the contact info parts
        # Prepare the contact info parts
    contact_parts = []
    contact_types = []  # Track the type for hyperlinking
    if personal_info.email:
        contact_parts.append(personal_info.email)
        contact_types.append('email')
    if personal_info.phone:
        contact_parts.append(personal_info.phone)
        contact_types.append('phone')
    if personal_info.address:
        contact_parts.append(personal_info.address)
        contact_types.append('address')
    # We'll add LinkedIn and GitHub as text placeholders for now
    if personal_info.linkedin:
        contact_parts.append('LinkedIn')
        contact_types.append('linkedin')
    if personal_info.github:
        contact_parts.append('GitHub')
        contact_types.append('github')
    contact_line = '   |   '.join(contact_parts)
    # Calculate starting x for centered line
    text_width = p.stringWidth(contact_line, font_main, 12)
    start_x = (width - text_width) / 2
    y_contact = y
    p.setFillColor(colors.black)
    p.drawString(start_x, y_contact, contact_line)
    # Now overlay hyperlinks for LinkedIn, GitHub, Email, and Phone
    x_cursor = start_x
    for idx, part in enumerate(contact_parts):
        part_width = p.stringWidth(part, font_main, 12)
        part_type = contact_types[idx]
        if part_type == 'linkedin' and personal_info.linkedin:
            p.setFillColor(colors.HexColor('#0074D9'))  # Brighter blue
            p.drawString(x_cursor, y_contact, part)
            p.linkURL(personal_info.linkedin, (x_cursor, y_contact-2, x_cursor+part_width, y_contact+12), relative=0)
            p.setFillColor(colors.black)
        elif part_type == 'github' and personal_info.github:
            p.setFillColor(colors.HexColor('#0074D9'))  # Brighter blue
            p.drawString(x_cursor, y_contact, part)
            p.linkURL(personal_info.github, (x_cursor, y_contact-2, x_cursor+part_width, y_contact+12), relative=0)
            p.setFillColor(colors.black)
        elif part_type == 'email' and personal_info.email:
            p.setFillColor(colors.HexColor('#0074D9'))
            p.drawString(x_cursor, y_contact, part)
            p.linkURL(f"mailto:{personal_info.email}", (x_cursor, y_contact-2, x_cursor+part_width, y_contact+12), relative=0)
            p.setFillColor(colors.black)
        elif part_type == 'phone' and personal_info.phone:
            p.setFillColor(colors.HexColor('#0074D9'))
            p.drawString(x_cursor, y_contact, part)
            p.linkURL(f"tel:{personal_info.phone}", (x_cursor, y_contact-2, x_cursor+part_width, y_contact+12), relative=0)
            p.setFillColor(colors.black)
        x_cursor += part_width + p.stringWidth('   |   ', font_main, 12)
        y -= line_height
        y -= section_gap

    # Bio
    if resume.bios:
        y = section_title("About", y)
        p.setFont(font_main, 12)
        for bio in resume.bios:
            y = check_page_break(y, 2*line_height)
            y = draw_wrapped_text(bio.bio, left_margin+10, y, right_margin-left_margin-20, font_main, 12)
        y -= section_gap

    # Education
    if resume.educations:
        y = section_title("Education", y)
        for edu in resume.educations:
            y = check_page_break(y, 3*line_height)
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{edu.uni}, {edu.location}")
            p.setFont(font_main, 11)
            p.drawRightString(right_margin, y, f"{edu.start_year} - {edu.end_year}")
            y -= line_height
            y = draw_wrapped_text(edu.degree or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11)
            y -= 6
        y -= section_gap

    # Experience
    if resume.experiences:
        y = section_title("Experience", y)
        for exp in resume.experiences:
            y = check_page_break(y, 4*line_height)
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, f"{exp.role} at {exp.comp}")
            y -= line_height
            p.setFont(font_main, 11)
            y = draw_wrapped_text(exp.desc or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11, bullet='•')
            y -= 6
        y -= section_gap

    # Projects
    if resume.projects:
        y = section_title("Projects", y)
        for proj in resume.projects:
            y = check_page_break(y, 4*line_height)
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, f"{proj.proj}")
            y -= line_height
            p.setFont(font_main, 10)
            y = draw_wrapped_text(f"Tools: {proj.tool}", left_margin+20, y, right_margin-left_margin-40, font_main, 10)
            p.setFont(font_main, 11)
            y = draw_wrapped_text(proj.desc or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11, bullet='•')
            y -= 6
        y -= section_gap

    # Skills
    if resume.skills:
        y = section_title("Skills", y)
        # Group skills by group name
        grouped = {}
        for skill in resume.skills:
            group = skill.group or 'Other'
            grouped.setdefault(group, []).append(skill.data)
        for group, skills in grouped.items():
            p.setFont(font_bold, 12)
            y = check_page_break(y, 2*line_height)
            p.drawString(left_margin+10, y, group + ':')
            y -= line_height
            p.setFont(font_main, 12)
            y = draw_wrapped_text(', '.join(skills), left_margin+30, y, right_margin-left_margin-40, font_main, 12)
        y -= 6
    p.save()
    buffer.seek(0)
    return buffer

def generate_resume_pdf_modern(resume):
    # This is a simple modern format for demonstration. You can enhance it further.
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = 40
    right_margin = width - 40
    y = height - 50
    line_height = 20
    section_gap = 36
    min_y = 80

    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'EBGaramond-Regular.ttf')
    try:
        pdfmetrics.registerFont(TTFont('EBGaramond', font_path))
        font_main = "EBGaramond"
        font_bold = "EBGaramond"
    except Exception:
        font_main = "Helvetica"
        font_bold = "Helvetica-Bold"

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
    person_name = getattr(resume.user.personal_info, 'full_name', None) if getattr(resume.user, 'personal_info', None) else None
    display_name = person_name or getattr(resume, 'name', '')
    p.setFont(font_bold, 28)
    p.setFillColor(colors.HexColor('#005f73'))
    p.drawString(left_margin, y, display_name)
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
        # Group skills by group name
        grouped = {}
        for skill in resume.skills:
            group = skill.group or 'Other'
            grouped.setdefault(group, []).append(skill.data)
        for group, skills in grouped.items():
            p.setFont(font_bold, 12)
            y = check_page_break(y, 2*line_height)
            p.drawString(left_margin+10, y, group + ':')
            y -= line_height
            p.setFont(font_main, 12)
            p.drawString(left_margin+30, y, ', '.join(skills))
            y -= line_height
        y -= section_gap
    p.save()
    buffer.seek(0)
    return buffer
