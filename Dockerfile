# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in specific order
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.2.3 \
    spacy==3.7.2 \
    plotly==5.18.0 \
    dash==2.14.0 \
    scikit-learn==1.3.0 \
    python-dotenv==1.0.0 \
    matplotlib==3.7.2 \
    seaborn==0.12.2 \
    nltk==3.8.1

# Download required NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the application
COPY . .

# Create necessary directories
RUN mkdir -p data output

# Set environment variables
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "src/main.py"] 