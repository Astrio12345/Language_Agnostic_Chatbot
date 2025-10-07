# llm.py
import requests
import logging

# -------------------------------
# LLaMA 3.3 Free API configuration
# -------------------------------
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"  # OpenRouter endpoint

# -------------------------------
# Generation functions
# -------------------------------
def generate_answer(query, context_text, similarity_score=None, max_tokens=200):
    """
    Generate an answer using LLaMA 3.3 API with context (for RAG pipeline)
    """
    prompt = f"Answer the following query using the context below.\n\nContext: {context_text}\n\nQuery: {query}\nAnswer:"

    payload = {
        "model": "meta-llama/llama-3.3-8b-instruct:free",  # Correct free-tier model ID
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.HTTPError as e:
        logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "Error: Could not generate answer using LLaMA API."
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        return "Error: Could not generate answer using LLaMA API."


def generate_general_answer(query, max_tokens=200):
    """
    Generate a general answer without context (used when similarity is too low)
    """
    prompt = f"Provide a helpful general response to this question:\n\n{query}\nAnswer:"

    payload = {
        "model": "meta-llama/llama-3.3-8b-instruct:free",  # Correct free-tier model ID
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.HTTPError as e:
        logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "Error: Could not generate general answer using LLaMA API."
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        return "Error: Could not generate general answer using LLaMA API."


# -------------------------------
# Example usage
# -------------------------------
"""if __name__ == "__main__":
    query = "What are the BTech courses offered at GL Bajaj?"
    context = ("GL Bajaj Institute of Technology and Management offers BTech courses "
               "in CSE, IT, ECE, and Mechanical Engineering. It has experienced faculty "
               "and good infrastructure.")

    print("Answer with context:")
    print(generate_answer(query, context))

    print("\nGeneral answer (no context):")
    print(generate_general_answer(query))
"""