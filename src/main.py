import argparse
from data_processing.processor import DataProcessor
from analysis.trend_analyzer import TrendAnalyzer
from analysis.keyword_analyzer import KeywordAnalyzer
import os
import json

def main():
    print("\n" + "="*50)
    print("STARTING MAIN METHOD")
    print("="*50 + "\n")
    
    parser = argparse.ArgumentParser(description="Treehut Social Media Trend Analysis")
    parser.add_argument("--data", type=str, required=True, help="Path to the input data file")
    parser.add_argument("--output", type=str, default="output", help="Output directory for results")
    args = parser.parse_args()

    print(f"Arguments parsed: data={args.data}, output={args.output}")

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    print(f"Output directory created/verified: {args.output}")

    # Initialize processors
    print("Initializing processors...")
    data_processor = DataProcessor()
    trend_analyzer = TrendAnalyzer()
    keyword_analyzer = KeywordAnalyzer()
    print("Processors initialized successfully")

    # Load and process data
    print("\nLoading and processing data...")
    print(f"Attempting to load data from: {args.data}")
    df = data_processor.load_data(args.data)
    print(f"Data loaded successfully. Shape: {df.shape}")
    
    print("\nProcessing data...")
    processed_df = data_processor.process_data(df)
    print("Data processing completed")

    # Perform topic modeling
    print("\nPerforming topic modeling...")
    topics, processed_df = trend_analyzer.perform_topic_modeling(processed_df)
    print("Topic modeling completed")

    # Perform keyword analysis
    print("\nPerforming keyword analysis...")
    keyword_analysis = keyword_analyzer.analyze_keywords_in_corpus(processed_df)
    print("Keyword analysis completed")

    # Save processed data
    print("\nSaving processed data...")
    processed_df.to_csv(os.path.join(args.output, "processed_data.csv"), index=False)
    print("Processed data saved")

    # Save topic information
    print("\nSaving topic information...")
    with open(os.path.join(args.output, "topics.json"), "w") as f:
        json.dump(topics, f, indent=2)
    print("Topic information saved")

    # Save keyword analysis
    print("\nSaving keyword analysis...")
    keyword_analysis.to_csv(os.path.join(args.output, "keyword_analysis.csv"), index=False)
    print("Keyword analysis saved")

    print(f"\nAnalysis complete. Results saved to {args.output}")
    print("To view the visualization dashboard, run: docker-compose up")

if __name__ == "__main__":
    main() 