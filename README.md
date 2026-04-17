# Lung Cancer Drug Discovery Project
A bioinformatics pipeline to analyze lung cancer data using Python, Docker, and PostgreSQL.
#Project Summary

Technology Stack

Daily Log
12/4/2026: Create dababase on docker
13/4/2026: Test dababase connection
14/4/2026: Developer crawler to serach lung cancer gene id, and create table
15/4/2026: Infrastructure and Connectivity, resolved library mounting conflicts caused by the desktop OneDrive path
16/4/2026: Connect with NCBI to capture lung cancer gene targets and match corresponding drug molecules from PubChem
17/4/2026: Upgrade the underlying database to SQLAlchemy for more stable Pandas integration, implementing Lipinski's Rule of Five screening to calculate molecular weight (MW) and lipid solubility (LogP)