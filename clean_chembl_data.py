import logging
import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import SaltRemover
from rdkit.Chem import MolStandardize
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("data_cleaning.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

engine = create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

def standardize_and_label(smiles, ic50, chembl_id):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            logger.warning(f"Molecular error: {chembl_id}")
            return None, None, None

        remover = SaltRemover.SaltRemover()
        mol = remover.StripMol(mol)

        std_smiles = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
        inchikey = Chem.MolToInchiKey(mol)

        label = 1 if ic50 < 1000 else (0 if ic50 > 10000 else -1)

        return std_smiles, inchikey, label
    except Exception as e:
        logger.error(f"Error when handle {chembl_id}: {str(e)}")
        return None, None, None

def process_data():
    logger.info("Extract data from database")
    query = """
    SELECT 
        "chembl_id" As chembl_id,
        "smiles" AS smiles,
        "standard_value" AS standard_value
    FROM raw_chembl
    WHERE organism = 'Homo sapiens'
    """

    try:
        df = pd.read_sql(query, engine)
        print(f"DataFrame have: {df.columns.tolist()}")
        logger.info(f"Read {len(df)} datas.")
    except Exception as e:
        logger.critical(f"Unable to connect to the database: {e}")
        return
    
    logger.info("Initiate full volume standardized pipelines...")

    results = df.apply(lambda row: standardize_and_label(row['smiles'], row['standard_value'], row['chembl_id']), axis=1)
    df[['std_smiles', 'inchikey', 'label']] = pd.DataFrame(results.tolist(), index=df.index)

    train_df = df[(df['label'].isin([0, 1])) & (df['inchikey'].notna())]
    logger.info(f"Processing completion statistics:")
    logger.info(f"  - Original totals: {len(df)}")
    logger.info(f"  - Successful conversion and labeling: {len(train_df)}")
    logger.info(f"  - Excluding data (An intermediate value or invalid): {len(df) - len(train_df)}")

    output_file = "kaggle_training_data.csv"
    train_df.to_csv(output_file, index=False)
    logger.info(f"Training data has been saved to: {output_file}")

if __name__ == "__main__":
    process_data()