import boto3
import os
import dotenv
import io
from pptx import Presentation

dotenv.load_dotenv()

class S3DocumentProcessor:
    def __init__(self):
        # Initialize AWS session
        self.s3 = boto3.client(
            's3',
            aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION")
        )
        self.bucket_name = "custom-rag-llm"
    
    def upload_file_to_s3(self, file):
        """
        Upload one file  to S3 bucket
        """
        try:
            print(f'Uploading {file.name} to S3...\n')
            uploaded_files = []

            if file.name.endswith(('.pptx', '.pdf')):
                s3_key = file.name
                self.s3.upload_fileobj(file, self.bucket_name, s3_key)
                uploaded_files.append(s3_key)
            
            print(f"Uploaded {file.name} successfully")
            return s3_key

                    
        except Exception as e:
            print(f"Error uploading file to S3: {e}")
    
    def upload_to_s3(self, local_directory, s3_prefix=''):
        """
        Upload all files from a local directory to S3 bucket
        """
        try:
            print('Uploading files to S3...\n')
            uploaded_files = []
            
            for filename in os.listdir(local_directory):
                if filename.endswith(('.pptx', '.pdf')):
                    local_path = os.path.join(local_directory, filename)
                    s3_key = os.path.join(s3_prefix, filename) if s3_prefix else filename
                    
                    print(f"Uploading {filename} to S3...")
                    self.s3.upload_file(local_path, self.bucket_name, s3_key)
                    uploaded_files.append(s3_key)
                    print(f"Uploaded {filename} successfully")
        except Exception as e:
            print(f"Error uploading files to S3: {e}")
        
        return uploaded_files
    
    def list_files(self, prefix=''):
        """
        List all files in the S3 bucket with the given prefix
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [item['Key'] for item in response['Contents'] 
                    if item['Key'].endswith(('.pptx', '.pdf'))]
        except Exception as e:
            print(f"Error listing files in S3: {e}")
    
    def extract_from_s3_pptx(self, s3_key):
        """
        Extract text from a PowerPoint file stored in S3
        """
        try:
            print("Extracting text from PowerPoint file in S3...\n")
            # Get the file from S3
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read()
            
            # Load the PowerPoint from the in-memory file
            pres = Presentation(io.BytesIO(content))
            text_content = []
            
            for slide in pres.slides:
                slide_text = []
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slide_text.append(shape.text)
                text_content.append("\n".join(slide_text))
            
            return text_content
        
        except Exception as e:
            print(f"Error extracting text from PowerPoint file in S3: {e}")
    
    # def extract_from_s3_pdf(self, s3_key):
    #     """
    #     Extract text from a PDF file stored in S3
    #     """
    #     # Get the file from S3
    #     response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
    #     content = response['Body'].read()
        
    #     # Load the PDF from the in-memory file
    #     reader = PdfReader(io.BytesIO(content))
    #     text_content = []
        
    #     for page in reader.pages:
    #         text_content.append(page.extract_text())
        
    #     return text_content
    
    def process_s3_documents(self, prefix=''):
        """
        Process all documents in the S3 bucket with the given prefix
        """
        try:
            documents = []
            file_keys = self.list_files(prefix)
            
            for s3_key in file_keys:
                print(f"Processing {s3_key}...")
                
                if s3_key.endswith('.pptx'):
                    content = self.extract_from_s3_pptx(s3_key)
                    documents.append({"filename": s3_key, "content": content, "type": "pptx"})
                elif s3_key.endswith('.pdf'):
                    content = self.extract_from_s3_pdf(s3_key)
                    documents.append({"filename": s3_key, "content": content, "type": "pdf"})
            
            return documents
        
        except Exception as e:
            print(f"Error processing documents in S3: {e}")