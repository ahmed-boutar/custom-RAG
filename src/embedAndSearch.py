'''
This file contains the EmbedAndSearch class which is responsible 
for generating embeddings for the chunks of text and then searching 
for the most similar chunks to a given query based on cosine similarity'''
import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np


load_dotenv()
class EmbedAndSearch():
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass


    def generate_embeddings(self, chunks):
        embeddings = []
        for chunk in chunks:
            response = self.client.embeddings.create(input=chunk["text"], 
            model="text-embedding-ada-002")

            embedding_vector = response.data[0].embedding
            embeddings.append({
                "text": chunk["text"],
                "embedding": embedding_vector,
                "metadata": chunk["metadata"]
            })
        print('Embeddings Generated Successfully!\n')
        return embeddings

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


    def semantic_search(self, query, embeddings, top_k=10):
        response = self.client.embeddings.create(input=query, 
        model="text-embedding-ada-002")
        
        query_embedding = response.data[0].embedding

        results = []
        for embedding in embeddings:
            similarity = self.cosine_similarity(query_embedding, embedding["values"])
            results.append({
                "text": embedding["metadata"]["text"],
                "similarity": similarity,
                "metadata": embedding["metadata"]
            })

        results = sorted(results, key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

def main():
    embedAndSearch = EmbedAndSearch()

if __name__ == "__main__":
    main()