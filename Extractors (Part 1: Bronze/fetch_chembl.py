import os
import pandas as pd
import logging
from chembl_webresource_client.new_client import new_client
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def fetch_gene_target_activities(gene_list=["EGFR", "KRAS", "ERBB2"]):

    conn = psycopg2.connect(
            user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), database=os.getenv("DB_NAME")
        )
    cur = conn.cursor()
    target_api = new_client.target
    activity_api = new_client.activity


    for gene in gene_list:
        print(f"Searching the target: {gene} ...")

        target_res = target_api.search(gene)

        target_id = target_res[0]['target_chembl_id']
        print(f"Find the ChEMBL ID of {gene}: {target_id}")

        res = activity_api.filter(target_chembl_id=target_id).filter(standard_type="IC50").filter(target_organism="Homo sapiens").filter(standard_units="nM")
        activities_list = list(res[:500])
        df = pd.DataFrame(activities_list)

        if df.empty:
            print(f"Don't find data of {gene}")
            continue

        df = df.dropna(subset=['canonical_smiles', 'standard_value'])
        df['target_gene'] = gene

        final_df = df[[
            'target_gene',
            'molecule_chembl_id',
            'canonical_smiles',
            'standard_type',
            'standard_value',
            'standard_units',
            'target_organism'
        ]].rename(columns={
            'molecule_chembl_id': 'chembl_id',
            'canonical_smiles': 'smiles',
            'target_organism': 'organism'
        })

        for index, row in final_df.iterrows():
            try:
                cur.execute('''
                    INSERT INTO raw_chembl (target_gene, chembl_id, smiles, standard_type, standard_value, standard_units, organism)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chembl_id) DO NOTHING
                ''', (row['target_gene'], row['chembl_id'], row['smiles'],
                      row['standard_type'], row['standard_value'], row['standard_units'], row['organism']))
            except Exception as e:
                print(f"Input Error: {e}")
        conn.commit()

if __name__ == "__main__":
    targets = ["EGFR", "KRAS", "ERBB2"]
    fetch_gene_target_activities(targets)