'''
This module contains the PineConeService class which is responsible for interacting with the Pinecone API
to create indexes, upload embeddings and load embeddings from the Pinecone index'''
import dotenv
from pinecone import (Pinecone, ServerlessSpec)
import os
import numpy as np

dotenv.load_dotenv()


class PineConeService():
    
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east1-aws")
    

    def initialize_index(self, index_name, dimension=1536, metric="cosine"):
        '''
        Initialize Pinecone index if it does not exist
        '''
        try:
            if not self.pc.has_index(index_name):
                self.pc.create_index(name=index_name,
                                    dimension=dimension,
                                    metric=metric,
                                    spec= ServerlessSpec(
                                        cloud="aws",
                                        region="us-east-1"
                                    ),)
            else:
                print(f"Index {index_name} already exists")
            
        except Exception as e:
            print(f"Error creating index: {e}")
        
        return self.pc.Index(index_name)
        
        
    
    def upload_embeddings(self, index_name, embeddings, batch_size=100):
        '''
        Upload embeddings to Pinecone index
        '''
        try:
            print("Uploading embeddings to Pinecone...\n")
            index = self.pc.Index(index_name)
            print(f"list(index.list()): {list(index.list())}")
            num_vector_ids = len(list(index.list())[0]) if len(list(index.list())) != 0 else 0
            print(f'num_vectors = {num_vector_ids}')
            for i in range(0, len(embeddings), batch_size):
                batch = embeddings[i:i+batch_size]
                vectors_to_upsert = []
                
                for j, item in enumerate(batch):
                    vector_id = f"vec_{i+j+num_vector_ids}"
                    vectors_to_upsert.append({
                        "id": vector_id,
                        "values": item["embedding"],
                        "metadata": {
                            "text": item["text"],
                            **item["metadata"]
                        }
                    })
                
                index.upsert(vectors=vectors_to_upsert)
                print("Embeddings uploaded successfully!")

        except Exception as e:
            print(f"Error uploading embeddings: {e}")

    def load_stored_embeddings(self, index_name):
        '''
        Load embeddings from Pinecone index
        '''
        try:
            
            index = self.pc.Index(index_name)
            
            print("LOADING EMBEDDINGS FROM PINECONE...\n")
        
            random_embedding = np.random.rand(1536)
            # return the top 10000 vectors. This is my way of retrieving all vectors (since I know
            # that I have less than 10000 vectors in the index)
            # to perform the semantic search locally 
            query_result = index.query(vector=random_embedding.tolist(), top_k=10000, include_values=True, include_metadata=True)
            # print(f'\nQUERY RESULT = {query_result}')
            return query_result['matches']
            
        except Exception as e:
            print(f"Error loading stored embeddings: {e}")
            return None
