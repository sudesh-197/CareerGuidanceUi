"""Routine progress tracking (weekly progress, summary and analytics)."""

import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.auth import token_required
from app.extensions import db
from app.models.progress import RoutineProgress

bp = Blueprint('progress', __name__)


@bp.route('/api/routine/progress/weekly', methods=['GET'])
@token_required
def get_weekly_progress(current_user):
    """
    Get user's weekly progress for all topics
    
    Requires: Authorization header with Bearer token
    Query Parameters:
        - skill: Filter by skill (optional)
    Returns: {success, progress}
    """
    try:
        
        skill_filter = request.args.get('skill')
        
        # Build query
        query = RoutineProgress.query.filter_by(user_id=current_user)
        
        if skill_filter:
            query = query.filter_by(skill=skill_filter)
        
        # Get all progress records
        progress_records = query.order_by(RoutineProgress.week_number).all()
        
        return jsonify({
            'success': True,
            'progress': [record.to_dict() for record in progress_records],
            'count': len(progress_records)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/routine/progress/weekly', methods=['POST'])
@token_required
def update_weekly_progress(current_user):
    """
    Update completion status for a specific week/topic
    
    Requires: Authorization header with Bearer token
    Accepts: {
        skill: string,
        week_number: int,
        topic: string,
        completed: boolean
    }
    Returns: {success, progress, message}
    """
    try:
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['skill', 'week_number', 'topic', 'completed']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        skill = data['skill']
        week_number = data['week_number']
        topic = data['topic']
        completed = data['completed']
        
        # Validate types
        if not isinstance(week_number, int) or week_number < 1:
            return jsonify({
                'success': False,
                'message': 'Week number must be a positive integer'
            }), 400
        
        if not isinstance(completed, bool):
            return jsonify({
                'success': False,
                'message': 'Completed must be a boolean'
            }), 400
        
        # Check if record exists
        progress_record = RoutineProgress.query.filter_by(
            user_id=current_user,
            skill=skill,
            week_number=week_number,
            topic=topic
        ).first()
        
        if progress_record:
            # Update existing record
            progress_record.completed = completed
            progress_record.completed_at = datetime.datetime.utcnow() if completed else None
            progress_record.updated_at = datetime.datetime.utcnow()
        else:
            # Create new record
            progress_record = RoutineProgress(
                user_id=current_user,
                skill=skill,
                week_number=week_number,
                topic=topic,
                completed=completed,
                completed_at=datetime.datetime.utcnow() if completed else None
            )
            db.session.add(progress_record)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress': progress_record.to_dict(),
            'message': f'Progress updated: {topic} marked as {"completed" if completed else "incomplete"}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/routine/progress/summary', methods=['GET'])
@token_required
def get_progress_summary(current_user):
    """
    Get progress summary with completion statistics per skill
    
    Requires: Authorization header with Bearer token
    Returns: {success, summary}
    """
    try:
        
        # Get completion stats per skill
        stats = db.session.query(
            RoutineProgress.skill,
            func.count(RoutineProgress.id).label('total_topics'),
            func.sum(db.case((RoutineProgress.completed == True, 1), else_=0)).label('completed_topics')
        ).filter_by(
            user_id=current_user
        ).group_by(
            RoutineProgress.skill
        ).all()
        
        summary = []
        for skill, total, completed in stats:
            completed = completed or 0
            completion_percentage = (completed / total * 100) if total > 0 else 0
            
            # Determine status
            if completion_percentage >= 80:
                status = 'Achieved'
            elif completion_percentage >= 50:
                status = 'In Progress'
            elif completion_percentage > 0:
                status = 'Started'
            else:
                status = 'Not Started'
            
            summary.append({
                'skill': skill,
                'total_topics': total,
                'completed_topics': completed,
                'completion_percentage': round(completion_percentage, 1),
                'status': status
            })
        
        return jsonify({
            'success': True,
            'summary': summary,
            'total_skills': len(summary)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/routine/evolution/analytics', methods=['GET'])
@token_required
def get_evolution_analytics(current_user):
    """
    Get evolution analytics with graph-ready data
    
    Requires: Authorization header with Bearer token
    Query Parameters:
        - skill: Filter by skill (optional)
    Returns: {
        success,
        analytics: {
            daily_progress: [{date, completed_topics, cumulative_topics}],
            weekly_progress: [{week_number, completed_topics, remaining_topics, completion_rate}],
            skill_completion: [{skill, total_topics, completed_topics, completion_percentage, status}],
            overall_metrics: {total_topics, completed_topics, remaining_topics, overall_completion_rate, ...}
        }
    }
    """
    try:
        from app.services.routine.evolution_analytics import EvolutionAnalytics
        
        skill_filter = request.args.get('skill')
        
        # Build query
        query = RoutineProgress.query.filter_by(user_id=current_user)
        
        if skill_filter:
            query = query.filter_by(skill=skill_filter)
        
        # Get all progress records
        progress_records = query.all()
        
        # Convert to dict format
        progress_data = [record.to_dict() for record in progress_records]
        
        # Generate analytics
        analytics_engine = EvolutionAnalytics()
        analytics = analytics_engine.generate_analytics(progress_data)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
