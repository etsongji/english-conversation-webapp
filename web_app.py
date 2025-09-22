"""
Flask Web Application for English Conversation Practice
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import uuid

# Import our modules
from config import Config, initialize_config
from ai_tutor import AITutorService, ConversationTopics

# Initialize configuration
try:
    initialize_config()
except Exception as e:
    print(f"Configuration initialization failed: {e}")

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Enable CORS and SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
ai_service = None

def init_services():
    """Initialize AI service"""
    global ai_service
    try:
        ai_service = AITutorService()
        if ai_service.is_available:
            logger.info(f"AI service initialized: {ai_service.provider}")
        else:
            logger.warning("AI service not available")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_available': ai_service.is_available if ai_service else False
    })

@app.route('/api/topics')
def get_topics():
    """Get available conversation topics"""
    return jsonify({
        'topics': ConversationTopics.TOPICS
    })

@app.route('/api/start-topic', methods=['POST'])
def start_topic():
    """Start conversation with a specific topic"""
    data = request.get_json()
    topic = data.get('topic', 'daily_life')
    
    try:
        starter = ConversationTopics.get_random_starter(topic)
        return jsonify({
            'success': True,
            'message': starter,
            'topic': topic
        })
    except Exception as e:
        logger.error(f"Error starting topic: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not ai_service or not ai_service.is_available:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 503
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({
            'success': False,
            'error': 'Empty message'
        }), 400
    
    try:
        # Get AI response
        ai_response = ai_service.get_response(user_message)
        
        # Get conversation stats
        stats = ai_service.get_stats()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get AI response'
        }), 500

@app.route('/api/conversation/save', methods=['POST'])
def save_conversation():
    """Save current conversation"""
    if not ai_service:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 503
    
    try:
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        saved_path = ai_service.save_conversation(filename)
        
        if saved_path:
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Conversation saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save conversation'
            }), 500
            
    except Exception as e:
        logger.error(f"Save conversation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversation/clear', methods=['POST'])
def clear_conversation():
    """Clear current conversation"""
    if not ai_service:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 503
    
    try:
        ai_service.clear_conversation()
        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get conversation statistics"""
    if not ai_service:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 503
    
    try:
        stats = ai_service.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# SocketIO Events for real-time features
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {
        'connected': True,
        'ai_available': ai_service.is_available if ai_service else False
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('message')
def handle_message(data):
    """Handle real-time chat messages"""
    if not ai_service or not ai_service.is_available:
        emit('error', {'message': 'AI service not available'})
        return
    
    user_message = data.get('message', '').strip()
    if not user_message:
        emit('error', {'message': 'Empty message'})
        return
    
    try:
        # Get AI response
        ai_response = ai_service.get_response(user_message)
        
        # Get updated stats
        stats = ai_service.get_stats()
        
        # Send response back to client
        emit('response', {
            'user_message': user_message,
            'ai_response': ai_response,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"SocketIO message error: {e}")
        emit('error', {'message': 'Failed to get AI response'})

if __name__ == '__main__':
    # Initialize services
    init_services()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Production mode on Railway
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode
        socketio.run(app, host='0.0.0.0', port=port, debug=True)