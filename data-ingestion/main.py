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

import lxml.etree as ET
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import requests
from google.cloud import storage
import logging
import os
from datetime import datetime
from flask import Flask, render_template


app = Flask(__name__)


def xml_to_pdf_and_upload(xml_url, template_file, gcs_bucket_name, gcs_filename):
    # Fetch XML data from URL
    response = requests.get(xml_url)
    response.raise_for_status()

    # Parse XML (handling namespaces)
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
    tree = ET.fromstring(response.content)
    root = tree

    # Prepare data for the template (with debugging)
    data = {
        'entries': []
    }
    for entry in root.findall('atom:entry', namespaces=namespaces):
        data['entries'].append({
            'title': entry.find('atom:title', namespaces=namespaces).text,
            'updated': entry.find('atom:updated', namespaces=namespaces).text,
            'content': entry.find('atom:content', namespaces=namespaces).text
        })
    print("DEBUG: Data prepared for template:", data)  # Debugging output

    # Template Setup
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template(template_file)

    # Render HTML output
    html_content = template.render(data)

    # Generate PDF (with optional WeasyPrint debugging)
    logging.basicConfig(level=logging.DEBUG)  # Enable WeasyPrint logging
    HTML(string=html_content).write_pdf('temp_output.pdf')

    # Upload PDF to Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_filename)
    blob.upload_from_filename('temp_output.pdf')

@app.route('/trigger-pdf', methods=['POST'])
def generate_pdf_and_upload():
    template_file = 'xml_template.html'  # Make sure this exists under templates/ directory!
    gcs_bucket_name = 'knowedge-rag'  # Replace with your bucket name, this is the bucket name that will store the source PDF files.
    # Get today's date and format
    today_str = datetime.now().strftime('%Y%m%d')
    with open('feed_urls.txt', 'r') as file:
        try:
            for line in file:
                product_name, xml_url = line.strip().split()
                gcs_filename = f'{product_name}_release_notes_{today_str}.pdf'
                xml_to_pdf_and_upload(xml_url, template_file, gcs_bucket_name, gcs_filename)
        except FileNotFoundError:
            print("Error: 'feed_urls.txt' file not found.")  # Handle the error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  # Catch other potential errors
    return 'PDF Generation Complete', 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

