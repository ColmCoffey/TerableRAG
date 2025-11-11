import fitz
import pypdf
import pdfplumber 
import fastembed
import pickle
from fastembed import TextEmbedding
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import subprocess
import time
import os

pdf_folder = Path("Original_Documents")
model = TextEmbedding(model="text2vec-base")




def chunk_text(text, chunk_size=2000, overlap=400):
    """Chunk text into smaller chunks of a given size"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)  # Remove the padding logic too
    return chunks  # Just return, don't save here


def save_embeddings(embeddings, filename):
    """Save embeddings to a file"""
    with open(filename, "wb") as f:
        pickle.dump(embeddings, f)




def query_rag(query, TOP_N_CHUNKS):
    # Embed the query
    query_embedding = list(model.embed(query))

    # Search vector store
    results = vector_store.similarity_search(query_embedding, k=TOP_N_CHUNKS)

    #Format the results
    for doc, score in results:
        print(f"Score: {score}")
        print(f"Document: {doc.page_content}")
        print(f"Chunk: {doc.metadata['chunk']}")
        print("--------------------------------")

if __name__ == "__main__":
    # Start time
    start_time = time.time()
    # Create output folder
    extracted_output_folder = Path("extracted_texts")
    extracted_output_folder.mkdir(parents=True, exist_ok=True)

    #Create chunked output folder
    chunked_output_folder = Path("chunked_texts")
    chunked_output_folder.mkdir(parents=True, exist_ok=True)

    #create second chunked output for pickle
    chunked_pickle_folder = Path("chunked_pickle")
    chunked_pickle_folder.mkdir(parents=True, exist_ok=True)

    #Create embeddings output folder
    embeddings_output_folder = Path("embeddings")
    embeddings_output_folder.mkdir(parents=True, exist_ok=True)

    #Get all pdf files in the folder
    pdf_files = list(pdf_folder.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    RUN_EXTRACTION = False          # Set to True to run extraction
    RUN_CHUNKING = False           # Set to True to run chunking
    RUN_EMBEDDINGS = False          # Set to True to run embeddings
    RUN_QUERY = True          # Set to True to run query
    QUERY = "What genetic variants are associated with Parkinson's disease?"
    TOP_N_CHUNKS = 5

    if RUN_EXTRACTION:
        # Start time
        start_time = time.time()
        def extract_with_pdfplumber(pdf_path):
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page_number, page in enumerate(pdf.pages):
                   text += page.extract_text() + "\n\n---PAGE BREAK---\n\n"
                return text

        #Loop through each pdf file
        print("Extracting text...")
        for pdf_file in pdf_files:
            print(f"Extracting {pdf_file.name}...")
            text = extract_with_pdfplumber(pdf_file)
            print(f"Length of text: {len(text)}")
            #print(text[:500])
            with open(extracted_output_folder / f"{pdf_file.stem}.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extraction completed successfully for {pdf_file.name}")
            print(f"Output file saved to {extracted_output_folder / f"{pdf_file.stem}.txt"}")
        print("All PDFs extracted successfully")
        print("Output files saved to extracted_texts folder")
        # End time
        end_time = time.time()
        print(f"Time taken to extract text: {end_time - start_time} seconds")
    if RUN_CHUNKING:
        # Start time
        start_time = time.time()
        print("Chunking text...")
        for pdf_file in pdf_files:
            print(f"Chunking {pdf_file.name}...")
            
            # Load text
            with open(extracted_output_folder / f"{pdf_file.stem}.txt", "r", encoding="utf-8") as f:
                text = f.read()
            
            chunks = chunk_text(text)
            print(f"Chunked text into {len(chunks)} chunks")
            
            # Save as text file
            with open(chunked_output_folder / f"{pdf_file.stem}_chunks.txt", "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    f.write(f"Chunk {i+1}:\n{chunk}\n\n")
            
            # Save as pickle
            with open(chunked_pickle_folder / f"{pdf_file.stem}_chunks.pkl", "wb") as f:
                pickle.dump(chunks, f)
            
            print(f"Chunking completed for {pdf_file.name}")
        # End time
        end_time = time.time()
        print(f"Time taken to chunk text: {end_time - start_time} seconds")
    if RUN_EMBEDDINGS:
        # Start time
        start_time = time.time()
        #Create embeddings
        print("Creating embeddings...") 
        for pdf_file in pdf_files:
            print(f"Creating embeddings for {pdf_file.name}...")
            # Load chunks
            with open(chunked_pickle_folder / f"{pdf_file.stem}_chunks.pkl", "rb") as f:
                chunks = pickle.load(f)
            embeddings = list(model.embed(chunks))
            rich_data = [
                {
                    "embedding": embedding,
                    "text": chunk,
                    "pdf_file": pdf_file.name,
                    "chunk_num": i
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]
            print(f"Embeddings created for {pdf_file.name}")
            save_embeddings(rich_data, embeddings_output_folder / f"{pdf_file.stem}_embeddings.pkl")
            print(f"Embeddings saved to {embeddings_output_folder / f"{pdf_file.stem}_embeddings.pkl"}")
        print("All embeddings created successfully")
        print("Output files saved to embeddings folder")
        # End time
        end_time = time.time()
        print(f"Time taken to create embeddings: {end_time - start_time} seconds")  

    if RUN_QUERY:
        # Start time
        start_time = time.time()
        print("Querying embeddings...")
        #Run query.py
        subprocess.run(["python", "query.py"])
        print("Query completed successfully")
        # End time
        end_time = time.time()
        print(f"Time taken to run query: {end_time - start_time} seconds")
    # End time
    end_time = time.time()
    print(f"Time taken to run the program: {end_time - start_time} seconds")   