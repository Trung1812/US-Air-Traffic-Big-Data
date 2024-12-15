import os
import requests
import tarfile
from google.cloud import storage
from prefect import task, flow

# GCP and Dataproc details
project_id = 'totemic-program-442307-i9'
region = 'asia-southeast-1'
bucket_name = 'bk9999airline'
cluster_name = 'clean-data'

# Setup for GCS
storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name)

# 1. Task: Create Dataproc Cluster
@task
def create_dataproc_cluster():
    os.system(f"gcloud dataproc clusters create {cluster_name} "
              f"--region={region} "
              f"--zone={region}-a "
              f"--single-node "
              f"--image-version=2.0-debian10 "
              f"--master-machine-type=n1-standard-2 "
              f"--worker-machine-type=n1-standard-2 "
              f"--project={project_id} "
              f"--bucket={bucket_name}")

# 2. Task: Download File
@task
def download_file():
    fname = 'airline.tar.gz'
    url = 'https://dax-cdn.cdn.appdomain.cloud/dax-airline/1.0.1/' + fname
    r = requests.get(url)
    with open(fname, 'wb') as f:
        f.write(r.content)
    return fname

# 3. Task: Extract the Dataset (Directly to GCS)
@task
def extract_to_gcs(fname):
    tar = tarfile.open(fname)
    extracted_folder = 'airline'  # Folder where the data will be extracted
    os.makedirs(extracted_folder, exist_ok=True)
    tar.extractall(path=extracted_folder)  # Extract to local directory
    tar.close()

    # Upload to GCS
    for root, dirs, files in os.walk(extracted_folder):
        for file in files:
            blob = bucket.blob(f"{extracted_folder}/{file}")
            blob.upload_from_filename(os.path.join(root, file))
    return "Extraction and upload to GCS complete."

# 4. Task: Delete Dataproc Cluster
@task
def delete_dataproc_cluster():
    os.system(f"gcloud dataproc clusters delete {cluster_name} --region={region} --quiet")

# Define the Prefect flow
@flow
def flow_run():
    # Define the sequence of tasks
    create_cluster = create_dataproc_cluster()
    file_name = download_file()
    extract_and_upload = extract_to_gcs(file_name)
    delete_cluster = delete_dataproc_cluster()

    # Set task dependencies (sequence)
    create_cluster >> file_name >> extract_and_upload >> delete_cluster

# Run the flow
if __name__ == "__main__":
    flow_run()
