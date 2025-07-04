from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file, abort
from flask_login import login_required, current_user
from .models import *
from . import db
from .pdf_utils import generate_resume_pdf
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

@views.route('/update-personal-info', methods=['POST'])
@login_required
def update_personal_info():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    linkedin = request.form.get('linkedin')
    github = request.form.get('github')
    website = request.form.get('website')

    personal_info = PersonalInfo.query.filter_by(user_id=current_user.id).first()
    if not personal_info:
        personal_info = PersonalInfo(user_id=current_user.id)
        db.session.add(personal_info)

    personal_info.full_name = full_name
    personal_info.email = email
    personal_info.phone = phone
    personal_info.address = address
    personal_info.linkedin = linkedin
    personal_info.github = github
    personal_info.website = website
    db.session.commit()
    flash('Personal information updated!', category='success')
    return redirect(url_for('views.profile'))

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
        return redirect(url_for('views.home'))
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
        return redirect(url_for('views.home'))
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
    return redirect(url_for('views.home'))

@views.route('/resume/<int:resume_id>/preview_pdf')
@login_required
def preview_resume_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    buffer = generate_resume_pdf(resume)
    buffer.seek(0)
    return send_file(buffer, as_attachment=False, download_name=f"{resume.name}.pdf", mimetype='application/pdf')

@views.route('/resume/<int:resume_id>/download')
@login_required
def download_specific_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    buffer = generate_resume_pdf(resume)
    return send_file(buffer, as_attachment=True, download_name=f"{resume.name}.pdf", mimetype='application/pdf')