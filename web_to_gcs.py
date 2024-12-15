import os
import tarfile
from google.cloud import storage

# GCP and Dataproc details
project_id = 'totemic-program-442307-i9'
bucket_name = 'bk9999airline'

# Setup for GCS
storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name)

def extract_to_gcs():
    fname = 'airline.tar.gz'  # The file in the GCS bucket
    extracted_file = 'airline.csv'  # The file to be saved in GCS

    # Download the file from GCS to local
    print(f"Downloading file {fname} from GCS...")
    blob = bucket.blob(fname)
    blob.download_to_filename(fname)
    print(f"File {fname} downloaded successfully.")

    if not os.path.exists(fname):
        print(f"File {fname} does not exist.")
        return

    print(f"Extracting {fname}...")
    # Extract the file and save to the desired file in GCS
    with tarfile.open(fname, 'r:gz') as tar:
        # Assuming there's only one file in the tar archive
        for member in tar.getmembers():
            if member.name.endswith('.csv'):  # Extract the .csv file
                print(f"Found CSV file: {member.name}")
                extracted_file_path = '/tmp/' + extracted_file  # Temporarily save to local
                tar.extract(member, path='/tmp/')  # Extract it to the temporary location

                # Upload the extracted CSV file to GCS
                print(f"Uploading {extracted_file_path} to GCS bucket as {extracted_file}...")
                blob = bucket.blob(extracted_file)
                blob.upload_from_filename(extracted_file_path)
                print(f"File {extracted_file} uploaded successfully to GCS.")

    # Clean up the local temp file after uploading
    os.remove(extracted_file_path)

if __name__ == "__main__":
    print("Starting the process...")
    extract_to_gcs()
    print("Process completed.")
