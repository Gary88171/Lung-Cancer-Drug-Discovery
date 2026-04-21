import os
import pandas as pd
import logging
from rdkit import Chem
from rdkit.Chem import SaltRemover
from rdkit.Chem.MolStandardize import rdMolStandardize
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

engine = create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

def standardize_molecule(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return None, None
        remover = SaltRemover.SaltRemover()
        mol = remover.StripMol(mol)
        uncharger = rdMolStandardize.Uncharger()
        mol = uncharger.uncharge(mol)
        return Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True), Chem.MolToInchiKey(mol)
    except:
        return None, None
    
def run_unification():
    logger.info("Read PubChem(drugs table) in the database...")
    df_pub = pd.read_sql("SELECT drug_name, smiles FROM drugs", engine)

    pub_res = df_pub['smiles'].apply(standardize_molecule)
    df_pub[['std_smiles', 'inchikey']] = pd.DataFrame(pub_res.tolist(), index=df_pub.index)

    logger.info("Read ChEMBL data from the database(raw_chembl table)...")
    df_chem = pd.read_sql("SELECT chembl_id, smiles, standard_value, organism FROM raw_chembl WHERE organism = 'Homo sapiens'", engine)

    chem_res = df_chem['smiles'].apply(standardize_molecule)
    df_chem[['std_smiles', 'inchikey']] = pd.DataFrame(chem_res.tolist(), index=df_chem.index)
    
    logger.info("Cross library validation is being performed()")

    combined = pd.concat([df_chem, df_pub], ignore_index=True)

    combined = combined.sort_values('standard_value', na_position='last')
    final_df = combined.drop_duplicates(subset=['inchikey'], keep='first')

    def assign_label(row):
        if pd.notna(row['standard_value']):
            if row['standard_value'] < 1000: return 1
            if row['standard_value'] > 10000: return 0
            return -1
        
        if pd.notna(row['drug_name']):
            return 1
        return -1
    
    final_df['label'] = final_df.apply(assign_label, axis=1)

    final_dataset = final_df[final_df['label'].isin([0, 1])]

    output = "final_gold_dataset.csv"
    final_dataset.to_csv(output, index=False)

    logger.info(f"Verification complete")
    logger.info(f"Final data pens: {len(final_dataset)}")
    logger.info(f"  - Where is the number of pens proved by the experiment IC50: {final_dataset['standard_value'].notna().sum()}")
    logger.info(f"The file has been saved to: {output}")

if __name__ == "__main__":
    run_unification()