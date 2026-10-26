"""Resume analysis (Analyze feature)."""

import base64
import traceback
from io import BytesIO

from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.extensions import db, limiter
from app.models.explore_cache import UserAnalysisCache

bp = Blueprint('analysis', __name__)


@bp.route('/api/analyze-resume', methods=['POST'])
@token_required
@limiter.limit("10 per minute")
def analyze_resume_comprehensive(current_user):
    """
    Comprehensive resume analysis with NLP and PDF generation
    Requires: Authorization header with Bearer token
    Accepts: multipart/form-data with optional 'resume' file and JSON data
    Returns: Complete analysis with download link
    """
    try:
        
        from app.services.analysis.resume_analyzer import ResumeAnalyzer
        from app.services.analysis.skill_engine import SkillEngine
        from app.services.analysis.report_generator import ReportGenerator
        
        # Initialize analyzers
        resume_analyzer = ResumeAnalyzer()
        skill_engine = SkillEngine()
        report_generator = ReportGenerator()
        
        # Get form data
        current_domain = request.form.get('currentDomain', '')
        target_domain = request.form.get('targetDomain', 'Software Development')
        experience_years = int(request.form.get('experienceYears', 0))
        manual_skills = request.form.get('manualSkills', '')
        project_descriptions = request.form.get('projectDescriptions', '')
        certifications = request.form.get('certifications', '')
        strength_level = request.form.get('strengthLevel', 'Intermediate')
        
        # Parse manual inputs
        manual_skills_list = [s.strip() for s in manual_skills.split(',') if s.strip()] if manual_skills else []
        manual_projects = [p.strip() for p in project_descriptions.split('\n') if p.strip()] if project_descriptions else []
        manual_certs = [c.strip() for c in certifications.split(',') if c.strip()] if certifications else []
        
        # Initialize variables
        resume_data = None
        extracted_skills = []
        resume_text = ""
        
        # Process resume if uploaded
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                # Read file into BytesIO
                file_stream = BytesIO(file.read())
                
                # Analyze resume
                resume_data = resume_analyzer.analyze_resume(file_stream, file.filename)
                extracted_skills = resume_data['extracted_skills']
                resume_text = resume_data['cleaned_text']
        
        # Merge skills from resume and manual entry
        all_skills = skill_engine.merge_skills(extracted_skills, manual_skills_list)
        user_skills_set = skill_engine.normalize_skills(all_skills)
        
        # Merge projects and certifications
        all_projects = (resume_data['projects'] if resume_data else []) + manual_projects
        all_certs = (resume_data['certifications'] if resume_data else []) + manual_certs
        
        # Calculate readiness score
        readiness_score = skill_engine.calculate_readiness_score(
            user_skills_set,
            target_domain,
            experience_years,
            len(all_projects) > 0,
            len(all_certs) > 0
        )
        
        # Identify missing skills
        missing_skills = skill_engine.identify_missing_skills(user_skills_set, target_domain)
        
        # Calculate resume strength
        resume_strength = skill_engine.calculate_resume_strength(
            resume_text if resume_text else manual_skills + project_descriptions,
            all_skills,
            all_projects,
            all_certs,
            experience_years
        )
        
        # Detect mistakes
        mistakes = skill_engine.detect_mistakes(
            resume_text if resume_text else manual_skills + project_descriptions,
            all_projects
        )
        
        # Generate suggestions
        suggestions = skill_engine.generate_suggestions(
            readiness_score['total_score'],
            missing_skills,
            resume_strength,
            mistakes
        )
        
        # Suggest domains
        suggested_domains = skill_engine.suggest_domains(user_skills_set, top_n=5)
        
        # Prepare analysis data
        analysis_data = {
            'extracted_skills': all_skills,
            'readiness_score': readiness_score,
            'resume_strength': resume_strength,
            'missing_skills': missing_skills,
            'mistakes': mistakes,
            'suggestions': suggestions,
            'suggested_domains': suggested_domains,
            'experience_years': experience_years,
            'projects_count': len(all_projects),
            'certifications_count': len(all_certs),
        }
        
        # Generate PDF report
        user_info = {
            'name': 'User',  # TODO: Get from database
            'domain': target_domain,
        }
        
        pdf_buffer = report_generator.generate_report(analysis_data, user_info)
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
        
        # Save analyze result to Explore personalization cache (non-blocking)
        try:
            cache = UserAnalysisCache.query.filter_by(user_id=current_user).first()
            if not cache:
                cache = UserAnalysisCache(user_id=current_user)
                db.session.add(cache)
            cache.readiness_score = int(readiness_score['total_score'])
            cache.target_domain = target_domain
            cache.extracted_skills = all_skills[:30]
            cache.missing_skills = missing_skills[:15]
            db.session.commit()
        except Exception:
            pass  # Never block analyze if cache write fails

        # Return comprehensive response
        return jsonify({
            'success': True,
            'analysis': {
                'extracted_skills': all_skills,
                'total_skills': len(all_skills),
                'readiness_score': readiness_score['total_score'],
                'readiness_details': readiness_score,
                'resume_strength': resume_strength['total_strength'],
                'resume_strength_details': resume_strength,
                'confidence_level': readiness_score['confidence_level'],
                'missing_skills': missing_skills,
                'mistakes': mistakes,
                'suggestions': suggestions,
                'suggested_domains': suggested_domains,
                'experience_years': experience_years,
                'projects_count': len(all_projects),
                'certifications_count': len(all_certs),
            },
            'pdf_report': pdf_base64,
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Analysis failed: {str(e)}'
        }), 500


@bp.route('/api/analyze/upload', methods=['POST'])
@token_required
def analyze_upload(current_user):
    """
    Legacy endpoint - redirects to comprehensive analysis
    """
    return analyze_resume_comprehensive()


@bp.route('/api/analyze/manual', methods=['POST'])
@token_required
@limiter.limit("10 per minute")
def analyze_manual(current_user):
    """
    Analyze manually entered skills
    Requires: Authorization header with Bearer token
    Accepts: {skills: string, domain: string}
    Returns: {success, extracted_skills, readiness_score, suggested_domains, missing_skills}
    """
    try:
        data = request.get_json()
        
        if 'skills' not in data or 'domain' not in data:
            return jsonify({
                'success': False,
                'message': 'Skills and domain are required'
            }), 400
        
        skills_text = data['skills']
        domain = data['domain']
        
        # TODO: Process the manual input
        # 1. Parse skills from text
        # 2. Match against domain requirements
        # 3. Calculate readiness score
        # 4. Suggest related domains
        # 5. Identify skill gaps
        
        # Mock response (replace with actual analysis)
        # Parse skills from comma-separated text
        entered_skills = [s.strip() for s in skills_text.split(',') if s.strip()]
        
        return jsonify({
            'success': True,
            'extracted_skills': entered_skills,
            'readiness_score': 68,
            'suggested_domains': [
                domain,
                'Related Domain 1',
                'Related Domain 2'
            ],
            'missing_skills': [
                'Advanced Skill 1',
                'Advanced Skill 2',
                'Industry Tool 1',
                'Best Practice 1'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
