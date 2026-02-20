import os
import uuid
import argparse
import psycopg2
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from psycopg2.extras import execute_values
# extractions tools
from docx import Document
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

#load and set the config from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
DB_URL = os.getenv("POSTGRES_URL")

def extract_text(file_path: str) -> str:
    """Extract text from PDF or DOCX files"""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Format is not supported, only PDF / DOCX")
    
    return text.strip()

def get_chunks(text: str, chunk_size=1000, chunk_overlap=200) -> List[str]:
    """Seperate the chunks form the given file"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)


def get_embeddings(texts: List[str]):
    """Vector creation with Gemini API"""
    model = 'gemini-embedding-001'
    response = client.models.embed_content(
            model=model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )    
    return [e.values for e in response.embeddings]


def save_to_db(file_name: str, chunks: List[str], embeddings: List[List[float]], strategy: str):
    """Saving the vectors to PostgreSQL with pgvector"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_vectors (
            id UUID PRIMARY KEY,
            chunk_text TEXT,
            embedding vector(3072),
            filename TEXT,
            split_strategy TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    data = []
    for text, vector in zip(chunks, embeddings):
        data.append((str(uuid.uuid4()), text, vector, file_name, strategy))

    insert_query = """
        INSERT INTO document_vectors (id, chunk_text, embedding, filename, split_strategy)
        VALUES %s
    """
    execute_values(cur, insert_query, data)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f" Saved and insert - {len(chunks)} - succesfully.")


def process_file(file_path: str):
    """Resposible for all the staging process"""
    print(f"Processing file: {file_path}...")
    
    # 1. Exctract 
    full_text = extract_text(file_path)
    
    # 2. seperate to a fixed size chuncks with overlap
    strategy = "Fixed-size with overlap (1000/200)"
    chunks = get_chunks(full_text)
    
    # 3. Embeddings
    embeddings = get_embeddings(chunks)
    
    # 4. saving to DB
    save_to_db(os.path.basename(file_path), chunks, embeddings, strategy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index a document (PDF/DOCX) into the vector database.")
    parser.add_argument(
        "--file", 
        "-f", 
        type=str, 
        help="The valid path to the file you want to index (e.g., ./my_doc.pdf)"
    )
    args = parser.parse_args()
    if args.file:
        path = args.file
        if os.path.exists(path):
            process_file(path)
        else:
            print(f"ERROR: File not found at '{path}'. Please check the path and try again.\n")
    else:
        print("ERROR: No file provided. Usage: python index_documents.py --file [path]")
        parser.print_help()