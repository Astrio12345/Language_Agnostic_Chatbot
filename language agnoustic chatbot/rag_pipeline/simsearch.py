#simsearch.py
import numpy as np
import faiss
from config import ORACLE_CONFIG
import oracledb

from sentence_transformers import SentenceTransformer

# ------------------------
# Load model
# ------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
dim = 384  # embedding dimension for all-MiniLM-L6-v2

# ------------------------
# Oracle DB connection
# ------------------------
conn = oracledb.connect(
    user=ORACLE_CONFIG["user"],
    password=ORACLE_CONFIG["password"],
    dsn=ORACLE_CONFIG["dsn"]
)
cursor = conn.cursor()
def chunk_text(text, chunk_size=150):
    """Split text into 100–200 word semantic chunks."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def fetch_chunks():
    """Fetch chunks from Oracle DB and prepare embeddings."""
    cursor.execute("SELECT FILE_ID, CHUNK_INDEX, CHUNK_TEXT, EMBEDDING FROM documents")
    rows = cursor.fetchall()
    chunk_texts = []
    embeddings = []

    for row in rows:
        file_id, chunk_index, chunk_text, embedding = row

        # Handle CLOB
        if hasattr(chunk_text, "read"):
            chunk_text = chunk_text.read()
        chunk_texts.append(chunk_text)

        # Convert embedding to np array
        embeddings.append(np.array(embedding, dtype="float32"))

    embeddings = np.vstack(embeddings)
    faiss.normalize_L2(embeddings)

    # Create FAISS index
    index = faiss.IndexFlatIP(dim)  # inner product = cosine similarity
    index.add(embeddings)

    return index, chunk_texts, embeddings

index, chunk_texts, embeddings = fetch_chunks()

def similarity_search(query, top_n=5):
    query_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)

    D, I = index.search(query_emb, top_n)
    top_chunks = [(chunk_texts[i], float(D[0][idx])) for idx, i in enumerate(I[0])]
    top_chunks_text = "\n".join([chunk_texts[i] for i in I[0]])
    similarity = float(D[0][0]) if D.size > 0 else 0.0

    return top_chunks_text, similarity, top_chunks
