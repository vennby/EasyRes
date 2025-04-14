from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'skill' in request.form:
            return add_skill(request.form.get('skill'))
        elif 'role' in request.form:
            return add_experience(
                request.form.get('role'),
                request.form.get('comp'),
                request.form.get('desc'),
                request.form.get('start_date'),
                request.form.get('end_date'),
                request.form.get('ongoing')
            )
    
    return render_template("profile.html", user=current_user)

def add_skill(skill_data):
    # Check skill length constraint
    if len(skill_data) > 20:
        flash("Skill must be smaller than 20 characters!", category='error')
    else:
        new_skill = Skills(data=skill_data, user_id=current_user.id)
        db.session.add(new_skill)
        db.session.commit()
        flash("Skill added!", category='success')
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

@views.route('/delete-experience', methods=['POST'])
def delete_experience():
    experience_data = json.loads(request.data)
    experience_id = experience_data['experienceId']
    experience = Experiences.query.get(experience_id)
    if experience and experience.user_id == current_user.id:
        db.session.delete(experience)
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