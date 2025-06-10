# LangGraph ChatBot

A web-based chatbot application powered by LangGraph with memory functionality. This chatbot maintains conversation history within threads (short-term memory) and can store user information across conversations (long-term memory).

## Features

- Interactive web interface with real-time responses
- Thread-based conversation management with unique thread IDs
- Short-term memory using InMemorySaver to maintain conversation history
- Long-term memory using InMemoryStore for user information
- System message context injection based on stored user information
- Markdown support in chat responses

## Requirements

- Python 3.8+
- Flask
- LangGraph
- LangChain
- OpenAI API key (or other supported LLM provider)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API key in the environment or update `chatbot.py`

## Running Locally

```
python app.py
```

The application will be available at http://localhost:5001

## Deployment

This application can be deployed to various platforms. Here are some options:

### Option 1: Render

1. Create a new account on [Render](https://render.com) if you don't have one
2. Click "New" and select "Blueprint" (or "Web Service" if you prefer manual setup)
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Add your `OPENAI_API_KEY` as an environment variable in the Render dashboard
6. Deploy the application

### Option 2: Heroku

1. Create a new app on [Heroku](https://heroku.com)
2. Connect your GitHub repository or use the Heroku CLI
3. Add your `OPENAI_API_KEY` as a config var in the Heroku dashboard
4. Deploy the application

### Option 3: Python Anywhere

1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your code or clone from GitHub
3. Set up a web app with Flask
4. Add your `OPENAI_API_KEY` as an environment variable
5. Configure the WSGI file to point to your app.py

### Option 4: Netlify, Vercel, or other platforms

This application can also be deployed to other platforms that support Python web applications. Please refer to the respective platform's documentation for deployment instructions.

## Project Structure

- `app.py`: Flask web server
- `chatbot.py`: LangGraph chatbot implementation with memory
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files
- `visualize_graph.py`: Utility for visualizing the LangGraph
