import requests

API_URL = "http://localhost:8000/chatbot"

def run_kb_agent(question: str):
    try:
        response = requests.post(API_URL, json={"query": question})
        response.raise_for_status()
        print("KB Retrieval process")
        # print(response.json().get("results", "No results found"))
        return response.json().get("results", "No results found")  # Return the full JSON from the API
    except requests.RequestException as e:
        return {"error": f"Error contacting KB API: {e}"}
