# AWS GraphRAG PLM Co-Pilot Demo

This project demonstrates a Product Lifecycle Management (PLM) Co-Pilot built with a GraphRAG architecture. It uses Neo4j for the knowledge graph, an open-source LLM (Mistral 7B) hosted on AWS SageMaker, and a Streamlit web interface.

This architecture is powerful for answering complex questions about interconnected data, such as a manufacturing supply chain.



## ⚙️ Architecture
1.  **Data Source**: Four CSV files representing parts, suppliers, compliance, and their relationships.
2.  **Knowledge Graph**: A Python script (`ingest_data.py`) parses the CSVs and populates a Neo4j AuraDB instance.
3.  **LLM Backend**: A Mistral 7B model is deployed on an AWS SageMaker endpoint for inference.
4.  **RAG Orchestration**: LangChain's `GraphCypherQAChain` connects the graph and the LLM. It translates a user's natural language question into a Cypher query, executes it against the graph, and uses the result to generate a final answer.
5.  **Frontend**: A Streamlit application (`app.py`) provides a simple UI for users to ask questions and view results, including key LLMOps/FinOps metrics like latency and cost.

## 🚀 Setup Instructions

Follow these steps to get the PLM Co-Pilot running.

### 1. Set Up Neo4j AuraDB

1.  Go to the [Neo4j AuraDB website](https://neo4j.com/cloud/platform/aura-database/) and sign up for a free account.
2.  Create a new **Free DB Instance**.
3.  Once the instance is running, find your connection credentials:
    * **Connection URI** (the `neo4j+s://...` string)
    * **Username** (usually `neo4j`)
    * **Password** (the one you saved during creation)
4.  Keep these details handy for your `.env` file.

### 2. Deploy LLM on AWS SageMaker

You need to deploy a large language model to a SageMaker endpoint. We recommend using Mistral 7B via AWS JumpStart for simplicity.

1.  Log in to your AWS Management Console.
2.  Navigate to the **Amazon SageMaker** service.
3.  In the left-hand menu, go to **JumpStart**.
4.  Search for **Mistral 7B Instruct** and select it.
5.  Click **Deploy**. For the instance type, choose an appropriate GPU instance like `ml.g5.2xlarge`.
6.  Once the deployment is complete, an endpoint will be created. Go to **Inference > Endpoints** in the SageMaker console.
7.  Copy the **Endpoint name**. It will look something like `jumpstart-dft-mistral-7b-instruct-...`.

_**Note:** Running a SageMaker endpoint incurs AWS costs. Remember to shut it down after your demo!_

### 3. Set Up Local Python Environment

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 4. Configure Environment Variables

1.  Create a copy of the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Open the `.env` file and fill in the values you collected in the previous steps:
    ```
    NEO4J_URI="your-neo4j-uri"
    NEO4J_USERNAME="your-neo4j-username"
    NEO4J_PASSWORD="your-neo4j-password"
    AWS_REGION="your-aws-region" # e.g., us-east-1
    SAGEMAKER_ENDPOINT_NAME="your-sagemaker-endpoint-name"
    ```
    Also, ensure your local environment is configured with AWS credentials (e.g., via `aws configure` or environment variables).

### 5. Ingest Data into Neo4j

Run the ingestion script to populate your graph database. This script will first wipe the database to ensure a clean slate.

```bash
python ingest_data.py