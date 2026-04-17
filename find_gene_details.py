import os
import psycopg2
from Bio import Entrez
from dotenv import load_dotenv

load_dotenv()

Entrez.email = os.getenv("EMAIL")
Entrez.api_key = os.getenv("API_KEY")

def find_and_store_genes(gene_id_list):
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

        print(f"crawler the {len(gene_id_list)} gene infor from NCBI")

        handle = Entrez.efetch(db="gene", id=",".join(gene_id_list), retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        for record in records:
            gene_name = record.get('Entrezgene_gene', {}).get('Gene-ref', {}).get('Gene-ref_locus', 'Unknown')
            description = record.get('Entrezgene_gene', {}).get('Gene-ref', {}).get('Gene-ref_desc', 'No description')
            ncbi_id = str(record.get('Entrezgene_track-info', {}).get('Gene-track', {}).get('Gene-track_geneid', '0'))            

            cur.execute('''
                INSERT INTO lung_cancer_targets (gene_name, ncbi_id, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (ncbi_id) DO NOTHING            
            ''', (gene_name, ncbi_id, description))

            print(f"stord in: {gene_name} (ID: {ncbi_id})")

        conn.commit()
        cur.close()
        conn.close()
        print(f" stord: {gene_name} (ID: {ncbi_id})")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":

    test_ids = ["3845", "2064", "1956"]
    find_and_store_genes(test_ids)