import pathlib
import pickle
from fastembed import TextEmbedding
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

start_time = time.time()
model = TextEmbedding(model="text2vec-base")
QUERY = "What genetic variants are associated with Parkinson's disease?"
#Load all pdf files
end_time = time.time()
print(f"Time taken to load model: {end_time - start_time} seconds")

start_time = time.time()
embeddings_output_folder = Path("embeddings")
pdf_folder = Path("Original_Documents")
pdf_files = list(pdf_folder.glob("*.pdf"))


#Load all the rich data pickle files
start_time = time.time()

all_rich_data = []
for pdf_file in pdf_files:
    with open(embeddings_output_folder / f"{pdf_file.stem}_embeddings.pkl", "rb") as f:
        embeddings = pickle.load(f)
        all_rich_data.extend(embeddings)
# End time
end_time = time.time()
print(f"Time taken to load all rich data: {end_time - start_time} seconds")


# Start time
start_time = time.time()

#Extract just the embeddings from all the dictionaries into a big matrixs
vector_matrix = [embedding["embedding"] for embedding in all_rich_data]
# Convert all_embeddings into a numpy array matrix for similarity computation
vector_matrix = np.array(vector_matrix)

# End time
end_time = time.time()
print(f"Time taken to extract embeddings: {end_time - start_time} seconds")

# Start time
start_time = time.time()

# Embed the query
# Compute the similarity between your query embedding and the matrix
query_embedding = list(model.embed(QUERY))
query_embedding = np.array(query_embedding).reshape(1, -1)

# Compute the similarity between your query embedding and the matrix
similarities = cosine_similarity(query_embedding, vector_matrix)[0]
# End time
end_time = time.time()
print(f"Time taken to compute similarities: {end_time - start_time} seconds")
# End time
end_time = time.time()
print(f"Time taken to compute query embedding: {end_time - start_time} seconds") 

# Sort the simlarity scores to get the indices of the top 5
top_n = 5
top_indices = np.argsort(similarities)[::-1][:top_n]
# Use those indices to look up the corresponding dictionaries and return the text + metadata
top_results = []
for idx in top_indices:

    result = {
        "score": similarities[idx],
        "pdf_file": all_rich_data[idx]["pdf_file"],
        "chunk_num": all_rich_data[idx]["chunk_num"],
        "text": all_rich_data[idx]["text"]
    }
    top_results.append(result)





# comment out beloww

for i, result in enumerate(top_results):
    print(f"Result: {i+1}:")
    print(f"Score: {result['score']}")
    print(f"PDF File: {result['pdf_file']}")
    print(f"Chunk Number: {result['chunk_num']}")
    print(f"Text: {result['text'][:50]}")
    print('--------------------------------')


# Generate answer to the query
answer = ""
for result in top_results:
    answer += result['text']
print(f"Answer to the query: {answer}")
