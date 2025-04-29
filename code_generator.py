import json
from typing import Dict, Optional

class CodeGenerator:
    def __init__(self, code_examples_dir: str):
        # Load code templates
        with open(f"{code_examples_dir}/templates.json", 'r') as f:
            self.templates = json.load(f)

    def generate_code(self, intent: str, provider: str, language: str, parameters: Dict = None) -> Dict:
        """Generate code snippet based on intent, provider and language"""
        # Default to empty dict if no parameters provided
        if parameters is None:
            parameters = {}

        # Find appropriate template
        template_key = f"{provider}_{intent}_{language}"
        if template_key in self.templates:
            template = self.templates[template_key]

            # Simple template substitution
            code = template['code']
            for key, value in parameters.items():
                placeholder = f"{{{key}}}"
                code = code.replace(placeholder, str(value))

            return {
                'code': code,
                'language': language,
                'explanation': template['explanation'],
                'requires': template.get('requires', [])
            }
        else:
            # Fallback - find closest match by removing constraints
            fallbacks = [
                f"{provider}_{intent}_javascript",  # Try JavaScript as default language
                f"{provider}_payment_processing_{language}",  # Try payment processing as default intent
                "stripe_payment_processing_javascript"  # Ultimate fallback
            ]

            for fallback in fallbacks:
                if fallback in self.templates:
                    template = self.templates[fallback]
                    return {
                        'code': template['code'],
                        'language': fallback.split('_')[-1],
                        'explanation': template['explanation'] + "\n(Note: This is a fallback example.)",
                        'requires': template.get('requires', [])
                    }

            # If all else fails
            return {
                'code': "// No suitable code example found",
                'language': language or 'javascript',
                'explanation': "Could not find a suitable code example for this combination.",
                'requires': []
            }

# Example code templates (in practice you'd have this in an external JSON file)
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

#

