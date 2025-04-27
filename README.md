# Treehut Social Media Trend Analysis

This project analyzes social media trends and topics of interest for Treehut's Instagram presence, focusing on comment analysis and trend identification.

## Project Structure

```
.
├── data/               # Raw data directory
├── output/            # Processed data and results
├── src/               # Source code
│   ├── data_processing/  # Data cleaning and preprocessing
│   ├── analysis/        # Trend analysis and topic modeling
│   └── visualization/   # Dashboard and visualization code
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd treehut-trend-analysis
```

2. Create necessary directories:

```bash
mkdir -p data output
```

3. Place your raw data file in the `data` directory:

```bash
cp path/to/your/raw_data.csv data/
```

4. Build and run with Docker:

```bash
# Build the container
docker-compose build

# Run the analysis
docker-compose run --rm -it app python -u src/main.py --data data/raw_data.csv --output output

# Start the visualization dashboard
docker-compose up
```

## Usage

1. **Data Analysis**:

   - Place your raw data file in the `data` directory
   - Run the analysis pipeline
   - Results will be saved to the `output` directory

2. **Visualization Dashboard**:
   - Access the dashboard at http://localhost:8050
   - View comment volume over time
   - Analyze comment length distribution
   - See activity patterns by day and hour

## Features

- Time-based trend analysis
- Comment length analysis
- Activity pattern analysis
- Interactive visualization dashboard

## Dependencies

- Python 3.11
- pandas
- numpy
- spacy
- plotly
- dash
- scikit-learn
- nltk

## Docker

The project uses Docker to ensure consistent environments. The Dockerfile and docker-compose.yml files are included for easy setup.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
