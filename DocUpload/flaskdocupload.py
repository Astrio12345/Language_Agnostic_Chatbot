from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Import helper functions
from docsplit import process_document
from genembedding import generate_embeddings
from oracle31 import store_embeddings

# Config
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ✅ Check if file extension is allowed
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ Upload route
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        print("📥 Incoming upload request...")

        if "file" not in request.files:
            print("❌ No file part in request")
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            print("❌ No file selected")
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Step 1: Save file
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file.save(filepath)
            print(f"✅ File saved at: {filepath}")

            # Step 2: Clean + split document
            print("🔄 Processing document...")
            chunks = process_document(filepath, chunk_size=100, overlap=50)
            print(f"✅ Processed into {len(chunks)} chunks")

            if not chunks:
                return jsonify({"error": "No text extracted from document"}), 400

            # Step 3: Generate embeddings
            print("🔄 Generating embeddings...")
            embeddings = generate_embeddings(chunks)
            print(f"✅ Generated {len(embeddings)} embeddings")

            # Step 4: Store in Oracle DB
            print("🔄 Storing embeddings in DB...")
            store_embeddings(filename, chunks, embeddings)
            print("✅ Stored successfully in DB")

            return jsonify({
                "message": "File processed and stored successfully ✅",
                "file": filename,
                "chunks_count": len(chunks)
            }), 200

        print("❌ Invalid file type")
        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
        print(f"❌ Error while processing file: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


# ✅ Start Flask app
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("🚀 Flask server starting at http://127.0.0.1:5002")
    app.run(host="0.0.0.0", port=5002, debug=True)
