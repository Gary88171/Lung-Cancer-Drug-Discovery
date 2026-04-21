import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_raw_tables():
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), database=os.getenv("DB_NAME")
        )
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw_chembl (
                id SERIAL PRIMARY KEY,
                target_gene VARCHAR(50),
                chembl_id VARCHAR(50) UNIQUE,
                smiles TEXT,standard_type VARCHAR(20),
                standard_value FLOAT,
                standard_units VARCHAR(20),
                inchikey VARCHAR(27),
                organism VARCHAR(100)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw_drugbank (
                id SERIAL PRIMARY KEY,
                drug_name VARCHAR(255),
                smiles TEXT,
                approval_status VARCHAR(100),
                inchikey VARCHAR(27)
            );
        ''')

        conn.commit()
        cur.close()
        conn.close()
        print("Table Crated")

if __name__ == "__main__":
        create_raw_tables()
