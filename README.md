# Custom RAG 

This project is an attempt to create a custom RAG system, where I can upload my lecture slides and have an LLM answer my questions with content from the slides and sources referencing each slide. The LLM used is gpt-4o. 

This repo us currently being used for a hosted streamlit app. 

# How it works 
 
 When you upload a pptx or a collection of powerpoint files, the app will process each file and:
 - Parses all the slides to extract the text 
 - Chunks the text (you can look into preprocessAndChunk.py to learn about the chunking strategy => very naive since I haven't used any library and tried to do it on my own)
 - Generates embeddings from the text using gpt-4o
 - Saves the embeddings to a pinecone index 
 
 When you prompt the LLM for information, it will:
 - Turn the prompt into an embedding 
 - Retrieve all of the embeddings from pinecone (I am using my own semantic search with cosine similarity. Just wanted to implement it for practice)
 - Return the top 5 most similar embeddings 
 - Extract the text that represents the embeddings 
 - Add the text to the LLM prompt
 - Generate a response and includes the sources (file and slide the information comes from)