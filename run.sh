#!/bin/bash

# Setup environment
echo "Setting up environment..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Check if API key is set
if [ -z "$LLM_API_KEY" ]; then
    echo "Warning: LLM_API_KEY not set. LLM features will be disabled."
    USE_LLM=""
else
    echo "LLM_API_KEY found. LLM features will be enabled."
    USE_LLM="--llm"
fi

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt')"

# Initialize data directories
echo "Initializing data directories..."
mkdir -p knowledge_base/paypal knowledge_base/stripe structured_knowledge vector_db/paypal vector_db/stripe code_examples

# Run the web application
echo "Starting the Payment API Integration Agent..."
python app.py $USE_LLM