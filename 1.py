import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('products.csv')

# Remove duplicate rows
df_cleaned = df.drop_duplicates()

# Save the cleaned data to a new CSV file
df_cleaned.to_csv('cleaned_file.csv', index=False)