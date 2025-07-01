from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file, abort
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import *
from . import db
import os, io, json

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template("home.html", user=current_user, resumes=resumes)

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'bio' in request.form:
            return add_bio(
                request.form.get('bio')
            )
        if 'uni' in request.form:
            return add_education(
                request.form.get('uni'),
                request.form.get('location'),
                request.form.get('degree'),
                request.form.get('start_year'),
                request.form.get('end_year')
            )
        if 'role' in request.form:
            return add_experience(
                request.form.get('role'),
                request.form.get('comp'),
                request.form.get('desc'),
                request.form.get('start_date'),
                request.form.get('end_date'),
                request.form.get('ongoing')
            )
        if 'proj' in request.form:
            return add_project(
                request.form.get('proj'),
                request.form.get('tool'),
                request.form.get('desc')
            )
        elif 'skill' in request.form:
            return add_skill(request.form.get('skill'))
    
    return render_template("profile.html", user=current_user)

def add_bio(bio):
    bio = request.form.get('bio')
    
    new_bio = Bios(
        bio = bio,
        user_id=current_user.id
    )
    
    db.session.add(new_bio)
    db.session.commit()
    flash("Bio added!", category='success')
    return redirect(url_for('views.profile'))

def add_education(uni, location, degree, start_year, end_year):
    uni = request.form.get('uni')
    location = request.form.get('location')
    degree = request.form.get('degree')
    start_year = request.form.get('start_year')
    end_year = request.form.get('end_year')

    new_education = Educations(
        uni=uni,
        location=location,
        degree = degree,
        start_year = start_year,
        end_year = end_year,
        user_id=current_user.id
    )
    
    db.session.add(new_education)
    db.session.commit()
    flash("Education added!", category='success')
    return redirect(url_for('views.profile'))

def add_experience(role, comp, desc, start_date, end_date, ongoing):
    role = request.form.get('role')
    comp = request.form.get('comp')
    desc = request.form.get('desc')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    ongoing = request.form.get('ongoing') == 'on'

    new_experience = Experiences(
        role=role,
        comp=comp,
        desc=desc,
        start_date=start_date,
        end_date=end_date if not ongoing else None,
        ongoing=ongoing,
        user_id=current_user.id
    )
    db.session.add(new_experience)
    db.session.commit()
    flash("Experience added!", category='success')
    return redirect(url_for('views.profile'))

def add_project(proj, tool, desc):
    new_project = Projects(
        proj=proj,
        tool=tool,
        desc=desc,
        user_id=current_user.id
    )

    db.session.add(new_project)
    db.session.commit()
    flash("Project added!", category='success')
    return redirect(url_for('views.profile'))

def add_skill(skill_data):
    if len(skill_data) > 20:
        flash("Skill must be smaller than 20 characters!", category='error')
    else:
        new_skill = Skills(data=skill_data, user_id=current_user.id)
        db.session.add(new_skill)
        db.session.commit()
        flash("Skill added!", category='success')
    return redirect(url_for('views.profile'))

@views.route('/delete-bio', methods=['POST'])
@login_required
def delete_bio():
    bio_data = json.loads(request.data)
    bio_id = bio_data['bioId']
    bio = Bios.query.get(bio_id)
    if bio and bio.user_id == current_user.id:
        db.session.delete(bio)
        db.session.commit()
    return jsonify({})

@views.route('/delete-education', methods=['POST'])
def delete_education():
    education_data = json.loads(request.data)
    education_id = education_data['educationId']
    education = Educations.query.get(education_id)
    if education and education.user_id == current_user.id:
        db.session.delete(education)
        db.session.commit()
    return jsonify({})

@views.route('/delete-experience', methods=['POST'])
def delete_experience():
    experience_data = json.loads(request.data)
    experience_id = experience_data['experienceId']
    experience = Experiences.query.get(experience_id)
    if experience and experience.user_id == current_user.id:
        db.session.delete(experience)
        db.session.commit()
    return jsonify({})

@views.route('/delete-project', methods=['POST'])
def delete_project():
    project_data = json.loads(request.data)
    project_id = project_data['projectId']
    project = Projects.query.get(project_id)
    if project and project.user_id == current_user.id:
        db.session.delete(project)
        db.session.commit()
    return jsonify({})

@views.route('/delete-skill', methods=['POST'])
def delete_skill():
    skill = json.loads(request.data)
    skillId = skill['skillId']
    skill = Skills.query.get(skillId)
    if skill:
        if skill.user_id == current_user.id:
            db.session.delete(skill)
            db.session.commit()
    return jsonify({})

# List all resumes for the current user
@views.route('/resumes')
@login_required
def list_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template('resumes.html', resumes=resumes, user=current_user)

# Create a new resume (GET: show form, POST: save selections)
@views.route('/resume/create', methods=['GET', 'POST'])
@login_required
def create_resume():
    if request.method == 'POST':
        name = request.form.get('name')
        bio_ids = request.form.getlist('bios')
        education_ids = request.form.getlist('educations')
        experience_ids = request.form.getlist('experiences')
        project_ids = request.form.getlist('projects')
        skill_ids = request.form.getlist('skills')
        resume = Resume(name=name, user_id=current_user.id)
        resume.bios = Bios.query.filter(Bios.id.in_(bio_ids)).all() if bio_ids else []
        resume.educations = Educations.query.filter(Educations.id.in_(education_ids)).all() if education_ids else []
        resume.experiences = Experiences.query.filter(Experiences.id.in_(experience_ids)).all() if experience_ids else []
        resume.projects = Projects.query.filter(Projects.id.in_(project_ids)).all() if project_ids else []
        resume.skills = Skills.query.filter(Skills.id.in_(skill_ids)).all() if skill_ids else []
        db.session.add(resume)
        db.session.commit()
        flash('Resume created!', category='success')
        return redirect(url_for('views.list_resumes'))
    # GET: show selection form
    return render_template('resume_form.html',
        user=current_user,
        bios=current_user.bios,
        educations=current_user.educations,
        experiences=current_user.experiences,
        projects=current_user.projects,
        skills=current_user.skills,
        resume=None
    )

# Edit a resume
@views.route('/resume/<int:resume_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        resume.name = request.form.get('name')
        bio_ids = request.form.getlist('bios')
        education_ids = request.form.getlist('educations')
        experience_ids = request.form.getlist('experiences')
        project_ids = request.form.getlist('projects')
        skill_ids = request.form.getlist('skills')
        resume.bios = Bios.query.filter(Bios.id.in_(bio_ids)).all() if bio_ids else []
        resume.educations = Educations.query.filter(Educations.id.in_(education_ids)).all() if education_ids else []
        resume.experiences = Experiences.query.filter(Experiences.id.in_(experience_ids)).all() if experience_ids else []
        resume.projects = Projects.query.filter(Projects.id.in_(project_ids)).all() if project_ids else []
        resume.skills = Skills.query.filter(Skills.id.in_(skill_ids)).all() if skill_ids else []
        db.session.commit()
        flash('Resume updated!', category='success')
        return redirect(url_for('views.list_resumes'))
    return render_template('resume_form.html',
        user=current_user,
        bios=current_user.bios,
        educations=current_user.educations,
        experiences=current_user.experiences,
        projects=current_user.projects,
        skills=current_user.skills,
        resume=resume
    )

# Delete a resume
@views.route('/resume/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    db.session.delete(resume)
    db.session.commit()
    flash('Resume deleted!', category='success')
    return redirect(url_for('views.list_resumes'))

# Fetch a single resume (for edit)
@views.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    return render_template('resume_preview.html', resume=resume, user=current_user)

@views.route('/resume/<int:resume_id>/download')
@login_required
def download_specific_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = 50
    right_margin = width - 50
    y = height - 60
    line_height = 18
    section_gap = 28

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
        print(f"Warning: EB Garamond font not found or could not be loaded. Using Helvetica instead. Error: {e}")

    def draw_wrapped_text(text, x, y, max_width, font, font_size):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line = ''
        for word in words:
            test_line = f'{line} {word}'.strip()
            if stringWidth(test_line, font, font_size) < max_width:
                line = test_line
            else:
                p.drawString(x, y, line)
                y -= line_height
                line = word
        if line:
            p.drawString(x, y, line)
            y -= line_height
        return y

    # Name (centered, large, elegant)
    p.setFont(font_bold, 28)
    p.drawCentredString(width/2, y, f"{resume.name}")
    y -= line_height + 10
    p.setStrokeColorRGB(0.2, 0.2, 0.2)
    p.setLineWidth(1)
    p.line(left_margin, y, right_margin, y)
    y -= section_gap

    def section_title(title, y):
        p.setFont(font_bold, 16)
        p.drawString(left_margin, y, title)
        y -= line_height
        p.setLineWidth(0.5)
        p.setStrokeColorRGB(0.7, 0.7, 0.7)
        p.line(left_margin, y+6, right_margin, y+6)
        y -= 6
        return y

    # Bio
    if resume.bios:
        y = section_title("BIO", y)
        p.setFont(font_main, 12)
        for bio in resume.bios:
            y = draw_wrapped_text(bio.bio, left_margin+10, y, right_margin-left_margin-20, font_main, 12)
        y -= section_gap
    # Education
    if resume.educations:
        y = section_title("EDUCATION", y)
        p.setFont(font_main, 12)
        for edu in resume.educations:
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{edu.uni}, {edu.location}")
            p.setFont(font_main, 11)
            p.drawRightString(right_margin, y, f"{edu.start_year} - {edu.end_year}")
            y -= line_height
            y = draw_wrapped_text(edu.degree or '', left_margin+10, y, right_margin-left_margin-20, font_main, 11)
            y -= 8
            if y < 100:
                p.showPage()
                y = height - 60
        y -= section_gap
    # Experience
    if resume.experiences:
        y = section_title("EXPERIENCE", y)
        p.setFont(font_main, 12)
        for exp in resume.experiences:
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{exp.role} at {exp.comp}")
            p.setFont(font_main, 11)
            y = draw_wrapped_text(exp.desc or '', left_margin+10, y, right_margin-left_margin-20, font_main, 11)
            y -= 8
            if y < 100:
                p.showPage()
                y = height - 60
        y -= section_gap
    # Projects
    if resume.projects:
        y = section_title("PROJECTS", y)
        p.setFont(font_main, 12)
        for proj in resume.projects:
            p.setFont(font_bold, 13)
            p.drawString(left_margin, y, f"{proj.proj}")
            y -= line_height
            tools_indent = left_margin + 30
            p.setFont(font_main, 10)
            y = draw_wrapped_text(f"Tools: {proj.tool}", tools_indent, y, right_margin-tools_indent, font_main, 10)
            p.setFont(font_main, 11)
            y = draw_wrapped_text(proj.desc or '', left_margin+10, y, right_margin-left_margin-20, font_main, 11)
            y -= 8
            if y < 100:
                p.showPage()
                y = height - 60
        y -= section_gap
    # Skills
    if resume.skills:
        y = section_title("SKILLS", y)
        p.setFont(font_main, 12)
        skills = ', '.join(skill.data for skill in resume.skills)
        y = draw_wrapped_text(skills, left_margin, y, right_margin-left_margin, font_main, 12)
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{resume.name}.pdf", mimetype='application/pdf')