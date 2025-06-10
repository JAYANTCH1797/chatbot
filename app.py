from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from chatbot import graph, State

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

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
        # Prepare the input and config for the graph
        input_state = {"messages": [{"role": "user", "content": user_message}]}
        config = {"configurable": {"thread_id": thread_id}}
        
        # Use the LangGraph to generate a response
        result = graph.invoke(input_state, config)
        
        # Extract the assistant's response
        assistant_message = result["messages"][-1].content
        
        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    session_id = request.json.get('session_id')
    
    if session_id and session_id in thread_ids:
        # Generate a new thread ID for this session
        thread_ids[session_id] = str(uuid.uuid4())
        return jsonify({
            'status': 'Conversation reset successfully',
            'session_id': session_id
        })
    else:
        # If no session ID provided, create a new one
        new_session_id = str(uuid.uuid4())
        thread_ids[new_session_id] = str(uuid.uuid4())
        return jsonify({
            'status': 'New conversation started',
            'session_id': new_session_id
        })

if __name__ == '__main__':
    # Use environment variables for port with a fallback to 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', debug=False, port=port)
