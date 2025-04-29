import requests
import time
import sys
import os

def test_web_agent():
    """Test the web interface of the payment API agent"""
    base_url = "http://localhost:5000"

    # Check if the server is running
    try:
        response = requests.get(base_url, timeout=2)
        if response.status_code != 200:
            print("Server is not responding correctly. Status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to the server. Make sure it's running on http://localhost:5000")
        return False

    print("✅ Server is running")

    # Test queries
    test_queries = [
        "How do I set up authentication with Stripe?",
        "I want to process a payment with PayPal using Python",
        "How do I handle subscription billing?",
        "What's the code for refunding a payment in JavaScript?",
        "How do I troubleshoot payment errors?"
    ]

    success_count = 0

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: '{query}'")
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"query": query},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if "message" in data and len(data["message"]) > 50:
                    print(f"✅ Got valid response ({len(data['message'])} chars)")
                    success_count += 1
                else:
                    print("❌ Response too short or invalid format")
                    print(data)
            else:
                print(f"❌ Error status code: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ Exception during test: {e}")

        # Sleep between requests
        time.sleep(1)

    print(f"\nTests completed: {success_count}/{len(test_queries)} successful")
    return success_count == len(test_queries)

if __name__ == "__main__":
    print("Running end-to-end tests for Payment API Integration Agent")
    success = test_web_agent()
    sys.exit(0 if success else 1)