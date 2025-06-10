from flask import Flask, render_template, request, jsonify, session
import os
import uuid
import sys

# Initialize Flask app
app = Flask(__name__)

# Configure secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Check for OpenAI API key
if not os.environ.get('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY environment variable is not set.")
    print("The application may not function correctly without an API key.")

# Import the chatbot components with error handling
try:
    from chatbot import graph, State
except ImportError as error:
    print(f"Error importing chatbot components: {error}")
    print("Make sure all dependencies are installed correctly.")
    # Don't exit here to allow the app to start even with errors

# Dictionary to store thread IDs for each session
thread_ids = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    session_id = request.json.get('session_id', str(uuid.uuid4()))
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create thread ID for this session
    if session_id not in thread_ids:
        thread_ids[session_id] = str(uuid.uuid4())
    
    thread_id = thread_ids[session_id]
    
    try:
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
            assistant_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            assistant_message = "I'm sorry, I couldn't generate a response."
        
        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })
    
    except Exception as error:
        print(f"Error in chat endpoint: {str(error)}")
        return jsonify({'error': f"An error occurred: {str(error)}"}), 500

@app.route('/reset', methods=['POST'])
def reset():
    try:
        session_id = request.json.get('session_id')
        
        if session_id and session_id in thread_ids:
            # Generate a new thread ID for this session
            thread_ids[session_id] = str(uuid.uuid4())
            return jsonify({
                'status': 'success', 
                'message': 'Conversation reset', 
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
    except Exception as error:
        print(f"Error in reset endpoint: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': f"An error occurred: {str(error)}"
        }), 500

if __name__ == '__main__':
    # Use environment variables for port with a fallback to 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', debug=False, port=port)
