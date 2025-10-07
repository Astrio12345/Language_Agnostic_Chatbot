
import docx2txt
import fitz  # PyMuPDF for PDF

def read_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""

    if ext == "txt":
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    elif ext == "pdf":
        pdf = fitz.open(filepath)
        for page in pdf:
            text += page.get_text()
    elif ext == "docx":
        text = docx2txt.process(filepath)

    return text

def clean_text(text):
    return " ".join(text.split())

def split_into_word_chunks(text, chunk_size=20, overlap=10):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += (chunk_size - overlap)
    return chunks

def process_document(filepath, chunk_size=20, overlap=10):
    print(f"📄 Reading file: {filepath}")
    text = read_file(filepath)
    cleaned = clean_text(text)
    chunks = split_into_word_chunks(cleaned, chunk_size, overlap)
    return chunks

