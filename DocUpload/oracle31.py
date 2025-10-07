import oracledb
import json

# Oracle DB Config
DB_CONFIG = {
    "user": "system",
    "password": "manish8076",
    "dsn": "localhost:1521/freepdb1"   # ✅ Adjust host/service here
}

def get_connection():
    return oracledb.connect(**DB_CONFIG)

def store_embeddings(file_id, chunks, embeddings):
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
            CREATE TABLE documents (
                file_id VARCHAR2(255),
                chunk_index NUMBER,
                chunk_text CLOB,
                embedding CLOB
            )';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN RAISE;
                END IF;
        END;
    """)

    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        embedding_json = json.dumps(emb)
        cursor.execute(
            """
            INSERT INTO documents (file_id, chunk_index, chunk_text, embedding)
            VALUES (:1, :2, :3, :4)
            """,
            [file_id, idx, chunk, embedding_json]
        )

    conn.commit()
    cursor.close()
    conn.close()
