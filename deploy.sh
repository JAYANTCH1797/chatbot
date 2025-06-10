#!/bin/bash
# Deployment script for LangGraph Chatbot with Memory

echo "🚀 Preparing to deploy LangGraph Chatbot with Memory..."

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    npm install -g @render/cli
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY environment variable is not set."
    echo "You will need to set this in your deployment platform's environment variables."
fi

# Create a .env file for local testing (ignored by git)
if [ ! -f .env ]; then
    echo "Creating .env file for local development..."
    echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
    echo "PORT=5001" >> .env
    echo ".env file created (this is ignored by git)"
fi

# Ensure all dependencies are installed
echo "Installing dependencies..."
pip install -r requirements.txt

# Run a quick test to make sure everything works
echo "Testing application..."
python -c "from chatbot import graph; print('✅ LangGraph import successful')"

echo "✅ Deployment preparation complete!"
echo ""
echo "To deploy to Render.com:"
echo "1. Create a new Web Service on Render"
echo "2. Connect your GitHub repository"
echo "3. Use the following settings:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn app:app"
echo "4. Add the OPENAI_API_KEY environment variable"
echo ""
echo "Your application is ready to be deployed!"
