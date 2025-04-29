from flask import Flask, request, jsonify, render_template
import os
import json
import argparse

# Import all necessary components (assuming they're defined in separate modules)
from intent_recognizer import IntentRecognizer
from vector_store import VectorStore
from code_generator import CodeGenerator
from payment_api_agent import PaymentAPIAgent, PaymentAPIAgentWithLLM
from llm_service import LLMService

app = Flask(__name__)


# Initialize the agent
def initialize_agent(use_llm=True):
    # This is the same initialization function from Phase 6
    print("Initializing Payment API Integration Agent...")
    # At the beginning of initialize_agent function, add:
    print(f"LLM flag is set to: {use_llm}")
    print(f"LLM_API_KEY environment variable is {'set' if os.environ.get('LLM_API_KEY') else 'NOT set'}")

    # Create directories if they don't exist
    directories = [
        "knowledge_base/paypal",
        "knowledge_base/stripe",
        "structured_knowledge",
        "vector_db/paypal",
        "vector_db/stripe",
        "code_examples"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Step 1: Initialize the intent recognizer
    print("Initializing intent recognizer...")
    intent_recognizer = IntentRecognizer()

    # Step 2: Create mock vector stores for this example
    # In production, you'd run the scraping and embedding scripts first
    print("Initializing vector stores...")
    try:
        paypal_store = VectorStore("vector_db/paypal/embeddings.json")
        stripe_store = VectorStore("vector_db/stripe/embeddings.json")
        vector_stores = {
            'stripe': stripe_store,
            'paypal': paypal_store
        }
    except FileNotFoundError:
        # Create mock vector stores with empty data
        print("Vector store files not found. Creating mock stores...")
        for provider in ['paypal', 'stripe']:
            os.makedirs(f"vector_db/{provider}", exist_ok=True)
            with open(f"vector_db/{provider}/embeddings.json", 'w') as f:
                json.dump([], f)

        # Retry loading
        paypal_store = VectorStore("vector_db/paypal/embeddings.json")
        stripe_store = VectorStore("vector_db/stripe/embeddings.json")
        vector_stores = {
            'stripe': stripe_store,
            'paypal': paypal_store
        }

    # Step 3: Initialize code generator
    print("Initializing code generator...")
    # Create sample templates if not exists
    templates_file = "code_examples/templates.json"
    if not os.path.exists(templates_file):
        example_templates = {
            "stripe_payment_processing_javascript": {
                "code": "const stripe = require('stripe')('YOUR_STRIPE_SECRET_KEY');\n\nasync function createPayment() {\n  try {\n    const paymentIntent = await stripe.paymentIntents.create({\n      amount: 1000, // Amount in cents\n      currency: 'usd',\n      payment_method_types: ['card'],\n      description: 'Software development services',\n    });\n    return paymentIntent;\n  } catch (error) {\n    console.error('Error creating payment:', error);\n  }\n}",
                "explanation": "This code creates a PaymentIntent in Stripe, which is the recommended way to accept payments. The amount is in cents (1000 = $10.00).",
                "requires": ["stripe npm package"]
            },
            "stripe_payment_processing_python": {
                "code": "import stripe\n\n# Set your API key\nstripe.api_key = \"YOUR_STRIPE_SECRET_KEY\"\n\ndef create_payment():\n    try:\n        payment_intent = stripe.PaymentIntent.create(\n            amount=1000,  # Amount in cents\n            currency=\"usd\",\n            payment_method_types=[\"card\"],\n            description=\"Software development services\",\n        )\n        return payment_intent\n    except Exception as e:\n        print(f\"Error creating payment: {e}\")\n        return None",
                "explanation": "This Python function creates a PaymentIntent in Stripe. You'll need to install the stripe package first with pip.",
                "requires": ["stripe Python package"]
            }
        }
        os.makedirs("code_examples", exist_ok=True)
        with open(templates_file, 'w') as f:
            json.dump(example_templates, f)

    code_generator = CodeGenerator("code_examples")

    # Step 4: Initialize LLM service if requested
    if True:
        print("Initializing LLM service...")
        api_key = os.environ.get("LLM_API_KEY")
        if not api_key:
            print("Warning: LLM_API_KEY environment variable not set")
            print("Please set your API key: export LLM_API_KEY=your_key_here")

        llm_service = LLMService(api_key=api_key)
        agent = PaymentAPIAgentWithLLM(intent_recognizer, vector_stores, code_generator, llm_service)
        print("Agent with LLM integration initialized!")
    else:
        # Use the base agent without LLM
        agent = PaymentAPIAgent(intent_recognizer, vector_stores, code_generator)
        print("Base agent initialized!")

    return agent


# Parse command line arguments
parser = argparse.ArgumentParser(description="Payment API Integration Agent")
parser.add_argument("--llm", action="store_true", help="Enable LLM integration")
args, _ = parser.parse_known_args()

# Initialize the agent
agent = initialize_agent(use_llm=args.llm)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        response = agent.process_query(user_query)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_documentation():
    # This endpoint would trigger the documentation scraping process
    try:
        data = request.json
        provider = data.get('provider', 'stripe')
        if provider not in ['stripe', 'paypal']:
            return jsonify({"error": "Invalid provider"}), 400

        # Here you would call your scraping function
        # For now, we'll just return a success message
        return jsonify({"status": "Scraping initiated for " + provider})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
