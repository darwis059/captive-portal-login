# Use a lightweight Python image
FROM python:3.11-alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the automation script
COPY autologin.py .

# Run Python in unbuffered mode so logs print immediately in Docker
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python", "autologin.py"]