import re




class TextPreprocesser():
    def __init__(self):
        pass

    def clean_text(self, text):
        print("Cleaning text...\n")
        # Replace multiple newlines and tabs with a single space
        text = re.sub(r'[\n\t]+', ' ', text)  
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text).strip()  
        print("Cleaning complete.\n")
        return text
    
    def chunk_text(self, documents, chunk_size=500, overlap=100):
        print("Chunking text...\n")
        if not isinstance(documents, list):
            temp = []
            temp.append(documents)
            documents = temp
        
        

        chunked_documents = []
        for doc in documents:
            if doc["type"] == "pptx":
                # For PowerPoint, each slide is already a natural chunk
                for i, slide_content in enumerate(doc["content"]):
                    if len(slide_content.strip()) > 0:
                        slide_content = self.clean_text(slide_content)
                        chunked_documents.append({
                            "text": slide_content,
                            "metadata": {
                                "filename": doc["filename"],
                                "slide_number": i + 1,
                                "document_type": "pptx"
                            }
                        })
        print("Chunking complete.\n")
        return chunked_documents
    
    

# def main():
#     DATA_DIR = "../data"
#     ingesterAndParser = IngesterAndParser()
#     textPreprocesser = TextPreprocesser()
#     extracted_text = ingesterAndParser.process_documents(DATA_DIR)
#     chunked_text = textPreprocesser.chunk_text(extracted_text)
#     print(chunked_text)

# if __name__ == "__main__":
#     main()
    