document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const resetBtn = document.getElementById('reset-btn');
    
    // Store session ID for conversation memory
    let sessionId = localStorage.getItem('chatSessionId') || null;

    // Function to sanitize HTML to prevent XSS attacks
    function sanitizeHTML(text) {
        const element = document.createElement('div');
        element.textContent = text;
        return element.innerHTML;
    }
    
    // Function to convert simple markdown to HTML
    function markdownToHTML(text) {
        if (!text) return '';
        
        // Sanitize the input first
        let html = sanitizeHTML(text);
        
        // Convert line breaks to <br>
        html = html.replace(/\n/g, '<br>');
        
        // Convert markdown-style bold (**text**) to <strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown-style italic (*text*) to <em>
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert markdown-style code blocks (```code```) to <pre><code>
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Convert markdown-style inline code (`code`) to <code>
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Preserve multiple spaces
        html = html.replace(/ {2,}/g, function(match) {
            return '&nbsp;'.repeat(match.length);
        });
        
        return html;
    }
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // For user messages, simple text is fine
        // For bot messages, we want to preserve formatting
        if (isUser) {
            const messageParagraph = document.createElement('p');
            messageParagraph.textContent = content;
            messageContent.appendChild(messageParagraph);
        } else {
            // For bot messages, use our markdown converter
            messageContent.innerHTML = markdownToHTML(content);
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator message bot';
        indicator.id = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicator.appendChild(dot);
        }
        
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Function to send a message
    function sendMessage() {
        const message = userInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input field
            userInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send message to server with session ID
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: sessionId
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Store session ID if provided
                if (data.session_id) {
                    sessionId = data.session_id;
                    localStorage.setItem('chatSessionId', sessionId);
                }
                
                // Add bot response to chat
                if (data.response) {
                    addMessage(data.response);
                } else if (data.error) {
                    addMessage('Error: ' + data.error);
                }
            })
            .catch(error => {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add error message
                addMessage('Error: Could not connect to the server.');
                console.error('Error:', error);
            });
        }
    }

    // Function to reset the chat
    function resetChat() {
        // Clear chat messages except the first welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Reset conversation on the server
        fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
            
            // Update session ID if a new one is provided
            if (data.session_id) {
                sessionId = data.session_id;
                localStorage.setItem('chatSessionId', sessionId);
            }
            
            // Add system message about reset
            addMessage('Conversation has been reset. Start a new chat!');
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    resetBtn.addEventListener('click', resetChat);
});
