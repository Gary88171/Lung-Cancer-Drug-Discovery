# Lung Cancer Drug Discovery Project
A bioinformatics pipeline to analyze lung cancer data using Python, Docker, and PostgreSQL.
#Project Summary

This is a drug screening project based on Graph Neural Networks(GNN). The goal is to predict the biological activity(IC50) of candidate drugs (such as EGFR, KRAS, ERBB2) for critical carcinogenic driving factors for lung cancer.

#Technology Stack
Operating System: WSL2(Ubuntu 22.04 LTS)
Database: PostgreSQL (Docker-based) for structured chemical data storage.
Cheminformatics: RDKit 2026.03(Advanced standardization,Salt removal, InChiKey generation).
Machine Learning: PyTorch Geometric (PyG), Scikit-learn.
Visual Analysis: Microsoft Power BI (for Exploratory Data Analysis)

Data Engineering & Pipeline
The data collection and standardization process of this project strictly follows scientific standards:
Multi-source Integration: Integration of PubChem(Clinical/listed drug), ChEMBL (Biological activity experimental data) with DrugBank.
Automated Preprocessing:
1.Species Filtering: Strictly screen Homo sapiens (human) data to exclude non-human experimental noise.
2.InChiKey Unification: Deduplication and data validation across databases using InCHiKey as a unique identifier.
3.Label Engineering: According to IC50 value label the molecule as Active(1,<1000nM) and Inactive(0,>10000nM).

Current Status
WSL2/Docker Enviroment Setup
Automated Data Fetching(EGFR, KRAS, ERBB2)
Molecular Standardization Pipeline(RDKit 2026)
Dataset Generation(Balanced Labels)
GNN Model Training on Kaggle (Ongoing)
Daily Log
12/4/2026: Create dababase on docker
13/4/2026: Test dababase connection
14/4/2026: Developer crawler to serach lung cancer gene id, and create table
15/4/2026: Infrastructure and Connectivity, resolved library mounting conflicts caused by the desktop OneDrive path
16/4/2026: Connect with NCBI to capture lung cancer gene targets and match corresponding drug molecules from PubChem
17/4/2026: Upgrade the underlying database to SQLAlchemy for more stable Pandas integration, implementing Lipinski's Rule of Five screening to calculate molecular weight (MW) and lipid solubility (LogP)
18/4/2026: Success grad from ChEMBL API has IC50 data of experimental values. Implement ON CONFLICT DO NOTHING logic to avoid ID conflicts caused by repeated capture. 