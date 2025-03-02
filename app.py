'''
This is the main application file for the Lecture Material RAG Assistant (streamlit app)
'''
import streamlit as st
import boto3
import io
import os
import tempfile
from pptx import Presentation
from openai import OpenAI
import time

from src.ingestAndParse import IngesterAndParser
from src.preprocessAndChunk import TextPreprocesser
from src.embedAndSearch import EmbedAndSearch
from src.utils.awsService import S3DocumentProcessor
from src.utils.gptService import GPTService
from src.utils.pineconeService import PineConeService


def main():
    st.title("📚 Lecture Material RAG Assistant")
    st.markdown("Upload lecture slides and ask questions about your course materials.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize services (pipelines)
    ingesterAndParser = IngesterAndParser()
    textPreprocesser = TextPreprocesser()
    embedAndSearch = EmbedAndSearch()
    pineconeService = PineConeService()
    gptService = GPTService()
    s3processor = S3DocumentProcessor()
    
    # Sidebar for file upload and management
    with st.sidebar:
        st.header("Document Management")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Lecture Materials", 
            type=["pdf", "pptx"], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            
            # Process button
            if st.button("Process New Files"):
                existing_files = s3processor.list_files()
                with st.spinner("Processing files..."):
                    for uploaded_file in st.session_state.uploaded_files:
                        if uploaded_file.name in existing_files:
                            st.info(f"{uploaded_file.name} has already been processed!")
                            continue
                        else:
                            st.info(f"Uploading {uploaded_file.name} to S3...")
                            print(f"UPLOADED FILE OBJ = {uploaded_file}")
                            s3_key = s3processor.upload_file_to_s3(uploaded_file)
                            
                            if s3_key:
                                try:
                                    st.info(f"Processing and indexing {uploaded_file.name}...")
                                    # Extract text from uploaded file 
                                    doc = ingesterAndParser.extract_text_from_pptx(uploaded_file)

                                    # Chunk text 
                                    chunks = textPreprocesser.chunk_text(doc)

                                    # Generate embeddings 
                                    embeddings = embedAndSearch.generate_embeddings(chunks)

                                    pineconeService.initialize_index("custom-rag-llm")

                                    # upload to pinecone
                                    pineconeService.upload_embeddings("custom-rag-llm", embeddings)

                                    st.success(f"Successfully processed {uploaded_file.name}")
                                
                                except Exception as e:
                                    st.error(f"Error processing {uploaded_file.name}: {e}")
                                
                # Clear the uploaded files list after processing
                st.session_state.uploaded_files = []
                st.rerun()
        
        # Display existing files in S3 bucket
        st.subheader("Existing Files")
        existing_files = s3processor.list_files()
        if existing_files:
            for file_key in existing_files:
                filename = file_key.split("/")[-1]
                st.text(f"• {filename}")
        else:
            st.info("No files found in S3 bucket")
    
    # Chat interface
    st.header("Chat with your Lecture Assistant")
    
    
    # Display chat messages from history
    # Setting the messages by role (user or assistant)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input for new message
    if prompt := st.chat_input("Ask a question about your lecture materials"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Search for relevant contexts
            with st.spinner("Searching lecture materials..."):
                # Load stored embeddings from pinecone index
                stored_embeddings = pineconeService.load_stored_embeddings("custom-rag-llm")
                # Generate embeddings
                print("Generating embeddings for Query...")
                contexts = embedAndSearch.semantic_search(prompt, stored_embeddings)
                print(f'\nDEBUGGING CONTEXT: {contexts}')
        
            # Check if contexts were found
            if not contexts:
                response = "I couldn't find any relevant information in your lecture materials. Please upload some lecture files or try a different question."
            else:
                # Construct prompt with contexts
                full_prompt = gptService.construct_prompt(prompt, contexts)
                
                # Generate response
                with st.spinner("Generating response..."):
                    response = gptService.generate_answer(full_prompt)
            
            # Display source information
            st.markdown("#### Sources:")
            for context in contexts:
                st.markdown(f"- {context['metadata']['filename']} (slide number: {context['metadata']['slide_number']})")
            
            # Update message placeholder with response
            message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})



if __name__=="__main__":
    main()