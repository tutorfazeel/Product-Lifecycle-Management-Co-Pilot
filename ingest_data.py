import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neo4j AuraDB connection details
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# --- CORRECTED FILE PATHS ---
# Pointing to the large dataset in the 'mock_data' folder
PARTS_CSV = os.path.join('mock_data', 'parts.csv')
SUPPLIERS_CSV = os.path.join('mock_data', 'suppliers.csv')
SUPPLY_CHAIN_CSV = os.path.join('mock_data', 'supply_chain.csv')
COMPLIANCE_CSV = os.path.join('mock_data', 'compliance.csv')


class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, params={}):
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record for record in result]

    def clear_database(self):
        print("Clearing existing data from the database...")
        query = "MATCH (n) DETACH DELETE n"
        self.run_query(query)
        print("Database cleared.")

    def create_constraints(self):
        print("Creating constraints for faster lookups...")
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Part) REQUIRE p.part_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Supplier) REQUIRE s.supplier_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pl:ProductLine) REQUIRE pl.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:ComplianceDoc) REQUIRE d.doc_id IS UNIQUE",
        ]
        for query in queries:
            self.run_query(query)
        print("Constraints created.")

    def ingest_data(self):
        # Verify that the data files exist before proceeding
        for f in [PARTS_CSV, SUPPLIERS_CSV, SUPPLY_CHAIN_CSV, COMPLIANCE_CSV]:
            if not os.path.exists(f):
                print(f"Error: Data file not found at {f}. Please ensure your large dataset is in the 'mock_data' folder.")
                return

        self.clear_database()
        self.create_constraints()

        # Ingest Parts and Product Lines
        print("Ingesting Parts and Product Lines with corrected relationship...")
        parts_df = pd.read_csv(PARTS_CSV)
        parts_query = """
        UNWIND $rows AS row
        MERGE (p:Part {part_id: row.part_id})
        SET p.name = row.part_name
        MERGE (pl:ProductLine {name: row.product_line})
        // --- THE ESSENTIAL FIX ---
        MERGE (pl)-[:CONTAINS_PART]->(p)
        """
        self.run_query(parts_query, params={'rows': parts_df.to_dict('records')})

        # Ingest Suppliers
        print("Ingesting Suppliers...")
        suppliers_df = pd.read_csv(SUPPLIERS_CSV)
        suppliers_query = """
        UNWIND $rows AS row
        MERGE (s:Supplier {supplier_id: row.supplier_id})
        SET s.name = row.supplier_name, s.region = row.region
        """
        self.run_query(suppliers_query, params={'rows': suppliers_df.to_dict('records')})

        # Ingest Supply Chain Relationships
        print("Ingesting Supply Chain relationships...")
        supply_chain_df = pd.read_csv(SUPPLY_CHAIN_CSV)
        supply_chain_query = """
        UNWIND $rows AS row
        MATCH (p:Part {part_id: row.part_id})
        MATCH (s:Supplier {supplier_id: row.supplier_id})
        MERGE (p)-[:SUPPLIED_BY]->(s)
        """
        self.run_query(supply_chain_query, params={'rows': supply_chain_df.to_dict('records')})
        
        # Ingest Compliance Documents
        print("Ingesting Compliance data...")
        compliance_df = pd.read_csv(COMPLIANCE_CSV)
        compliance_query = """
        UNWIND $rows AS row
        MATCH (p:Part {part_id: row.part_id})
        MERGE (d:ComplianceDoc {doc_id: row.doc_id})
        SET d.status = row.status, d.standard = row.standard
        MERGE (p)-[:HAS_COMPLIANCE]->(d)
        """
        self.run_query(compliance_query, params={'rows': compliance_df.to_dict('records')})

        print("\nLarge dataset ingestion complete with corrected schema! ✨")

if __name__ == "__main__":
    ingestor = Neo4jIngestor(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    ingestor.ingest_data()
    ingestor.close()