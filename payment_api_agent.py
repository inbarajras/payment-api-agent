import json
from typing import Dict, List, Optional

class PaymentAPIAgent:
    def __init__(self, intent_recognizer, vector_stores, code_generator):
        self.intent_recognizer = intent_recognizer
        self.vector_stores = vector_stores  # Dict mapping provider to vector store
        self.code_generator = code_generator
        self.conversation_history = []

    def process_query(self, query: str) -> Dict:
        # Recognize intent
        intent_data = self.intent_recognizer.recognize(query)

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Determine if we need to ask for missing information
        response = self.handle_missing_info(intent_data)
        if response:
            return response

        # Choose provider
        provider = intent_data['payment_provider']

        # Search documentation
        if provider and provider in self.vector_stores:
            vector_store = self.vector_stores[provider]
            search_results = vector_store.search(query, top_k=3)
        else:
            # If no provider specified, search both
            search_results = []
            for p, store in self.vector_stores.items():
                if provider is None or p == provider:
                    results = store.search(query, top_k=2)
                    for r in results:
                        r['provider'] = p
                    search_results.extend(results)

        # Generate code if needed
        code_snippet = None
        if any(intent in intent_data['matched_intents'] for intent in ['authentication', 'payment_processing', 'subscription', 'refund']):
            # Use the first matched intent for code generation
            for intent in intent_data['matched_intents']:
                if intent in ['authentication', 'payment_processing', 'subscription', 'refund']:
                    primary_intent = intent
                    break
            else:
                primary_intent = 'payment_processing'  # Default

            code_snippet = self.code_generator.generate_code(
                intent=primary_intent,
                provider=provider or 'stripe',  # Default to Stripe if not specified
                language=intent_data['programming_language'] or 'javascript'  # Default to JS
            )

        # Prepare response
        response = self.format_response(intent_data, search_results, code_snippet)

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response['message']
        })

        return response

    def handle_missing_info(self, intent_data: Dict) -> Optional[Dict]:
        """Check if we need more information from the user"""
        if not intent_data['payment_provider'] and not self.has_previous_provider():
            return {
                "message": "Which payment provider are you working with? PayPal or Stripe?",
                "missing_info": "payment_provider",
                "options": ["PayPal", "Stripe"]
            }

        if any(intent in intent_data['matched_intents'] for intent in ['authentication', 'payment_processing', 'subscription', 'refund']) and not intent_data['programming_language'] and not self.has_previous_language():
            return {
                "message": "What programming language are you using for the integration?",
                "missing_info": "programming_language",
                "options": ["JavaScript", "Python", "PHP", "Ruby", "Java", "C#"]
            }

        return None

    def has_previous_provider(self) -> bool:
        """Check if a payment provider was mentioned in conversation history"""
        for msg in self.conversation_history:
            if msg["role"] == "user":
                if "paypal" in msg["content"].lower():
                    return True
                if "stripe" in msg["content"].lower():
                    return True
        return False

    def has_previous_language(self) -> bool:
        """Check if a programming language was mentioned in conversation history"""
        languages = ["javascript", "python", "php", "ruby", "java", "c#", "node"]
        for msg in self.conversation_history:
            if msg["role"] == "user":
                if any(lang in msg["content"].lower() for lang in languages):
                    return True
        return False

    def format_response(self, intent_data: Dict, search_results: List[Dict], code_snippet: Optional[Dict]) -> Dict:
        """Format a helpful response based on the available information"""
        provider = intent_data['payment_provider'] or "payment provider"

        # Start with a greeting that acknowledges the intent
        if 'authentication' in intent_data['matched_intents']:
            message = f"I'll help you set up authentication with {provider.capitalize()}.\n\n"
        elif 'payment_processing' in intent_data['matched_intents']:
            message = f"Let's process payments with {provider.capitalize()}.\n\n"
        elif 'subscription' in intent_data['matched_intents']:
            message = f"I'll show you how to implement subscription billing with {provider.capitalize()}.\n\n"
        elif 'refund' in intent_data['matched_intents']:
            message = f"Here's how to handle refunds with {provider.capitalize()}.\n\n"
        elif 'error_handling' in intent_data['matched_intents']:
            message = f"Let's troubleshoot your {provider.capitalize()} integration.\n\n"
        else:
            message = f"Here's some information about working with {provider.capitalize()}.\n\n"

        # Add documentation insights
        if search_results:
            message += "Based on the documentation:\n\n"
            for i, result in enumerate(search_results[:2], 1):
                message += f"{i}. {result['text']}\n\n"
                if 'url' in result:
                    message += f"   Source: {result['url']}\n\n"

        # Add code snippet if available
        if code_snippet:
            lang = code_snippet['language']
            message += f"Here's a code example in {lang}:\n\n```{lang}\n{code_snippet['code']}\n```\n\n"
            message += f"{code_snippet['explanation']}\n\n"

            if code_snippet['requires']:
                message += "Required dependencies:\n"
                for req in code_snippet['requires']:
                    message += f"- {req}\n"
                message += "\n"

        # Add follow-up suggestion
        message += "Is there anything specific about this implementation you'd like me to explain further?"

        return {
            "message": message,
            "intent_data": intent_data,
            "documentation": search_results[:3] if search_results else []
        }

class PaymentAPIAgentWithLLM(PaymentAPIAgent):
    def __init__(self, intent_recognizer, vector_stores, code_generator, llm_service):
        super().__init__(intent_recognizer, vector_stores, code_generator)
        self.llm_service = llm_service

    def process_query(self, query: str) -> Dict:
        # Recognize intent
        intent_data = self.intent_recognizer.recognize(query)

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Determine if we need to ask for missing information
        response = self.handle_missing_info(intent_data)
        if response:
            return response

        # Choose provider
        provider = intent_data['payment_provider']

        # Search documentation
        search_results = []
        for p, store in self.vector_stores.items():
            if provider is None or p == provider:
                results = store.search(query, top_k=3)
                for r in results:
                    r['provider'] = p
                search_results.extend(results)

        # Generate code if needed
        code_snippet = None
        if any(intent in intent_data['matched_intents'] for intent in ['authentication', 'payment_processing', 'subscription', 'refund']):
            for intent in intent_data['matched_intents']:
                if intent in ['authentication', 'payment_processing', 'subscription', 'refund']:
                    primary_intent = intent
                    break
            else:
                primary_intent = 'payment_processing'

            code_snippet = self.code_generator.generate_code(
                intent=primary_intent,
                provider=provider or 'stripe',
                language=intent_data['programming_language'] or 'javascript'
            )

        # Prepare messages for LLM
        messages = []
        for msg in self.conversation_history[-5:]:  # Use last 5 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Generate response with LLM using documentation context
        llm_response = self.llm_service.generate_response(
            messages=messages,
            context=search_results + ([code_snippet] if code_snippet else [])
        )

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": llm_response
        })

        return {
            "message": llm_response,
            "intent_data": intent_data,
            "documentation": search_results[:3] if search_results else []
        }