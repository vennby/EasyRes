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

def generate_classic_resume(resume):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin, right_margin = 50, width - 50
    y = height - 60
    line_height = 18
    section_gap = 30
    min_y = 80

    font_main, font_bold = register_fonts()

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
        y = check_page_break(y, 2 * line_height)
        p.setFont(font_bold, 14)
        p.setFillColor(colors.HexColor('#111111'))
        p.drawString(left_margin, y, title.upper())
        y -= 8
        p.setStrokeColor(colors.HexColor('#cccccc'))
        p.setLineWidth(1)
        p.line(left_margin, y, right_margin, y)
        y -= line_height
        p.setFillColor(colors.black)
        return y

    person_name = getattr(resume.user.personal_info, 'full_name', None) if getattr(resume.user, 'personal_info', None) else getattr(resume, 'name', '')
    p.setFont(font_bold, 30)
    p.setFillColor(colors.HexColor('#1a1a1a'))
    p.drawCentredString(width / 2, y, person_name)
    y -= line_height + 10
    p.setStrokeColor(colors.HexColor('#bbbbbb'))
    p.setLineWidth(1)
    p.line(left_margin, y, right_margin, y)
    y -= section_gap

    personal_info = getattr(resume.user, 'personal_info', None)
    if personal_info:
        p.setFont(font_main, 12)
        contact_parts = []
        contact_types = []
        if personal_info.email:
            contact_parts.append(personal_info.email)
            contact_types.append('email')
        if personal_info.phone:
            contact_parts.append(personal_info.phone)
            contact_types.append('phone')
        if personal_info.linkedin:
            contact_parts.append('LinkedIn')
            contact_types.append('linkedin')
        if personal_info.github:
            contact_parts.append('GitHub')
            contact_types.append('github')

        contact_line = '   •   '.join(contact_parts)
        x_start = left_margin
        p.setFillColor(colors.black)
        p.drawString(x_start, y, contact_line)
        x_cursor = x_start
        for idx, part in enumerate(contact_parts):
            part_width = p.stringWidth(part, font_main, 12)
            part_type = contact_types[idx]
            if part_type == 'linkedin':
                p.linkURL(personal_info.linkedin, (x_cursor, y-2, x_cursor+part_width, y+12))
            elif part_type == 'github':
                p.linkURL(personal_info.github, (x_cursor, y-2, x_cursor+part_width, y+12))
            elif part_type == 'email':
                p.linkURL(f"mailto:{personal_info.email}", (x_cursor, y-2, x_cursor+part_width, y+12))
            elif part_type == 'phone':
                p.linkURL(f"tel:{personal_info.phone}", (x_cursor, y-2, x_cursor+part_width, y+12))
            x_cursor += part_width + p.stringWidth('   •   ', font_main, 12)
        y -= line_height
        y -= section_gap

    if resume.bios:
        y = section_title("About", y)
        p.setFont(font_main, 12)
        for bio in resume.bios:
            y = draw_wrapped_text(bio.bio, left_margin+10, y, right_margin-left_margin-20, font_main, 12)
        y -= section_gap

    if resume.educations:
        y = section_title("Education", y)
        for edu in resume.educations:
            y = check_page_break(y, 3 * line_height)
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{edu.uni}, {edu.location}")
            p.setFont(font_main, 11)
            date_range = f"{edu.start_year or ''} - {edu.end_year or ''}".strip(' -')
            p.drawRightString(right_margin, y, date_range)
            y -= line_height
            y = draw_wrapped_text(edu.degree or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11)
            y -= 6
        y -= section_gap

    if resume.experiences:
        y = section_title("Experience", y)
        for exp in resume.experiences:
            y = check_page_break(y, 4 * line_height)
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, f"{exp.role} at {exp.comp}")
            y -= line_height
            p.setFont(font_main, 11)
            y = draw_wrapped_text(exp.desc or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11, bullet='•')
            y -= 6
        y -= section_gap

    if resume.projects:
        y = section_title("Projects", y)
        for proj in resume.projects:
            y = check_page_break(y, 4 * line_height)
            p.setFont(font_bold, 12)
            p.drawString(left_margin, y, f"{proj.proj}")
            y -= line_height
            p.setFont(font_main, 10)
            y = draw_wrapped_text(f"Tools: {proj.tool}", left_margin+20, y, right_margin-left_margin-40, font_main, 10)
            p.setFont(font_main, 11)
            y = draw_wrapped_text(proj.desc or '', left_margin+20, y, right_margin-left_margin-40, font_main, 11, bullet='•')
            y -= 6
        y -= section_gap

    if resume.skills:
        y = section_title("Skills", y)
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