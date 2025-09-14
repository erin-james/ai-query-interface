from fastapi import FastAPI, Query
from services.query_engine import load_data, query_data
from fastapi.middleware.cors import CORSMiddleware
from services.semantic_parser_spacy import parse_question_spacy

# Initialize FastAPI application
app = FastAPI()

# Load CSV data into memory at startup
data_store = load_data()

# Enable CORS for frontend access (e.g., React Native app)
# You can restrict origins later for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider narrowing this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/query")
def query_csv(
    question: str = Query(..., description="Ask a question about your orders or finances")
) -> dict:
    """
    Endpoint to handle natural language queries about CSV data.
    Accepts a 'question' string and returns a formatted answer.
    """
    response = query_data(question, data_store)
    return {"answer": response}

@app.get("/")
def read_root() -> dict:
    """
    Health check endpoint to confirm the API is running.
    """
    return {"message": "CSV Query API is running"}
