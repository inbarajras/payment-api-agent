# Payment API Integration Agent

This project creates an AI agent that helps developers integrate payment APIs like Stripe and PayPal into their applications.

## Features

- Intelligent query understanding for payment API integration questions
- Documentation search across Stripe and PayPal APIs
- Code generation for common payment operations
- Context-aware conversation handling
- Optional LLM enhancement for natural responses

## Project Structure

```
payment-api-agent/
│
├── app.py                 # Main application file
├── intent_recognizer.py   # Intent recognition module
├── vector_store.py        # Vector database for documentation search
├── code_generator.py      # Code generation functionality
├── payment_api_agent.py   # Core agent logic
├── llm_service.py         # LLM integration (optional)
├── scraper.py             # Documentation scraper
├── embedder.py            # Document embedding creator
├── populate_kb.py         # Knowledge base population script
│
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container orchestration
├── run.sh                 # Launch script
│
├── templates/             # Web UI templates
│   └── index.html         # Main interface
│
├── knowledge_base/        # Raw scraped documentation
│   ├── paypal/
│   └── stripe/
│
├── structured_knowledge/  # Processed documentation
│   ├── paypal.json
│   └── stripe.json
│
├── vector_db/            # Vector embeddings for search
│   ├── paypal/
│   └── stripe/
│
└── code_examples/        # Code templates
    └── templates.json
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)
- Docker (optional, for containerized deployment)

### Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/payment-api-agent.git
   cd payment-api-agent
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your LLM API key (optional):
   ```
   export LLM_API_KEY=your_api_key_here
   ```

5. Populate the knowledge base:
   ```
   python populate_kb.py
   ```

6. Run the application:
   ```
   python app.py
   ```

The web interface will be available at http://localhost:5000

### Docker Deployment

1. Build and start the container:
   ```
   docker-compose up -d
   ```

2. The web interface will be available at http://localhost:5000

## Usage

Once the application is running, you can:

1. Open the web interface in your browser
2. Ask questions about integrating Stripe or PayPal
3. Get code examples and implementation guidance

## Configuration

The agent can be configured through environment variables:

- `LLM_API_KEY`: Your API key for the LLM service
- `FLASK_ENV`: Set to `development` for debug mode

## Adding More Payment Providers

To add support for additional payment APIs:

1. Add the new provider to the scraper configuration in `scraper.py`
2. Run the knowledge base population script with the new provider:
   ```
   python populate_kb.py --provider new_provider
   ```
3. Update the code generator templates in `code_examples/templates.json` to include examples for the new provider

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
