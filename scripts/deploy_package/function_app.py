import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fastembed import TextEmbedding
import json
import os

app = func.FunctionApp()
model = TextEmbedding(model="text2vec-base")

@app.route(route="query", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def query_rag(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # 1. Get query from request
        logging.info("Processing query request")
        
        try:
            req_body = req.get_json()
        except ValueError:
            logging.error("Invalid JSON in request body")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        query = req_body.get("query")
        if not query:
            logging.error("Missing query parameter")
            return func.HttpResponse(
                json.dumps({"error": "Missing 'query' parameter in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f"Query: {query}")
        
        # 2. Load embeddings from blob storage
        conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not configured")
            return func.HttpResponse(
                json.dumps({"error": "Storage connection string not configured"}),
                status_code=500,
                mimetype="application/json"
            )
        
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_service.get_container_client("embeddings")

        all_rich_data = []
        blobs = container_client.list_blobs()
        for blob in blobs:
            if blob.name.endswith(".pkl"):
                blob_client = container_client.get_blob_client(blob.name)
                data = blob_client.download_blob().readall()
                embeddings = pickle.loads(data)
                all_rich_data.extend(embeddings)
        
        if not all_rich_data:
            logging.error("No embeddings found in blob storage")
            return func.HttpResponse(
                json.dumps({"error": "No embeddings found in storage"}),
                status_code=404,
                mimetype="application/json"
            )
        
        logging.info(f"Loaded {len(all_rich_data)} embeddings")
        
        # Extract just the embeddings from all the dictionaries into a big matrix
        vector_matrix = [embedding["embedding"] for embedding in all_rich_data]
        vector_matrix = np.array(vector_matrix)

        # 3. Embed query
        query_embedding = list(model.embed(query))
        query_embedding = np.array(query_embedding).reshape(1, -1)

        # 4. Compute similarities
        similarities = cosine_similarity(query_embedding, vector_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][:5]
        
        # 5. Return top results as JSON
        top_results = []
        for idx in top_indices:
            result = {
                "score": float(similarities[idx]),  # Convert numpy float to Python float
                "pdf_file": all_rich_data[idx]["pdf_file"],
                "chunk_num": int(all_rich_data[idx]["chunk_num"]),  # Convert numpy int to Python int
                "text": all_rich_data[idx]["text"]
            }
            top_results.append(result)

        logging.info(f"Returning {len(top_results)} results")
        return func.HttpResponse(
            json.dumps(top_results),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f"Error in query_rag: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


