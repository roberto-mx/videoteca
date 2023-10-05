# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /opt/videoteca

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the application will run on
EXPOSE 8086

# Start the Django application with a specific IP and port
CMD ["python", "manage.py", "runserver", "172.16.110.29:8086"]

