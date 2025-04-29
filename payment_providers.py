"""Configuration for supported payment providers"""

PAYMENT_PROVIDERS = {
    'stripe': {
        'name': 'Stripe',
        'base_url': 'https://docs.stripe.com',
        'api_base': 'https://api.stripe.com/v1',
        'docs_structure': {
            'main_sections': ['payments', 'billing', 'connect', 'terminal', 'issuing'],
            'api_reference': '/api'
        },
        'auth_methods': ['api_key', 'oauth'],
        'supported_languages': ['javascript', 'python', 'php', 'ruby', 'java', 'go', 'dotnet']
    },
    'paypal': {
        'name': 'PayPal',
        'base_url': 'https://developer.paypal.com',
        'api_base': 'https://api.paypal.com/v1',
        'docs_structure': {
            'main_sections': ['checkout', 'payments', 'subscriptions', 'invoicing'],
            'api_reference': '/docs/api/overview'
        },
        'auth_methods': ['client_credentials', 'oauth'],
        'supported_languages': ['javascript', 'python', 'php', 'java', 'dotnet']
    }
}

def get_provider_config(provider_id):
    """Get configuration for a specific provider"""
    return PAYMENT_PROVIDERS.get(provider_id.lower())

def get_supported_providers():
    """Get list of supported providers"""
    return list(PAYMENT_PROVIDERS.keys())

def get_provider_languages(provider_id):
    """Get supported languages for a provider"""
    config = get_provider_config(provider_id)
    if config:
        return config.get('supported_languages', [])
    return []