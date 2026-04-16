# I need make a api to connect data from ncbi
#librail request
#mainpart(api, dataname, select and get data)
#report worong or done
#input data to database
import os
from Bio import Entrez
from dotenv import load_dotenv

load_dotenv()

Entrez.email = os.getenv("EMAIL")
Entrez.api_key = os.getenv("API_KEY")

def search_lung_cancer_genes():
    print("searching NCBI Gene Database")
    handle = Entrez.esearch(db="gene", term="Non-smll cell lung cancer", retmax=50)
    record = Entrez.read(handle)
    handle.close()

    gene_ids = record["IdList"]
    print(f"Gene ID list: {gene_ids}")
    return gene_ids

if __name__ == "__main__":
    try:
        ids = search_lung_cancer_genes()
    except Exception as e:
        print(f"Error: {e}")
