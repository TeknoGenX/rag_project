import os
import chromadb
from tqdm import tqdm
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from config import setup_settings, PDF_DIR, CHROMA_DB_DIR, COLLECTION_NAME

def ingest_pdfs():
    # 1. Inisialisasi pengaturan
    setup_settings()
    
    # 2. Siapkan ChromaDB
    db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 3. Ambil daftar PDF
    if not os.path.exists(PDF_DIR):
        print(f"Folder {PDF_DIR} tidak ditemukan.")
        return

    all_files = [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    total_files = len(all_files)
    
    if total_files == 0:
        print("Tidak ada file PDF ditemukan di folder data_pdf.")
        return

    print(f"Memulai proses embedding {total_files} file PDF ke ChromaDB...")
    
    # 4. INISIASI INDEX SATU KALI DI LUAR LOOP
    # Jika collection kosong, dia akan membuat index kosong yang siap diisi
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )
    
    # 5. Siapkan file log untuk mencatat error (overwrite jika sudah ada)
    log_file = "error_log.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Log Error Pemrosesan PDF ({total_files} file)\n")
        f.write("="*50 + "\n")

    failed_count = 0

    # 6. Loop dengan Try-Except yang tangguh
    for file_path in tqdm(all_files, desc="Processing PDFs"):
        try:
            # SimpleDirectoryReader membaca satu PDF. Menghasilkan list of Document (per halaman)
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            
            # Jika dokumen kosong (hanya berisi gambar tanpa teks)
            if not documents:
                raise ValueError("PDF kosong atau tidak mengandung teks yang bisa dibaca.")
                
            # Masukkan dokumen (halaman) satu per satu ke dalam Index yang sudah ada
            for doc in documents:
                index.insert(doc)
            
        except Exception as e:
            # Jika terjadi error (corrupt, password, dll), loop TIDAK AKAN berhenti.
            failed_count += 1
            
            # Catat nama file dan alasan error ke dalam file log
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[GAGAL] File: {file_path}\n")
                f.write(f"        Alasan: {str(e)}\n")
                f.write("-" * 50 + "\n")

    print("\n" + "="*50)
    print("PROSES INGESTI SELESAI!")
    print(f"Total berhasil : {total_files - failed_count} file")
    print(f"Total gagal    : {failed_count} file")
    print("="*50)
    
    if failed_count > 0:
        print(f"⚠️ Silakan buka file '{log_file}' untuk melihat daftar PDF yang bermasalah.")

if __name__ == "__main__":
    ingest_pdfs()