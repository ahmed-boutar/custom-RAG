from utils.gptService import GPTService
from utils.pineconeService import PineConeService
from embedAndSearch import EmbedAndSearch
from ingestAndParse import IngesterAndParser
from preprocessAndChunk import TextPreprocesser
import dotenv
dotenv.load_dotenv()
import openai
import os

def main():
    # Configuration
    documents_dir = "../data"
    pinecone_index_name = "custom-rag-llm"

    ingesterAndParser = IngesterAndParser()
    textPreprocesser = TextPreprocesser()
    embedAndSearch = EmbedAndSearch()
    pineconeService = PineConeService()
    gptService = GPTService()
    
    
    # Process documents
    print("Processing documents...")
    documents = ingesterAndParser.process_documents(documents_dir)
    
    # Chunk textx
    print("Chunking text...")
    chunks = textPreprocesser.chunk_text(documents)
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = embedAndSearch.generate_embeddings(chunks)
    
    # Initialize Pinecone
    print("Initializing Pinecone...")
    index = pineconeService.initialize_index(pinecone_index_name)
    
    # Upload to Pinecone
    print("Uploading to Pinecone...")
    pineconeService.upload_embeddings(index, embeddings)
    
    # Interactive query loop
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        # Retrieve relevant contexts
        print("Searching for relevant information...")
        contexts = embedAndSearch.semantic_search(query, embeddings)
        
        # Construct prompt
        prompt = gptService.construct_prompt(query, contexts)
        
        # Generate response
        print("Generating response...")
        response = gptService.generate_answer(prompt)
        
        print("\nAnswer:")
        print(response)

if __name__ == "__main__":
    main()