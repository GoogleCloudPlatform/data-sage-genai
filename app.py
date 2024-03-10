import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.cloud import storage
import PyPDF2
import numpy as np
import faiss
from google.cloud import aiplatform
import os
# Assuming these imports are correct based on your provided context
# You may need to adjust based on the actual library/package for Gemini Pro
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import (
   GenerationConfig,
   GenerationResponse,
   GenerativeModel,
   Image,
   Part,
)


app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize AI Platform with your project and location
aiplatform.init(project='genai-demo-2024', location='us-central1')


# Model identifiers (ensure these are correctly specified)
embedding_model_name = "textembedding-gecko@001"
# For the GenerativeModel, ensure you're using the correct identifier or mechanism to access it
summarization_model = GenerativeModel("gemini-1.0-pro")


bucket_name = 'knowedge-rag'


# Embedding dimension and FAISS index initialization
dimension = 768
faiss_index = faiss.IndexFlatL2(dimension)
document_summary_map = {}
document_id_counter = 0


def extract_text_from_pdf(blob):
   with io.BytesIO(blob.download_as_bytes()) as pdf_file:
       reader = PyPDF2.PdfReader(pdf_file)
       text = ""
       for page in reader.pages:
           content = page.extract_text()
           if content:
               text += content
   return text


def generate_summary(text):
   try:
       model = GenerativeModel("gemini-1.0-pro")
       generation_config = GenerationConfig(
           temperature=0.1,
           top_p=0.8,
           top_k=40,
           candidate_count=1,
           max_output_tokens=2048,
       )
       responses = model.generate_content(text,   generation_config=generation_config, stream=True,)
       generated_content = "".join([response.text for response in responses])
       return generated_content
   except Exception as e:
       print(f"Error generating summary: {e}")
       # Optionally, log the error or handle it more gracefully
       return "Summary generation failed."


def embed_text(text):
   # Placeholder for embedding; adjust based on actual usage
   embeddings = np.random.rand(dimension)  # Example: replace with real embeddings
   return embeddings


@app.route('/process_pdfs', methods=['POST'])
def process_pdfs():
   global document_id_counter
   storage_client = storage.Client()
   bucket = storage_client.bucket(bucket_name)
   blobs = bucket.list_blobs()


   for blob in blobs:
       if blob.name.endswith('.pdf'):
           text = extract_text_from_pdf(blob)
           summary = generate_summary(text)
           embeddings = embed_text(summary)
           faiss_index.add(np.array([embeddings]).astype(np.float32))
           document_summary_map[document_id_counter] = summary
           document_id_counter += 1


   return jsonify({'status': 'Processed and indexed PDF summaries'})


@app.route('/ask', methods=['POST'])
def ask():
   question = request.json.get('question', '')
   if not question:
       return jsonify({'error': 'No question provided'}), 400


   question_embedding = embed_text(question)
   _, closest_indices = faiss_index.search(np.array([question_embedding]).astype(np.float32), k=1)
   closest_ids = closest_indices.flatten().tolist()
   closest_summaries = [document_summary_map.get(doc_id, "Summary not found") for doc_id in closest_ids]
   return jsonify({'closest_summaries': closest_summaries})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))





