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
