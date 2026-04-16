import os
import psycopg2
from rdkit import Chem
from rdkit.Chem import Draw
from dotenv import load_dotenv

load_dotenv()

def draw_drugs_from_db():
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        #connect database
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )
        cur = conn.cursor()

        cur.execute("SELECT drug_name, smiles FROM drugs WHERE smiles IS NOT NULL LIMIT 400;")
        rows = cur.fetchall()

        if not rows:
            print()
            return
        
        mols = []
        labels = []
        for name, smiles in rows:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                mols.append(mol)
                labels.append(name)

        img = Draw._MolsToGridImage(mols, legends=labels, molsPerRow=8, subImgSize=(200, 200))
        img.save("drug_molecules.png")
        print("Drug molecular structure saved to drug_molecules.png")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Draw filed: {e}")

if __name__ == "__main__":
    draw_drugs_from_db()