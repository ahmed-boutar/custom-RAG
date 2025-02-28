import dotenv
from pinecone import (Pinecone, ServerlessSpec)
import os
import numpy as np

dotenv.load_dotenv()


class PineConeService():
    
    def __init__(self):
        # pinecone.init(api_key= os.getenv("PINECONE_API_KEY"), environment="us-east1-aws")
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east1-aws")
    

    def initialize_index(self, index_name, dimension=1536, metric="cosine"):
        try:
            if index_name not in self.pc.list_indexes():
                self.pc.create_index(name=index_name,
                                    dimension=dimension,
                                    metric=metric,
                                    spec= ServerlessSpec(
                                        cloud="aws",
                                        region="us-east-1"
                                    ),)
            else:
                print('AHHHHHHHHHH')
                print(f"Index {index_name} already exists")
                
        
        except Exception as e:
            print(f"Error creating index: {e}")
        
        return self.pc.Index(index_name)
        
        
    
    def upload_embeddings(self, index_name, embeddings, batch_size=100):
        try:
            print("Uploading embeddings to Pinecone...\n")
            index = self.pc.Index(index_name)
            for i in range(0, len(embeddings), batch_size):
                batch = embeddings[i:i+batch_size]
                vectors_to_upsert = []
                
                for j, item in enumerate(batch):
                    vector_id = f"vec_{i+j}"
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
        try:
            
            index = self.pc.Index(index_name)
            
            print("LOADING EMBEDDINGS FROM PINECONE...\n")
        
            random_embedding = np.random.rand(1536)
            query_result = index.query(vector=random_embedding.tolist(), top_k=10000, include_values=True, include_metadata=True)
            # stored_embeddings = np.array([match["values"] for match in query_result['matches']])
            # TODO CHECK IF THIS IS HOW IT's DONE
        
            return query_result['matches']
            
        except Exception as e:
            print(f"Error loading stored embeddings: {e}")
            return None
