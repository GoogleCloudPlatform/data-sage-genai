# DataSageGen

## Introduction
DataSageGen is an innovative chatbot designed to be a personal guide, helping users access and process information from a vast array of sources. This application leverages cutting-edge AI technologies to provide insights from data and AI product documentation, blog posts, white papers, community knowledge, and product and event announcements.

## Features
- **Text Embeddings**: Utilizes Vertex AI Embeddings Model "textembedding-gecko@001" to convert text data into embeddings, enabling semantic search capabilities.
- **Generative AI**: Generates context-based responses to user inquiries.
- **Interactive Web Interface**: Provides a Google Cloud Platform user-friendly chat interface for real-time interaction.
- **Google Cloud Integration**: Leverages Google Cloud services for scalable storage, AI model management and application scalabity and security.

## Getting Started

### Prerequisites
- Python 3.9 or later
- Flask
- Google Cloud SDK
- Docker (for container-based deployment)
- Enable Google Cloud Storage, Cloud Run , Cloud Build, BigQuery and Vertex AI APIs - https://console.cloud.google.com/apis/enableflow?apiid=storage-component.googleapis.com,cloudbuild.googleapis.com,run.googleapis.com,bigquery.googleapis.com,aiplatform.googleapis.com&_ga=2.132962701.243207769.1688884437-279425947.1688884437
- Create Vertex AI Vector Search Index. Refer to the steps in notebook: create-vertexai-vector-index.ipynb under  create-vertexai-vector-index/ directory.

### The Installation
1. **Clone the repository**
   ```
   git clone https://github.com/GoogleCloudPlatform/data-sage-genai.git
   cd datasagegen
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

### Configuration
Set the required environment variables in the app.py file :

```bash
# Replace your PROJECT_ID value here
PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-gcp-project-id')
# Replace your GCP REGION LOCATION value here
LOCATION = os.getenv('GCP_LOCATION', 'your-gcp-location')
# Replace your  Google Cloud Storage Bucket Name   here, this is a bucket where the embeddings are stored
BUCKET_NAME = os.getenv('GCP_BUCKET_NAME', 'your-gcp-bucket-name')
# Replace the INDEX_ENDPOINT_NAME by the   Vector Search endpoint ID
INDEX_ENDPOINT_NAME = os.getenv('GCP_INDEX_ENDPOINT_NAME', 'your-index-endpoint-id')
```
Name the deployed index id : bqrelease_index or adapt the id in the app.py code

### Local Deployment
Run the application locally:
```
flask run --host=0.0.0.0 --port=8080
```
Visit `http://localhost:8080` in your web browser to interact with DataSageGen.

### Docker Deployment (Local)
Build and run the Docker container locally:
```
docker build -t datasagegen .
docker run -p 8080:8080 datasagegen
```
Access the application at `http://localhost:8080`.

### Google Cloud Run Deployment

Open a Google Cloud Shell 

Build the Docker image and push it to Google Container Registry:
```
gcloud builds submit --tag gcr.io/your-gcp-project-id/datasagegen
```
Deploy the image to Cloud Run:
```
gcloud run deploy datasagegen --image gcr.io/your-gcp-project-id/datasagegen --platform managed --region your-gcp-location  
```
This command will provide you with a URL where the service is deployed.


### Data Ingestion Component

The data ingestion component of the DataSageGen application is responsible for converting XML data to PDF documents, storing them in Google Cloud Storage, and potentially transforming them into useful data embeddings for further processing. This component utilizes technologies such as Flask, Google Cloud Storage, Vertex AI Search Index and WeasyPrint for PDF generation.
The data ingestion code are located under data-ingestion directory.

#### Features
- XML to PDF Conversion : Converts XML data from specified URLs into formatted PDFs.
- Cloud Storage Integration : Uploads the generated PDFs to Google Cloud Storage.
- Generate Embeddings out of the new PDF files.
- Update the Vertex AI Search Index with new embeddings for use in machine learning or other data-driven applications.

####  Deployment on Google Cloud Platform

Utilize the provided `cloudbuild.yaml` for deploying the application to Google Cloud Run. Ensure you have configured Cloud Build and Cloud Run in your GCP project.
```bash
gcloud builds submit --config cloudbuild.yaml
```
####  Usage , replace the Cloud-Run-URL with your cloud run URL

Trigger the PDF generation and upload process by sending a POST request to `/trigger-pdf`. This can be done using curl or any HTTP client:
```bash
curl -X POST https://<Cloud-Run-URL>/trigger-pdf
```

### Enabling IAP for Cloud Run
 Step by Step Follow the documentation - https://cloud.google.com/iap/docs/enabling-cloud-run
 Set up a HTTPS Application Load Balancer with Cloud Run - https://cloud.google.com/load-balancing/docs/https/setting-up-https-serverless 
 
## License
See the LICENSE  file for details.
