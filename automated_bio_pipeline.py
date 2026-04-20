import os
import logging
import pandas as pd
import psycopg2
from chembl_webresource_client.new_client import new_client
from rdkit import Chem
from rdkit.Chem import SaltRemover
from rdkit.Chem.MolStandardize import rdMolStandardize
from dotenv import load_dotenv

load_dotenv()
#1Create log rule
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("pipeline_execution.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
#2remove salt from molecular, use rdkit.SaltRemover to remove.
def standardize_mol(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return None, None
        remover = SaltRemover.SaltRemover()
        mol = remover.StripMol(mol)

        uncharger = rdMolStandardize.Uncharger()
        mol = uncharger.uncharge(mol)

        std_smi = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
        ikey = Chem.MolToInchiKey(mol)
        return std_smi, ikey
    except Exception as e:
        logger.debug(f"SMILES handling filed: {e}")
        return None, None
#3Building the automated_pipeline
def run_pipeline():
    genes = ["EGFR", "KRAS", "ERBB2"]
    api = new_client.activity
    #3.1: Connect to database, use psycopg2 to make sure connect stable.
    try:
        conn = psycopg2.connect(
                user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), database=os.getenv("DB_NAME")
        )
        cur = conn.cursor()
        logger.info("Susscufer connecting to PostgreSQL Database")
    except Exception as e:
        logger.error(f"Database connecct failed: {e}")
        return
    #3.2: the 
    for gene in genes:
        logger.info(f"Start automating processing target: {gene}")
        #3.2.1:
        data_types = [
            ("Active", "standard_value__lt=1000"),
            ("Inactive", "standard_value__gt=10000")
        ]

        activity_api = new_client.activity

        for label_type, filter_str in data_types:
            logger.info(f"Geting {label_type} data (Conditions: {filter_str} of {gene}...)")

            query = activity_api.filter(
                target_components__target_component_synonyms__component_synonym__iexact=gene,
                target_organism="Homo sapiens",
                standard_type="IC50"
            )
            if label_type == "Active":
                res = query.filter(standard_value__lt=1000)
            else:
                res = query.filter(standard_value__gt=10000)
            
            try:
                raw_data = list(res[:1000])
                df = pd.DataFrame(raw_data)
            except Exception as e:
                logger.error(f"Network grab failed: {e}")
                continue

            if df.empty:
                logger.warning(f"{gene} {label_type} Check no data")
                continue

            success_count = 0
            for _, row in df.iterrows():
                std_smi, ikey = standardize_mol(row['canonical_smiles'])
                if not ikey: continue

                try:
                    cur.execute('''
                        INSERT INTO raw_chembl (target_gene, chembl_id, smiles, standard_type, standard_value, standard_units, organism, inchikey)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (chembl_id) DO NOTHING
                    ''', (gene, row['molecule_chembl_id'], std_smi, row['standard_type'], row['standard_value'], row['standard_units'], row['target_organism'], ikey))
                    if cur.rowcount > 0:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Write error: {e}")
            
            conn.commit()
            logger.info(f" {gene} {label_type} process completed, new addition {success_count}.")

    cur.close()
    conn.close()
    logger.info("The automated pipeline task was successfully concluded")

if __name__ == "__main__":
    run_pipeline()