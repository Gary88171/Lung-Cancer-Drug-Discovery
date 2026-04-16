import os
import pandas as pd
from sqlalchemy import create_engine
from rdkit import Chem
from rdkit.Chem import Descriptors
from dotenv import load_dotenv

load_dotenv()

def lipinski_analysis():
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

        sql = "SELECT id, drug_name, smiles FROM drugs WHERE smiles IS NOT NULL"
        df = pd.read_sql(sql, engine)

        results = []
        for index, row in df.iterrows():
                mol = Chem.MolFromSmiles(row['smiles'])
                if mol:
                    mw = Descriptors.MolWt(mol)
                    logp = Descriptors.MolLogP(mol)
                    hbd = Descriptors.NumHDonors(mol)
                    hba = Descriptors.NumHAcceptors(mol)

                    is_druglike = (mw <= 500 and logp <= 5 and hba <= 10)
                    results.append([row['id'], mw, logp, hbd, hba, is_druglike])

        res_df = pd.DataFrame(results, columns=['id', 'MW', 'LogP', 'HBD', 'HBA', 'DrugLike'])
        print(f"Total analyse molecular number: {len(res_df)}")
        print(f"Potential candidates who meet Lioinski's criteria: {res_df['DrugLike'].sum()}")

        res_df.to_sql('drug_analysis', engine, if_exists='replace', index=False)
        print("Saved to database: drug_analysis")



if __name__ == "__main__":
       lipinski_analysis()