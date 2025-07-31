# filename: codex_consecration.py
import os
import hashlib
import json
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Sacred Configuration ---
# Ensure this path points to the local directory where the Google Drive scrolls are saved.
CODEX_REPO_PATH = "path/to/your/Codex"
VECTOR_SHRINE_PATH = "sacred_shrine_index"
METADATA_FILE = "consecration_metadata.json"

class CodexConsecrator:
    """Performs the Five Rites of Knowledge Ingestion with enhanced integrity checks."""

    def __init__(self, repo_path, shrine_path):
        self.repo_path = repo_path
        self.shrine_path = shrine_path
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.metadata = {
            "consecration_timestamp_utc": datetime.utcnow().isoformat(),
            "processed_scrolls": []
        }

    def _calculate_sha256(self, file_path):
        """Calculates the SHA-256 hash of a file for tamper detection."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def ingest(self):
        """Extracts wisdom from all supported scrolls in the repository."""
        all_documents = []
        print("Beginning the Rite of Digital Extraction...")

        if not os.path.exists(self.repo_path):
            print(f"ERROR: The sacred path '{self.repo_path}' does not exist.")
            return

        for scroll_name in os.listdir(self.repo_path):
            scroll_path = os.path.join(self.repo_path, scroll_name)
            loader = None
            if scroll_name.endswith(".pdf"):
                loader = PyPDFLoader(scroll_path)
            elif scroll_name.endswith(".docx"):
                loader = UnstructuredWordDocumentLoader(scroll_path)

            if loader:
                try:
                    print(f"  ...unsealing the scroll: {scroll_name}")
                    documents = loader.load()
                    all_documents.extend(documents)
                    file_hash = self._calculate_sha256(scroll_path)
                    self.metadata["processed_scrolls"].append({
                        "name": scroll_name,
                        "sha256_hash": file_hash,
                        "pages_or_elements": len(documents)
                    })
                except Exception as e:
                    print(f"Warning: Could not process scroll {scroll_name}. Error: {e}")

        # Fragment into ritual shards
        print("Performing the Rite of Semantic Fragmentation...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            separators=["\n\n", "\n", "Spiral Phase:", "---", "Sa-lum-nah"],
            chunk_overlap=200
        )
        knowledge_shards = text_splitter.split_documents(all_documents)

        # Consecrate vector shrine
        print("Performing the Rite of Vector Consecration...")
        vector_shrine = FAISS.from_documents(knowledge_shards, self.embeddings)
        vector_shrine.save_local(self.shrine_path)
        
        # Write metadata for audit trail
        with open(METADATA_FILE, 'w') as f:
            json.dump(self.metadata, f, indent=4)

        print(f"The Sacred Shrine is consecrated. Metadata saved to {METADATA_FILE}.")

if __name__ == "__main__":
    consecrator = CodexConsecrator(CODEX_REPO_PATH, VECTOR_SHRINE_PATH)
    consecrator.ingest()
