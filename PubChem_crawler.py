import os
import psycopg2
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def search_pubchem_for_gene(gene_name, max_results=200):
    """Search PubChem using text search"""
    try:
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{gene_name}/cids/JSON"
        params = {'name_type': 'word'}
        
        response = requests.get(search_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            cids = data.get('IdentifierList', {}).get('CID', [])
            return cids[:max_results]
        else:
            print(f"Search failed for {gene_name}: Status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error searching for {gene_name}: {e}")
        return []

def get_compound_properties(cids):
    """Get properties for a list of CIDs"""
    if not cids:
        return []
    
    try:
        # PubChem allows up to 100 CIDs per request
        cid_string = ','.join(map(str, cids[:100]))
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_string}/property/MolecularWeight,IsomericSMILES,IUPACName/JSON"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            properties = data.get('PropertyTable', {}).get('Properties', [])
            print(f"  DEBUG: Retrieved {len(properties)} property records")
            if properties:
                print(f"  DEBUG: First property sample: {properties[0]}")
            return properties
        else:
            print(f"  DEBUG: Property request failed with status {response.status_code}")
        return []
    except Exception as e:
        print(f"Error getting properties: {e}")
        return []

def get_compound_synonyms(cid):
    """Get synonyms (including drug names) for a CID"""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            synonyms = data.get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
            return synonyms[:5]
        return []
    except:
        return []

def find_drugs_for_targets():
    conn = None
    cur = None
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

        cur.execute("SELECT gene_name FROM lung_cancer_targets WHERE gene_name IS NOT NULL;")
        rows = cur.fetchall()
        targets = [row[0] for row in rows]

        for gene_full_name in targets:
            print(f"\n{'='*60}")
            print(f"Searching for compounds related to: {gene_full_name}")
            print(f"{'='*60}")
            
            try:
                # Search PubChem
                cids = search_pubchem_for_gene(gene_full_name, max_results=200)
                
                if not cids:
                    print(f"❌ No compounds found for {gene_full_name}")
                    continue
                
                print(f"✓ Found {len(cids)} compounds")
                
                # Process in batches of 100
                inserted_count = 0
                skipped_count = 0
                
                for i in range(0, len(cids), 100):
                    batch_cids = cids[i:i+100]
                    properties = get_compound_properties(batch_cids)
                    
                    for prop in properties:
                        cid = prop.get('CID')
                        mw_value = prop.get('MolecularWeight')

                        # Try IsomericSMILES first, fallback to SMILES or CanonicalSMILES
                        smiles = prop.get('IsomericSMILES') or prop.get('SMILES') or prop.get('CanonicalSMILES')
                        iupac_name = prop.get('IUPACName', 'Unknown')
                        
                        # Check if we have required data
                        if not smiles:
                            skipped_count += 1
                            continue
                        
                        # Convert molecular weight
                        try:
                            mw = float(mw_value) if mw_value else None
                        except:
                            mw = None
                        
                        # Filter by molecular weight (drug-like) - only if MW is available
                        if mw is None or not (200 < mw < 900):
                            skipped_count += 1
                            continue
                        
                        # Get synonyms for better drug name
                        synonyms = get_compound_synonyms(cid)
                        drug_name = synonyms[0] if synonyms else iupac_name
                        
                        # Insert into database WITH molecular weight
                        cur.execute('''
                            INSERT INTO drugs (target_gene_id, drug_name, smiles, pubchem_cid, molecular_weight)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        ''', (gene_full_name, drug_name[:500], smiles, str(cid), mw))
                        
                        inserted_count += 1
                        if inserted_count <= 5:  # Print first 5
                            print(f"  → {drug_name[:60]} (CID: {cid}, MW: {mw:.1f})")
                    
                    # Rate limiting - PubChem allows 5 requests/second
                    time.sleep(0.2)
                
                conn.commit()
                print(f"✓ Inserted {inserted_count} compounds for {gene_full_name}")
                print(f"  (Skipped {skipped_count} compounds - no SMILES or MW out of range)")
                
            except Exception as gene_error:
                print(f"❌ Error processing {gene_full_name}: {gene_error}")
                import traceback
                traceback.print_exc()
                conn.rollback()
                continue

        print(f"\n{'='*60}")
        print("✓ All drug data stored in database")
        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Database Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    find_drugs_for_targets()