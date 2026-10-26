from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Direktori Proyek
PDF_DIR = "./data_pdf"
CHROMA_DB_DIR = "./db_chroma"
COLLECTION_NAME = "pdf_arsip_1000"

# Konfigurasi Model Ollama Lokal
LLM_MODEL = "qwen2.5-coder:7b"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_TIMEOUT = 3600.0  # Diubah menjadi 3600 agar konsisten dengan kebutuhan sebelumnya

def setup_settings():
    """Menerapkan konfigurasi LLM dan Embedding secara global."""
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=OLLAMA_TIMEOUT)
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL)
    
    # Pengaturan pemotongan teks
    Settings.chunk_size = 1000
    Settings.chunk_overlap = 150
    
    # KUNCI UTAMA: Batasi teks yang dikirim ke Ollama (1 potongan per proses)
    Settings.embed_batch_size = 1