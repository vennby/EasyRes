from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
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
    return render_template("home.html", user=current_user)

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

@views.route('/download-resume')
@login_required
def download_resume():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, f"{current_user.first_name}")
    y -= 30

    # Experience
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Experience:")
    y -= 20
    p.setFont("Helvetica", 12)
    for exp in current_user.experiences:
        p.drawString(60, y, f"{exp.role} at {exp.comp} ({exp.start_date} to {exp.end_date or 'Present'})")
        y -= 20
        p.drawString(70, y, exp.desc[:90])
        y -= 30

    # Education
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Education:")
    y -= 20
    p.setFont("Helvetica", 12)
    for edu in current_user.educations:
        p.drawString(60, y, f"{edu.uni}, {edu.location} — {edu.degree} ({edu.start_year} to {edu.end_year})")
        y -= 30

    # Projects
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Projects:")
    y -= 20
    p.setFont("Helvetica", 12)
    for proj in current_user.projects:
        p.drawString(60, y, f"{proj.proj} (Tools: {proj.tool})")
        y -= 20
        p.drawString(70, y, proj.desc[:90])
        y -= 30

    # Skills
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Skills:")
    y -= 20
    p.setFont("Helvetica", 12)
    skills = ', '.join(skill.data for skill in current_user.skills)
    p.drawString(60, y, skills)

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="resume.pdf", mimetype='application/pdf')