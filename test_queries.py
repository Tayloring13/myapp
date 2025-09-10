import requests
import urllib.parse

# Replace with your Railway project URL
BASE_URL = "https://myapp-production-14a4.up.railway.app/query"

# List of test queries
test_queries = [
    "Tell me about Tsurugaoka Hachimangu in Kamakura.",
    "What is the best time of year to visit Hase-dera, and what should I bring?",
    "Which attractions are near Hase-dera that a tourist shouldn’t miss?",
    "Explain the history of Kencho-ji temple and its significance in Kamakura.",
    "How does Hase-dera compare to other temples in Kamakura for scenery and photography?",
    "Are there any etiquette rules I should follow when visiting Japanese temples like Hase-dera?",
    "Describe the architectural style of Hase-dera, its main statues, and any famous festivals held there."
]

for q in test_queries:
    encoded_query = urllib.parse.quote(q)
    url = f"{BASE_URL}?q={encoded_query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"--- QUERY ---\n{q}\n")
        print(f"--- RESPONSE ---\n{data['response']}\n")
        print("="*60 + "\n")
    except Exception as e:
        print(f"Error with query '{q}': {e}\n")