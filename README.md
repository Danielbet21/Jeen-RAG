# Jeen - RAG 🚀

**Document Indexing System using Gemini & PostgreSQL**

Jeen - RAG is a specialized tool for processing and indexing PDF and DOCX documents into a vector database. It utilizes Google Gemini to generate 3072-dimensional embeddings and stores them in PostgreSQL via `pgvector` for future semantic retrieval.

---

## 📋 Prerequisites

* **Python:** 3.10+ recommended (Python 3.9 is compatible but triggers deprecation warnings).
* **Database:** PostgreSQL instance with the `pgvector` extension installed.
* **API Key:** A valid Google Gemini API key.

---

## ⚙️ Setup & Installation

1. **Clone the Project:**
```bash
git clone <repository-url>
cd Jeen-RAG

```


2. **Environment Configuration:**
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
POSTGRES_URL=postgresql://user:password@localhost:5432/your_db_name

```


3. **Install Dependencies:**
```bash
pip install -r req.txt

```



---

## 🚀 Usage & Expected Output

To index a document, execute the script via your terminal. Currently, the script is configured to look for a specific file path or can be updated to accept arguments.

### Running the Script:

```bash
python index_documents.py --file ./my_document.pdf

```

### What to Expect (Workflow):

When you run the script, the following actions occur automatically:

1. **Database Initialization:** The script checks if the `vector` extension and the `document_vectors` table exist. If not, it creates them with a `vector(3072)` column.
2. **Text Extraction:** The system reads the content of your `.pdf` or `.docx` file.
3. **Chunking:** The text is divided into manageable segments (1000 characters each) to maintain semantic context.
4. **Embedding Generation:** Each chunk is sent to the Gemini `v1beta` API using the `gemini-embedding-001` model.

### Terminal Output:

Upon a successful run, you will see the following progress messages in your console:

```text
Processing file: my_document.pdf...
Successfully created/verified database schema.
Saved and insert - 1 - successfully.

```

*(Note: The number will vary based on how many text chunks were generated from your document.)*

---

## 🛠️ Technical Specifications

* **Embedding Model:** `gemini-embedding-001` (via Google GenAI SDK).
* **Vector Dimension:** **3072** (Optimized for high-precision retrieval).
* **Chunking Strategy:** Recursive character splitting (1000 size / 200 overlap).
* **Storage:** PostgreSQL with `pgvector` using Cosine Similarity logic.

---

## ⚠️ Troubleshooting

* **Database Error:** Ensure your `POSTGRES_URL` is correct and the database user has permission to create extensions.
* **404 Not Found:** The script uses the `v1beta` API version to ensure access to the latest embedding models. Ensure your API key is valid in [Google AI Studio](https://aistudio.google.com/).
* **Dimension Mismatch:** This system is hardcoded for 3072 dimensions. If you previously used a 768-dimension table, the script will drop and recreate the table to match the new model requirements.