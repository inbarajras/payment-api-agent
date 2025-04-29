import unittest
import json
import os
import tempfile
import sys
import shutil

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intent_recognizer import IntentRecognizer
from vector_store import VectorStore
from code_generator import CodeGenerator
from payment_api_agent import PaymentAPIAgent

class TestPaymentAPIAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Create mock vector store data
        os.makedirs(os.path.join(self.test_dir, "paypal"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "stripe"), exist_ok=True)

        # Create mock embeddings data
        mock_embeddings = [
            {
                "document_id": "doc1",
                "chunk_id": 0,
                "title": "Processing Payments",
                "text": "To process a payment with Stripe, you need to create a PaymentIntent.",
                "category": "payment_processing",
                "embedding": [0.1] * 384  # Mock embedding vector
            },
            {
                "document_id": "doc2",
                "chunk_id": 0,
                "title": "Authentication",
                "text": "To authenticate with PayPal, you need to get API credentials from your dashboard.",
                "category": "authentication",
                "embedding": [0.2] * 384  # Mock embedding vector
            }
        ]

        with open(os.path.join(self.test_dir, "paypal", "embeddings.json"), "w") as f:
            json.dump(mock_embeddings, f)

        with open(os.path.join(self.test_dir, "stripe", "embeddings.json"), "w") as f:
            json.dump(mock_embeddings, f)

        # Create mock code templates
        self.templates_dir = tempfile.mkdtemp()
        mock_templates = {
            "stripe_payment_processing_javascript": {
                "code": "const stripe = require('stripe')('YOUR_KEY'); const charge = await stripe.paymentIntents.create({});",
                "explanation": "Test template",
                "requires": ["stripe package"]
            },
            "paypal_authentication_python": {
                "code": "import paypalrestsdk; paypalrestsdk.configure({ 'mode': 'sandbox', 'client_id': 'YOUR_ID', 'client_secret': 'YOUR_SECRET' })",
                "explanation": "Test template",
                "requires": ["paypalrestsdk package"]
            }
        }

        with open(os.path.join(self.templates_dir, "templates.json"), "w") as f:
            json.dump(mock_templates, f)

        # Initialize components
        self.intent_recognizer = IntentRecognizer()
        self.vector_stores = {
            'paypal': VectorStore(os.path.join(self.test_dir, "paypal", "embeddings.json")),
            'stripe': VectorStore(os.path.join(self.test_dir, "stripe", "embeddings.json"))
        }
        self.code_generator = CodeGenerator(self.templates_dir)

        # Initialize agent
        self.agent = PaymentAPIAgent(
            self.intent_recognizer,
            self.vector_stores,
            self.code_generator
        )

    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.templates_dir)

    def test_intent_recognition(self):
        """Test intent recognition module"""
        query = "How do I process a payment with Stripe using JavaScript?"
        result = self.intent_recognizer.recognize(query)

        self.assertIn('payment_processing', result['matched_intents'])
        self.assertEqual('stripe', result['payment_provider'])
        self.assertEqual('javascript', result['programming_language'])

    def test_code_generation(self):
        """Test code generation module"""
        code = self.code_generator.generate_code(
            intent="payment_processing",
            provider="stripe",
            language="javascript"
        )

        self.assertIn("stripe.paymentIntents.create", code['code'])
        self.assertEqual("javascript", code['language'])

    def test_query_processing(self):
        """Test full query processing"""
        query = "How do I authenticate with PayPal using Python?"
        response = self.agent.process_query(query)

        self.assertIsNotNone(response)
        self.assertIn("message", response)
        self.assertIn("PayPal", response["message"])

    def test_missing_provider(self):
        """Test handling of missing provider information"""
        query = "How do I process a payment?"
        response = self.agent.process_query(query)

        self.assertIn("missing_info", response)
        self.assertEqual("payment_provider", response["missing_info"])

    def test_conversation_history(self):
        """Test that conversation history is maintained"""
        # First query
        query1 = "I'm using Stripe"
        self.agent.process_query(query1)

        # Second query should use the provider from history
        query2 = "How do I process a payment?"
        response = self.agent.process_query(query2)

        self.assertNotIn("missing_info", response)
        self.assertIn("Stripe", response["message"])

if __name__ == "__main__":
    unittest.main()