'''
This module contains the S3DocumentProcessor class which is responsible for uploading files to S3, listing files in S3.
'''

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
    