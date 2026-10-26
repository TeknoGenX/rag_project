import chromadb
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from config import setup_settings, CHROMA_DB_DIR, COLLECTION_NAME

def load_index():
    """Memuat database vektor yang sudah ada dari hardisk."""
    setup_settings()
    
    db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Muat index dari Vector Store tanpa membaca PDF ulang
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    return index

def chat_interface():
    print("Memuat database PDF lokal...")
    try:
        index = load_index()
    except Exception as e:
        print(f"Error memuat database. Pastikan ingest_documents.py sudah dijalankan. Error: {e}")
        return

    # Buat Template Prompt agar AI merespons sesuai keinginan sistem
    qa_prompt_tmpl_str = (
        "Anda adalah asisten pencari dokumen. Jawab HANYA berdasarkan konteks "
        "yang diberikan. Jika tidak tahu, katakan tidak tahu.\n\n"
        "Konteks:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Pertanyaan: {query_str}\n"
        "Jawaban:"
    )
    qa_prompt = PromptTemplate(qa_prompt_tmpl_str)

    # Atur sistem pencarian (Top K = 5 dokumen paling relevan)
    # Gunakan text_qa_template, BUKAN system_prompt
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        text_qa_template=qa_prompt
    )

    print("\n==============================================")
    print("🤖 CLI Asisten PDF Lokal (Ketik 'exit' atau 'quit' untuk keluar)")
    print("==============================================\n")

    while True:
        user_query = input("📝 Pertanyaan: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Keluar dari terminal. Sampai jumpa!")
            break
        if not user_query.strip():
            continue

        print("🔍 Sedang mencari dan merangkum...")
        try:
            response = query_engine.query(user_query)
            
            print("\n💡 Jawaban:")
            print(response.response)
            
            # Ekstrak referensi dokumen untuk transparansi
            print("\n📚 Sumber Referensi:")
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    file_name = node.metadata.get('file_name', 'Tidak diketahui')
                    page_num = node.metadata.get('page_label', 'N/A')
                    score = round(node.score, 3) if node.score else "N/A"
                    print(f"  - File: {file_name} (Hal: {page_num}) | Relevansi: {score}")
            else:
                print("  - Tidak ada dokumen sumber yang ditemukan.")
            print("-" * 50)
            
        except Exception as e:
            print(f"\n❌ Terjadi kesalahan saat melakukan kueri: {e}")
            print("-" * 50)

if __name__ == "__main__":
    chat_interface()