import oracledb
from config import ORACLE_CONFIG

conn = oracledb.connect(
    user=ORACLE_CONFIG["user"],
    password=ORACLE_CONFIG["password"],
    dsn=ORACLE_CONFIG["dsn"]
)
def store_faq(question, answer, chunk_text):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO faqstore (question, answer, chunk_text)
        VALUES (:1, :2, :3)
    """, [question, answer, chunk_text])
    conn.commit()
