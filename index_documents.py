

def extract_text(file_path: str) -> str:
    pass

def get_chunks(text: str, chunk_size=1000, chunk_overlap=200) -> List[str]:
    pass


def get_embeddings(texts: List[str]):
    pass


def save_to_db(file_name: str, chunks: List[str], embeddings: List[List[float]], strategy: str):
    pass


def process_file(file_path: str):
    pass


if __name__ == "__main__":

    path = "my_document.pdf" 
    if os.path.exists(path):
        process_file(path)
    else:
        print("ERROR: File not found, try again\n")