from prefect import flow, task
from collect_data import collect_data
import os
import time

# Function to rename the files
def rename_files(extracted_dir, year, month):
    for file_name in os.listdir(extracted_dir):
        if file_name.startswith("On_Time_Reporting_Carrier_On_Time_Performance"):
            old_file_path = os.path.join(extracted_dir, file_name)
            new_file_path = os.path.join(extracted_dir, f"{year}_{month:02d}.csv")
            os.rename(old_file_path, new_file_path)
            print(f"Renamed file to: {new_file_path}")

# Define a Prefect Flow
@flow(name="Data Collection Flow")
def data_collection_flow():
    years = range(1987, 2025)  # From 1987 to 2024
    months = range(1, 13)  # From January to December

    # Loop through each year and month
    for year in years:
        for month in months:
            if year == 1987 and month < 10:  # Skip months before October 1987
                continue
            
            # Collect data
            collect_data(year, month)

            # Extract and rename the files after download
            extracted_dir = "./downloads/extracted"
            rename_files(extracted_dir, year, month)

            # Clean up: Remove the ZIP and unrelated extracted files
            for file_name in os.listdir(extracted_dir):
                file_path = os.path.join(extracted_dir, file_name)
                if not file_name.endswith('.csv'):
                    os.remove(file_path)
                    print(f"Removed extracted file: {file_path}")

            # Optional: Clean up the directory itself after processing
            if not any(file.endswith('.csv') for file in os.listdir(extracted_dir)):
                os.rmdir(extracted_dir)
                print(f"Removed empty extracted directory: {extracted_dir}")

# Run the flow
data_collection_flow()