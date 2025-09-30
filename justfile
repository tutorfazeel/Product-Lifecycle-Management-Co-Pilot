# Justfile for the AWS GraphRAG PLM Co-Pilot

# Default command: show available commands
default:
    @echo "Usage: just [COMMAND]"
    @echo ""
    @echo "Available commands:"
    @echo "  setup    -> Create Python virtual environment and install dependencies"
    @echo "  ingest   -> Run the data ingestion script to populate Neo4j"
    @echo "  run      -> Launch the Streamlit application"
    @echo "  clean    -> Remove virtual environment and pycache files"

# Set the Python interpreter command
# Use `python3.12` if available, otherwise fall back to `python3`
PYTHON := `command -v python3.12 || command -v python3`
VENV_DIR := ".venv"

# Setup the virtual environment and install dependencies
setup:
    @echo "🐍 Creating Python 3.12 virtual environment in './{{VENV_DIR}}'..."
    {{PYTHON}} -m venv {{VENV_DIR}}
    @echo "📦 Installing dependencies from requirements.txt..."
    ./{{VENV_DIR}}/bin/pip install --upgrade pip
    ./{{VENV_DIR}}/bin/pip install -r requirements.txt
    @echo "✅ Setup complete! Activate the environment with: source {{VENV_DIR}}/bin/activate"

# Run the data ingestion script
ingest:
    @echo "🚚 Ingesting data into Neo4j..."
    @source {{VENV_DIR}}/bin/activate && python ingest_data.py

# Run the Streamlit application
run:
    @echo "🚀 Launching the PLM Co-Pilot..."
    streamlit run app.py
# @source {{VENV_DIR}}/bin/activate && 
# Clean up the project directory
clean:
    @echo "🧹 Cleaning up project..."
    rm -rf {{VENV_DIR}}
    find . -type d -name "__pycache__" -exec rm -r {} +
    @echo "🗑️ Cleanup complete."
