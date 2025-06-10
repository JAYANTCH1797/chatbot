import json
from flask import Flask, request, jsonify, render_template, Response
import os
import uuid
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from chatbot import graph, State

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Dictionary to store thread IDs for each session
thread_ids = {}

def handler(event, context):
    """Netlify function handler"""
    # Parse the request from the event
    path = event.get('path', '').replace('/.netlify/functions/app', '')
    http_method = event.get('httpMethod', '')
    
    # Create a mock request object for Flask
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': None,
        'wsgi.errors': None,
    }
    
    # If this is a POST request, add the body
    if http_method == 'POST':
        body = json.loads(event.get('body', '{}'))
        environ['wsgi.input'] = body
    
    # Handle different routes
    if path == '/' and http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': render_template('index.html')
        }
    elif path == '/chat' and http_method == 'POST':
        return handle_chat(body)
    elif path == '/reset' and http_method == 'POST':
        return handle_reset(body)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

def handle_chat(request_data):
    """Handle chat requests"""
    user_message = request_data.get('message', '')
    session_id = request_data.get('session_id', str(uuid.uuid4()))
    
    if not user_message:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No message provided'})
        }
    
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
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': assistant_message,
                'session_id': session_id
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_reset(request_data):
    """Handle reset requests"""
    session_id = request_data.get('session_id')
    
    if session_id and session_id in thread_ids:
        # Generate a new thread ID for this session
        thread_ids[session_id] = str(uuid.uuid4())
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'Conversation reset successfully',
                'session_id': session_id
            })
        }
    else:
        # If no session ID provided, create a new one
        new_session_id = str(uuid.uuid4())
        thread_ids[new_session_id] = str(uuid.uuid4())
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'New conversation started',
                'session_id': new_session_id
            })
        }
