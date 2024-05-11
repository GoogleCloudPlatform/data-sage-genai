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


   # Use an official Python runtime as a parent image
 FROM python:3.9-slim


   # Set the working directory in the container
 WORKDIR /usr/src/app


   # Copy the current directory contents into the container at /usr/src/app
 COPY . .


   # Install any needed packages specified in requirements.txt
 RUN pip install --no-cache-dir -r requirements.txt


   # Make port 8080 available to the world outside this container
 EXPOSE 8080


   # Run app.py when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
