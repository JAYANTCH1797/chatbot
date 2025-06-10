const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Simple response for the chatbot API
exports.handler = async (event, context) => {
  // Get the path and method
  const path = event.path.replace(/\.netlify\/functions\/[^/]+/, '');
  const method = event.httpMethod;

  // Serve the index.html for the root path
  if (path === '/' && method === 'GET') {
    try {
      const htmlPath = './templates/index.html';
      const html = fs.readFileSync(htmlPath, 'utf8');
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'text/html' },
        body: html
      };
    } catch (err) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Failed to load HTML', details: err.message })
      };
    }
  }

  // Handle chat API endpoint
  if (path === '/chat' && method === 'POST') {
    try {
      const body = JSON.parse(event.body);
      const message = body.message || '';
      const sessionId = body.session_id || 'default-session';

      // For demo purposes, just echo back the message
      // In a real deployment, this would integrate with your LangGraph backend
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          response: `You said: "${message}". This is a static response from the Netlify function. For the full chatbot experience with LangGraph and memory functionality, please run the app locally.`,
          session_id: sessionId
        })
      };
    } catch (err) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Failed to process chat request', details: err.message })
      };
    }
  }

  // Handle reset API endpoint
  if (path === '/reset' && method === 'POST') {
    try {
      const body = JSON.parse(event.body);
      const sessionId = body.session_id || 'default-session';

      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'Conversation reset successfully (static response)',
          session_id: sessionId
        })
      };
    } catch (err) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Failed to reset conversation', details: err.message })
      };
    }
  }

  // Handle static assets
  if (path.startsWith('/static/')) {
    try {
      const filePath = '.' + path;
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const contentType = path.endsWith('.css') ? 'text/css' : 
                           path.endsWith('.js') ? 'application/javascript' : 
                           'text/plain';
        return {
          statusCode: 200,
          headers: { 'Content-Type': contentType },
          body: content
        };
      }
    } catch (err) {
      // Fall through to 404
    }
  }

  // Default 404 response
  return {
    statusCode: 404,
    body: JSON.stringify({ error: 'Not found' })
  };
};

