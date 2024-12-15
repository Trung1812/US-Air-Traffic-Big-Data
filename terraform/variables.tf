locals {
  data_lake_bucket = "dtc_data_lake"
}

variable "project_id" {
  default     = "totemic-program-442307-i9"
  description = "The project ID to host the cluster in"
}

variable "project" {
  description = "My First Project"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "asia-east2"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "flightdata"
}

variable "credentials" {
  description = "Path to your GCP credentials file. If not set, then set env-var GOOGLE_APPLICATION_CREDENTIALS"
  type = string
  default = "your-credentials-key.json"
}

variable "cluster_name" {
  description = "The name for the GKE cluster"
  default     = "flight-cleaning-cluster"
}

variable "env_name" {
  description = "The environment for the GKE cluster"
  default     = "prod"
}

variable "network" {
  description = "Network for your instance/cluster"
  default     = "default"
  type        = string
}

variable "vm_image" {
  description = "Image for you VM"
  default     = "ubuntu-os-cloud/ubuntu-2004-lts"
  type        = string
}