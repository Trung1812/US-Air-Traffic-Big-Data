from prefect import task, flow
import requests
import tarfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage

# Prefect task to upload a file to GCS
@task
def upload_to_gcs(bucket_name, blob_name, file_data):
    """Upload a file to a Google Cloud Storage bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file_data)
    print(f"Uploaded {blob_name} to bucket {bucket_name}")

# Prefect task to download the tarball
@task
def download_tarball(url):
    """Download tarball from the given URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    print("Tarball downloaded successfully.")
    return BytesIO(response.raw.read())

# Prefect task to extract files from the tarball
@task
def extract_and_upload_tar(tarball_data, bucket_name):
    """Extract tarball files and upload them to GCS."""
    with tarfile.open(fileobj=tarball_data, mode='r:gz') as tar:
        with ThreadPoolExecutor() as executor:
            for member in tar.getmembers():
                if member.isfile():
                    file_data = tar.extractfile(member)  # Get file data as a stream
                    blob_name = member.name  # Use the member name for GCS path
                    executor.submit(upload_to_gcs, bucket_name, blob_name, file_data)

# Define the Prefect 2.0+ flow
@flow(name="Airline Tarball Pipeline")
def airline_pipeline():
    bucket_name = 'bk9999airline'  # Replace with your GCS bucket name
    file_url = 'https://dax-cdn.cdn.appdomain.cloud/dax-airline/1.0.1/airline_2m.tar.gz'

    # Define task execution
    tarball_data = download_tarball(file_url)
    extract_and_upload_tar(tarball_data, bucket_name)

# Run the flow
if __name__ == "__main__":
    airline_pipeline()
