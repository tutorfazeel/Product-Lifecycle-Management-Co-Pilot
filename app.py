import os
import json
import time
import streamlit as st
import tiktoken
from dotenv import load_dotenv

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_community.llms.sagemaker_endpoint import SagemakerEndpoint, LLMContentHandler

# Load environment variables
load_dotenv()

# --- AWS SageMaker Endpoint Configuration ---
os.environ["AWS_PROFILE"] = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME")

# --- Neo4j Database Configuration ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# --- FinOps/LLMOps Configuration ---
INPUT_TOKEN_COST = 0.0002 / 1000  # Mock cost for 1K input tokens
OUTPUT_TOKEN_COST = 0.0008 / 1000 # Mock cost for 1K output tokens

# Content handler for Mistral 7B models on SageMaker
class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        # Add instruction formatting for Mistral
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        input_str = json.dumps(
            {"inputs": formatted_prompt, "parameters": {**model_kwargs}}
        )
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        
        print("Raw LLM Response:", response_json) # Good for debugging
        return response_json["generated_text"]
        # ----------------------
# Initialize the token counter
tokenizer = tiktoken.get_encoding("cl100k_base")

@st.cache_resource
def initialize_components():
    """Initialize and cache the Neo4j graph and the LangChain QA chain."""
    # Initialize Neo4j Graph
    graph = Neo4jGraph(
        url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD
    )

    # Force the graph object to refresh its schema information.
    # This ensures the LLM has the most accurate view of the database.
    graph.refresh_schema()

    # Initialize SageMaker LLM
    content_handler = ContentHandler()
    llm = SagemakerEndpoint(
        endpoint_name=SAGEMAKER_ENDPOINT_NAME,
        region_name=AWS_REGION,
        model_kwargs={"max_new_tokens": 512, "top_p": 0.9, "temperature": 0.1},
        content_handler=content_handler,
    )
    
    # Initialize the GraphCypherQAChain
    chain = GraphCypherQAChain.from_llm(
        graph=graph, llm=llm, verbose=True, return_intermediate_steps=True
    )
    return chain

# --- Streamlit UI ---
st.set_page_config(page_title="PLM Co-Pilot 🏭", layout="wide")
st.title("🔩 Product Lifecycle Management (PLM) Co-Pilot")
st.write("Ask me anything about the manufacturing supply chain!")

# Initialize the QA chain
try:
    qa_chain = initialize_components()
except Exception as e:
    st.error(f"Failed to initialize components. Please check your .env file and connections. Error: {e}")
    st.stop()

# Example questions - Use this first to show the update of data in the database
# example_questions = [
#     "Which parts are supplied by companies in Germany?",
#     "List all suppliers for the 'E-Bike Model X' product line.",
#     "What is the compliance status for the part 'Control Unit'?",
#     "Which supplier provides the 'Main Frame'?",
#     "Show me all parts that have failed a REACH compliance standard."
# ]
example_questions = [
    "Which supplier provides the 'Carbon Fiber Frame Assembly'?",
    "List all suppliers from the region Germany.",
    "What is the compliance status for the part 'Guidance System'?",
    "Show me all parts that have failed a RoHS compliance standard.",
    "Which region is 'Helios Energy' from?"
]
st.subheader("Example Questions:")
cols = st.columns(len(example_questions))
for i, question in enumerate(example_questions):
    if cols[i].button(question, key=f"example_{i}"):
        st.session_state.user_question = question

# User input
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""

user_question = st.text_input(
    "Your Question:", 
    key="user_question_input",
    value=st.session_state.user_question,
    placeholder="e.g., Which parts are from suppliers in the USA?"
)

if st.button("Ask Co-Pilot") and user_question:
    # Since endpoint is deleted, we can't run the query.
    # We will show a message to the user.
    # st.warning("The SageMaker endpoint has been deleted to save costs. To ask a new question, please redeploy the endpoint and restart the application.")

    with st.spinner("Thinking..."):
        # --- LLMOps & FinOps Instrumentation ---
        start_time = time.perf_counter()
        
        # Token calculation
        prompt_tokens = len(tokenizer.encode(user_question))

        # Invoke the chain
        result = qa_chain.invoke({"query": user_question})
        
        # Stop timer
        end_time = time.perf_counter()
        latency = end_time - start_time
        
        # Extract results
        answer = result.get("result", "Sorry, I couldn't find an answer.")
        cypher_query = result.get("intermediate_steps", [{}])[0].get("query", "No Cypher query generated.")

        completion_tokens = len(tokenizer.encode(answer))
        total_tokens = prompt_tokens + completion_tokens

        # Cost calculation
        cost = (prompt_tokens * INPUT_TOKEN_COST) + (completion_tokens * OUTPUT_TOKEN_COST)

        # --- Display Results ---
        st.subheader("Answer:")
        st.markdown(answer)
        
        with st.expander("Show Accountability & Metrics 📊"):
            st.subheader("Generated Cypher Query:")
            st.code(cypher_query, language="cypher")
            
            st.subheader("Performance & Cost:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="End-to-End Latency", value=f"{latency:.2f}s")
            with col2:
                st.metric(label="Total Tokens", value=f"{total_tokens}")
                st.caption(f"Prompt: {prompt_tokens}, Completion: {completion_tokens}")
            with col3:
                st.metric(label="Estimated Cost", value=f"${cost:.6f}")