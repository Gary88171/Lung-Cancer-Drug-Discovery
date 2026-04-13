import os
import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()

def create_table():
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )

        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS lung_cancer_targets (
            id SERIAL PRIMARY KEY,
            gene_name VARCHAR(100),
            ncbi_id VARCHAR(50) UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
        ''')

        conn.commit()
        print("Created table of lung cancer data")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Create table failed: {e}")

if __name__ == "__main__":
    create_table()