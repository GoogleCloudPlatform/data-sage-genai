# Copyright 2024 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#  https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from google.cloud import storage
import PyPDF2
import re
import json
import uuid
from datetime import datetime
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from datetime import datetime
import os
import subprocess

# Initialize Variables
# Change your PROJECT_ID value here
project = "genai-demo-2024"
# Change your GCP REGION LOCATION value here
location = "us-central1"
# Change your  Google Cloud Storage Bucket Name  that will store the embeddings
bucket_name = "gcp-newsletter-rag-vertex2"
# Change your  Google Cloud Storage Bucket Name   that store the source PDF files
source_bucket_name = "knowedge-rag"


def extract_sentences_from_pdf_bytes(pdf_bytes):
    reader = PyPDF2.PdfReader(pdf_bytes)
    text = ""
    for page in reader.pages:
        if page.extract_text() is not None:
            text += page.extract_text() + " "
    sentences = [sentence.strip() for sentence in text.split('. ') if sentence.strip()]
    return sentences


def clean_text(text):
    cleaned_text = re.sub(r'\u2022', '', text)  # remove bullet points
    cleaned_text = re.sub(r'#', '', cleaned_text)  # remove hash symbols
    cleaned_text = re.sub(r':', '', cleaned_text)  # remove colons
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # remove extra whitespaces and strip
    return cleaned_text


def generate_text_embeddings(sentences):
    aiplatform.init(project=project, location=location)
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    embeddings = model.get_embeddings(sentences)
    vectors = [embedding.values for embedding in embeddings]
    return vectors


def upload_file(bucket_name, file_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(file_path))
    blob.upload_from_filename(file_path)
    print(f"File {file_path} uploaded to {bucket_name}.")


def process_pdf_files_from_bucket(source_bucket_name, target_bucket_name):
    storage_client = storage.Client()
    today_str = datetime.now().strftime('%Y%m%d')
    prefix = ""  # Use this if your PDFs are stored under a specific prefix in the bucket
    blobs = storage_client.list_blobs(bucket_or_name=source_bucket_name, prefix=prefix)

    for blob in blobs:
        # Construct the pattern to match files of the format xxxx_YYYYMMDD.pdf
        pattern = f".*_{today_str}.pdf$"
        if re.match(pattern, blob.name):
            print(f"Processing: {blob.name}")
            blob.download_to_filename(blob.name)

            with open(blob.name, 'rb') as pdf_file:
                sentences = extract_sentences_from_pdf_bytes(pdf_file)

            if sentences:
                embeddings = generate_text_embeddings(sentences)
                embed_file_path = blob.name.replace('.pdf', '_embeddings.json')

                with open(embed_file_path, 'w') as embed_file:
                    for sentence, embedding in zip(sentences, embeddings):
                        cleaned_sentence = clean_text(sentence)
                        id = str(uuid.uuid4())
                        embed_item = {"id": id, "sentence": cleaned_sentence, "embedding": embedding}
                        json.dump(embed_item, embed_file)
                        embed_file.write('\n')

                upload_file(target_bucket_name, embed_file_path)
                os.remove(blob.name)  # Clean up downloaded PDF
                os.remove(embed_file_path)  # Clean up generated embeddings file


def run_gcloud_command():
    # replace the 7982036603235205120 with your Vector search index ID
    # In index_metadata.json file replace the gs://gcp-newsletter-rag-vertex2 to your  Google Cloud Storage Bucket Name  that will store the embeddings
    # replace genai-demo-2024 value with your google project ID
    # replace the  us-central1 with your preferred GCP region value
    command = [
        "gcloud", "ai", "indexes", "update",
        "7982036603235205120",
        "--display-name", "bqrelease_index",
        "--metadata-file", "index_metadata.json",
        "--project", "genai-demo-2024",
        "--region", "us-central1"
    ]

    try:
        subprocess.run(command, check=True)
        print("gcloud command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing gcloud command: {e}")


# Call the function to process PDF files
process_pdf_files_from_bucket(source_bucket_name, bucket_name)
# Call this function after process_pdf_files_from_bucket in your main logic
# process_pdf_files_from_bucket(source_bucket_name, bucket_name)
run_gcloud_command()
