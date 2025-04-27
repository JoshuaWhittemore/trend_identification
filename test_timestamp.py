import pandas as pd

# Test timestamp
test_timestamp = "2025-03-01 08:12:11+00:00"

print("Original timestamp:", test_timestamp)
print("Type:", type(test_timestamp))

# Try parsing with utc=True
parsed_timestamp = pd.to_datetime(test_timestamp, utc=True)
print("\nParsed timestamp:", parsed_timestamp)
print("Type:", type(parsed_timestamp))
print("Timezone:", parsed_timestamp.tzinfo)

# Create a small DataFrame to test
df = pd.DataFrame({
    'timestamp': [test_timestamp]
})

print("\nDataFrame before parsing:")
print(df)
print("Timestamp dtype:", df['timestamp'].dtype)

# Parse the timestamp in the DataFrame
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

print("\nDataFrame after parsing:")
print(df)
print("Timestamp dtype:", df['timestamp'].dtype) 