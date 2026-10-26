"""Routine builder: generation, chat mentor and evolution tracking."""

import json
import os
import tempfile

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.auth import token_required

bp = Blueprint('routine', __name__)


# Global progress manager instance (shared across requests)
_progress_manager_instance = None


def get_progress_manager():
    """Get or create global progress manager instance"""
    global _progress_manager_instance
    if _progress_manager_instance is None:
        from app.services.routine.progress_manager import ProgressManager
        _progress_manager_instance = ProgressManager()
    return _progress_manager_instance


@bp.route('/api/routine/evolution', methods=['GET', 'POST'])
@token_required
def get_routine_evolution(current_user):
    """
    Get evolution data with daily/monthly progress and excellence metrics
    
    Requires: Authorization header with Bearer token
    Query Parameters:
        - routineData: JSON string of routine data (optional)
    Returns: {
        success,
        dailyGraphData,
        monthlyGraphData,
        excellenceLevel,
        remainingSkills,
        motivationMessage,
        metrics
    }
    """
    try:
        from app.services.routine.evolution_tracker import EvolutionTracker
        
        # Get routine data from query params or request body
        routine_data = None
        if request.method == 'GET' and request.args.get('routineData'):
            try:
                routine_data = json.loads(request.args.get('routineData'))
            except:
                pass
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if data:
                routine_data = data.get('routineData')
        
        # Use shared progress manager
        manager = get_progress_manager()
        tracker = EvolutionTracker(manager)
        
        # Compute evolution
        result = tracker.compute_evolution(current_user, routine_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Evolution data fetch failed: {str(e)}'
        }), 500


@bp.route('/api/routine/progress', methods=['POST'])
@token_required
def update_routine_progress(current_user):
    """
    Update skill progress and recalculate metrics
    
    Requires: Authorization header with Bearer token
    Accepts: {
        week: int,
        skill: string,
        completionPercentage: float (0-100),
        date: string (ISO format),
        routineData: object
    }
    Returns: {success, progress_metrics, skill_progress}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['week', 'skill', 'completionPercentage', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        week = data['week']
        skill = data['skill']
        completion_percentage = data['completionPercentage']
        date = data['date']
        routine_data = data.get('routineData', None)
        
        # Validate types
        if not isinstance(week, int) or week < 1:
            return jsonify({
                'success': False,
                'message': 'Week must be a positive integer'
            }), 400
        
        if not isinstance(completion_percentage, (int, float)):
            return jsonify({
                'success': False,
                'message': 'Completion percentage must be a number'
            }), 400
        
        if not 0 <= completion_percentage <= 100:
            return jsonify({
                'success': False,
                'message': 'Completion percentage must be between 0 and 100'
            }), 400
        
        if not routine_data:
            return jsonify({
                'success': False,
                'message': 'Routine data is required'
            }), 400
        
        # Use shared progress manager
        manager = get_progress_manager()
        result = manager.update_progress(
            current_user,
            week,
            skill,
            completion_percentage,
            date,
            routine_data
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Progress update failed: {str(e)}'
        }), 500


@bp.route('/api/routine/chat', methods=['POST'])
@token_required
def routine_chat(current_user):
    """
    AI chat for routine guidance and support
    
    Requires: Authorization header with Bearer token
    Accepts: {
        userQuestion: string,
        routineData: object (optional),
        progressData: object (optional)
    }
    Returns: {success, response, action_items, category}
    """
    try:
        from app.services.routine.mistral_chat import get_mistral_chat
        
        data = request.get_json()
        
        if not data or 'userQuestion' not in data:
            return jsonify({
                'success': False,
                'message': 'userQuestion is required'
            }), 400
        
        user_question = data['userQuestion']
        routine_data = data.get('routineData', None)
        progress_data = data.get('progressData', None)
        
        # Validate question length
        if len(user_question.strip()) < 2:
            return jsonify({
                'success': False,
                'message': 'Question is too short'
            }), 400
        
        if len(user_question) > 1000:
            return jsonify({
                'success': False,
                'message': 'Question is too long (max 1000 characters)'
            }), 400
        
        # Generate AI response using Mistral (with automatic fallback)
        chat_ai = get_mistral_chat()
        result = chat_ai.generate_response(
            user_question,
            routine_data,
            progress_data
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': 'I encountered an error processing your question. Please try again.',
            'message': str(e)
        }), 500


@bp.route('/api/routine/generate', methods=['POST'])
@token_required
def generate_routine(current_user):
    """
    Generate personalized learning routine from uploaded analysis file
    
    Requires: Authorization header with Bearer token
    Accepts: multipart/form-data with:
        - file: Analysis report (JSON, PDF, or DOCX)
        - hoursPerWeek: Available study hours per week (optional, default 10)
    Returns: {success, routine}
    """
    try:
        
        # Import backend modules
        
        from app.services.routine.engine import RoutineEngineCore
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Get hours per week (default 10)
        hours_per_week = int(request.form.get('hoursPerWeek', 10))
        
        # Get user's domain override (sent from frontend localStorage)
        user_domain = request.form.get('userDomain', '').strip()
        
        if hours_per_week < 1 or hours_per_week > 168:
            return jsonify({
                'success': False,
                'message': 'Hours per week must be between 1 and 168'
            }), 400
        
        # Validate file type
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in ['json', 'pdf', 'docx']:
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only JSON, PDF, and DOCX are supported'
            }), 400
        
        # Save file temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"routine_{current_user}_{filename}")
        file.save(temp_path)
        
        try:
            # Generate routine using backend engine
            engine = RoutineEngineCore()
            result = engine.generate_routine(temp_path, file_ext, hours_per_week, user_domain)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Routine generation failed: {str(e)}'
        }), 500
