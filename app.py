from flask import Flask, render_template, request, jsonify, session
import os
import uuid
import sys

# Initialize Flask app
app = Flask(__name__)

# Configure secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Check for OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY', '').strip()
if not api_key:
    print("⚠️ Warning: OPENAI_API_KEY environment variable is not set.")
    print("The application will start but chatbot functionality will be limited.")
    print("Please set the OPENAI_API_KEY in your Render dashboard.")

# Import the chatbot components with error handling
graph = None
State = None

try:
    from chatbot import graph, State
    print("✅ Chatbot components imported successfully")
except ImportError as e:
    print(f"❌ Error importing chatbot components: {e}")
    print("Make sure all dependencies are installed correctly.")
except Exception as e:
    print(f"❌ Unexpected error importing chatbot: {e}")

# Dictionary to store thread IDs for each session
thread_ids = {}

@app.route('/')
def home():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    status = {
        'status': 'healthy',
        'api_key_configured': bool(api_key),
        'graph_available': graph is not None
    }
    return jsonify(status)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        # Check if graph is available
        if graph is None:
            return jsonify({
                'error': 'Chatbot service is not available. Please check server configuration.'
            }), 503
        
        # Get request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        user_message = request_data.get('message', '').strip()
        session_id = request_data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create thread ID for this session
        if session_id not in thread_ids:
            thread_ids[session_id] = str(uuid.uuid4())
        
        thread_id = thread_ids[session_id]
        
        # Import the necessary message type
        from langchain_core.messages import HumanMessage
        
        # Create a proper HumanMessage object
        user_message_obj = HumanMessage(content=user_message)
        
        # Prepare the input and config for the graph
        input_state = {"messages": [user_message_obj]}
        config = {"configurable": {"thread_id": thread_id}}
        
        # Use the LangGraph to generate a response
        result = graph.invoke(input_state, config)
        
        # Extract the assistant's response
        if result and "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                assistant_message = last_message.content
            else:
                assistant_message = str(last_message)
        else:
            assistant_message = "I'm sorry, I couldn't generate a response. Please try again."
        
        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })
    
    except ImportError as e:
        print(f"❌ Import error in chat endpoint: {str(e)}")
        return jsonify({
            'error': "Required dependencies are not available. Please check server configuration."
        }), 503
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': f"An unexpected error occurred. Please try again later."
        }), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset conversation thread"""
    try:
        request_data = request.get_json()
        session_id = request_data.get('session_id') if request_data else None
        
        if session_id and session_id in thread_ids:
            # Generate a new thread ID for this session
            thread_ids[session_id] = str(uuid.uuid4())
            return jsonify({
                'status': 'success', 
                'message': 'Conversation reset successfully', 
                'session_id': session_id
            })
        else:
            # If no session ID provided or invalid, create a new one
            new_session_id = str(uuid.uuid4())
            thread_ids[new_session_id] = str(uuid.uuid4())
            return jsonify({
                'status': 'success',
                'message': 'New conversation started',
                'session_id': new_session_id
            })
            
    except Exception as e:
        print(f"❌ Error in reset endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to reset conversation. Please try again.'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Use environment variables for port with a fallback to 5001
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🔑 API key configured: {bool(api_key)}")
    print(f"🤖 Graph available: {graph is not None}")
    
    app.run(host='0.0.0.0', debug=debug_mode, port=port)