import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.cloud import storage, aiplatform
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingModel
from functools import lru_cache

# Configuration variables
PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'genai-demo-2024')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
BUCKET_NAME = os.getenv('GCP_BUCKET_NAME', 'gcp-newsletter-rag-vertex2')
INDEX_ENDPOINT_NAME = os.getenv('GCP_INDEX_ENDPOINT_NAME', '8619577425484840960')

app = Flask(__name__)
CORS(app)

# Initialize AI Platform and VertexAI once
aiplatform.init(project=PROJECT_ID, location=LOCATION)
vertexai.init()
model = GenerativeModel("gemini-pro")


def load_files_from_bucket(bucket_name):
    """Load JSON data from all files in a GCP bucket."""
    storage_client = storage.Client()
    data = []
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        if blob.name.endswith('.json'):
            json_string = blob.download_as_text()
            for line in json_string.splitlines():
                entry = json.loads(line)
                data.append(entry)
    return data


def generate_text_embeddings(sentences):
    """Generate text embeddings for given sentences."""
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    embeddings = model.get_embeddings([sentences])  # Assume a single sentence for simplicity
    vectors = [embedding.values for embedding in embeddings]
    return vectors


def generate_context(ids, data):
    """Generate context based on IDs."""
    concatenated_names = ''
    for id in ids:
        for entry in data:
            if entry['id'] == id:
                concatenated_names += entry['sentence'] + "\n"
    return concatenated_names.strip()

@lru_cache(maxsize=None)
def get_data_from_bucket():
    # Load the data from the bucket and return it
    # This function will only run once for a given set of arguments
    return load_files_from_bucket(BUCKET_NAME)

@app.route('/ask', methods=['POST'])
def ask():
    """Handle question asking and generate response."""
    question = request.json.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    data = get_data_from_bucket()
    qry_emb = generate_text_embeddings(question)

    bqrelease_index_ep = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=INDEX_ENDPOINT_NAME)
    response = bqrelease_index_ep.find_neighbors(
        deployed_index_id="bqrelease_index",
        queries=[qry_emb[0]],
        num_neighbors=10
    )

    matching_ids = [neighbor.id for sublist in response for neighbor in sublist]
    context = generate_context(matching_ids, data)

    prompt = f"Based on the context delimited in backticks, answer the query, ```{context}``` {question}"
    chat = model.start_chat(history=[])
    chat_response = chat.send_message(prompt)

    return jsonify({'response': chat_response.text})


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1'], host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))

# gcloud builds submit --tag gcr.io/genai-demo-2024/reggemini:last
# gcloud run deploy ragsagegenie-srv  --image gcr.io/genai-demo-2024/reggemini:last --platform managed --region us-central1 --allow-unauthenticated