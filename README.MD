# AWS GraphRAG PLM Co-Pilot Demo

This project demonstrates a **Product Lifecycle Management (PLM) Co-Pilot** built with a **GraphRAG architecture**. It uses **Neo4j** for the knowledge graph, an **open-source LLM** hosted on **AWS SageMaker**, and a **Streamlit** web interface. This repository contains all the code and instructions needed for a full demonstration.

From a **Technical Manager's** perspective, this project isn't just a technical demo; it's a showcase of a modern **MLOps** workflow, complete with **FinOps** instrumentation and real-world deployment challenges.

---

## ⚙️ Architecture

- **Data Source:** CSV files representing parts, suppliers, compliance, and their relationships.
- **Knowledge Graph:** A Python script (`ingest_data.py`) populates a **Neo4j AuraDB** instance.
- **LLM Backend:** An open-source model (e.g., **Mistral 7B**) is deployed on a dedicated **AWS SageMaker** endpoint for inference.
- **RAG Orchestration:** LangChain's `GraphCypherQAChain` translates natural language questions into **Cypher queries**, executes them against the graph, and uses the results to generate a final answer.
- **Frontend:** A **Streamlit** application (`app.py`) provides a UI for users to ask questions and view results, including key **LLMOps/FinOps** metrics like latency and cost.

---

## 🚀 Setup & Execution Guide

This project uses **just** as a command runner to simplify setup and execution.

### 1. Prerequisites

Before you begin, ensure you have the following ready:

- **Neo4j AuraDB Instance:** A free instance from Neo4j AuraDB. You will need your **Connection URI**, **Username**, and **Password**.
- **AWS SageMaker Endpoint:** An active SageMaker endpoint running a model like **Mistral 7B Instruct**. You will need the **Endpoint Name** and your **AWS Region**.
- **Python:** Python **3.10+** installed on your system.
- **Just:** The `just` command runner. If you don't have it, install it via your package manager (for example):
    
    - macOS:
        4-space indentation for code block
        brew install just
    - Windows (Chocolatey):
        4-space indentation for code block
        choco install just
    - Linux (apt):
        4-space indentation for code block
        sudo apt install just

> (Note: The above package manager commands are shown as plain text — when you paste into your README, replace the explanatory lines as needed.)

### 2. Configure Environment Variables

Create your local environment file from the template:

    cp .env.example .env

Open the `.env` file and fill in the credentials you collected in the prerequisite step:

    NEO4J_URI="your-neo4j-uri"
    NEO4J_USERNAME="your-neo4j-username"
    NEO4J_PASSWORD="your-neo4j-password"
    AWS_REGION="your-aws-region"
    SAGEMAKER_ENDPOINT_NAME="your-sagemaker-endpoint-name"

### 3. Run the Application with just

With your `.env` file configured, running the entire project is as simple as executing these three commands from your terminal.

**Setup the Environment**  
This command creates a Python virtual environment and installs all required libraries.

    just setup

**Ingest Data into Neo4j**  
This command wipes the database and loads the data from the `mock_data/` folder.

    just ingest

**Launch the Co-Pilot App**  
This command starts the Streamlit web application.

    just run

You can now access the **PLM Co-Pilot** in your browser at:  
http://localhost:8501

---