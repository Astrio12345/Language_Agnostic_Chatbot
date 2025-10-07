# flaskapp.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import numpy as np

from lang_detect import detect_language
from translator import translate_to_english, translate_to_original
from convmemory import get_conversation_context, update_conversation_context
from rag_pipeline.simsearch import similarity_search
from rag_pipeline.llm import generate_answer, generate_general_answer
from rag_pipeline.faqstore import store_faq
from config import SIMILARITY_CONFIG

# ------------------------
# App Initialization
# ------------------------
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

def to_serializable(val):
    if isinstance(val, (np.float32, np.float64)):
        return float(val)
    if isinstance(val, (np.int32, np.int64)):
        return int(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    return val

# ------------------------
# API Endpoint
# ------------------------
@app.route("/query", methods=["POST"])
def handle_query():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input provided"}), 400

        user_query = data.get("query")
        user_id = data.get("user_id", "default_user")
        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        logging.info(f"User ID: {user_id}, Query: {user_query}")

        # Step 1: Language detection
        lang = detect_language(user_query)
        query_en = translate_to_english(user_query, lang) if lang != "en" else user_query

        # Step 2: Get conversation context
        context = get_conversation_context(user_id) or []
        context_str = "\n".join([
            f"Q: {str(item.get('query',''))} A: {str(item.get('answer',''))}"
            for item in context
        ])

        # Step 3: Similarity search
        top_chunks_text, similarity, top_chunks = similarity_search(query_en, top_n=5)

        # Handle Oracle LOBs
        if hasattr(top_chunks_text, "read"):
            top_chunks_text = top_chunks_text.read()
        top_chunks_text = str(top_chunks_text or "")

        similarity = float(to_serializable(similarity))
        logging.info(f"Similarity score: {similarity}, Top chunks total length: {len(top_chunks_text)}")

        # Step 4: Decide response
        min_threshold = SIMILARITY_CONFIG.get("min_threshold", 0.3)
        CONTACT_MESSAGE = "Contact To Mail Id - office@glbitm.ac.in"

        if similarity <= 0.0:  # No results at all
            # Call general LLM, but return contact message instead
            _ = generate_general_answer(query_en)
            answer_en = CONTACT_MESSAGE
            logging.info("Similarity is zero → General fallback used, contact message returned.")
        elif similarity < min_threshold:  # Weak match → General fallback
            _ = generate_general_answer(query_en)
            answer_en = CONTACT_MESSAGE
            logging.info(f"Low similarity ({similarity:.4f}) → General fallback used, contact message returned.")
        else:  # Good match → RAG
            answer_en = generate_answer(
                query_en,
                context_str + "\n" + top_chunks_text,
                similarity_score=similarity
            )
            logging.info(f"Similarity ({similarity:.4f}) → Answer generated via RAG.")

        # Step 5: Store Q&A
        try:
            store_faq(query_en, answer_en, top_chunks_text)
        except Exception as e:
            logging.warning(f"Failed to store FAQ: {e}")

        # Step 6: Update conversation memory
        try:
            update_conversation_context(user_id, user_query, answer_en)
        except Exception as e:
            logging.warning(f"Failed to update conversation context: {e}")

        # Step 7: Translate back if needed
        final_answer = translate_to_original(answer_en, lang) if lang != "en" else answer_en

        return jsonify({
            "query": user_query,
            "answer": final_answer,
            "similarity_score": similarity,
            "language": lang
        })

    except Exception as e:
        logging.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
