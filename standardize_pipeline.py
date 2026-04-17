from rdkit import Chem
from rdkit.Chem import SaltRemover
from rdkit.Chem.MolStandardize import rdMolStandardize


def standardize_molecule(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        remover = SaltRemover.SaltRemover()
        mol = remover.StripMol(mol)

        uncharger = rdMolStandardize.Uncharger()
        mol = uncharger.uncharge(mol)

        return Chem.MolToInchiKey(mol)
    return None
    
if __name__ == "__main__":
    print(f"keyinfor: {standardize_molecule('CN1C=NC2=C1C(=O)N(C(=O)N2C)C.Cl')}")