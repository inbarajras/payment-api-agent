import re
from typing import Dict, List, Optional

class IntentRecognizer:
    def __init__(self):
        # Define intents with their patterns
        self.intents = {
            'authentication': [
                r'(how to|how do I) (authenticate|connect|setup|set up|authorize)',
                r'(api keys|credentials|tokens|authentication)',
                r'(connect|integrate|setup) (my|the) (account|api)'
            ],
            'payment_processing': [
                r'(how to|how do I) (process|create|make|accept) (a |)payment',
                r'(charge|transaction|payment) (processing|flow)',
                r'accept (credit card|payment)'
            ],
            'subscription': [
                r'(recurring|subscription) (payment|billing)',
                r'(create|setup|manage) (a |)(subscription|recurring payment)'
            ],
            'refund': [
                r'(how to|how do I) (refund|return|cancel) (a |)(payment|transaction)',
                r'(process|issue) (a |)(refund|return)'
            ],
            'error_handling': [
                r'(error|exception|problem|issue|troubleshoot)',
                r'(not working|failed|failing)'
            ],
            'language_preference': [
                r'(in|using|with) (javascript|python|ruby|php|java|node|nodejs|\.net|c#)'
            ]
        }

    def detect_provider(self, query: str) -> Optional[str]:
        query = query.lower()
        if 'stripe' in query:
            return 'stripe'
        elif 'paypal' in query:
            return 'paypal'
        return None

    def detect_language(self, query: str) -> Optional[str]:
        query = query.lower()
        languages = {
            'javascript': ['javascript', 'js', 'node', 'nodejs'],
            'python': ['python', 'py'],
            'php': ['php'],
            'ruby': ['ruby'],
            'java': ['java'],
            'c#': ['c#', '.net', 'dotnet'],
        }

        for lang, keywords in languages.items():
            if any(keyword in query for keyword in keywords):
                return lang
        return None

    def recognize(self, query: str) -> Dict:
        query = query.lower()
        matched_intents = []

        # Check for each intent
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    matched_intents.append(intent)
                    break

        return {
            'matched_intents': list(set(matched_intents)),
            'payment_provider': self.detect_provider(query),
            'programming_language': self.detect_language(query),
            'query': query
        }
