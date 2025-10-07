from sentence_transformers import SentenceTransformer

# Load model once (384-dim MiniLM)
print("🔄 Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Model loaded")

def generate_embeddings(chunks):
    """
    Generate embeddings for list of text chunks.
    Returns: list of 384-dimensional vectors
    """
    return model.encode(chunks, convert_to_numpy=True).tolist()

