# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

<<<<<<< HEAD
# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]

=======
# Use Gunicorn for production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
>>>>>>> 98b6c7ebc80bea99b7d9631de34cd2b2b7bab5c1
