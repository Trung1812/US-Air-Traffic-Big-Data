terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.47.0"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}


# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}

resource "google_bigquery_dataset" "production_dataset" {
  dataset_id = "production"
  project    = var.project
  location   = var.region
}


resource "google_artifact_registry_repository" "bigdata-repo" {
  location      = var.region
  repository_id = "bigdata-repo"
  description   = "Prefect agents"
  format        = "DOCKER"
}


resource "google_compute_firewall" "port_rules" {
  project     = var.project
  name        = "kafka-broker-port"
  network     = var.network
  description = "Opens port 9092 in the Kafka VM for Spark cluster to connect"

  allow {
    protocol = "tcp"
    ports    = ["9092", "9093", "9094"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["kafka"]

}

resource "google_compute_instance" "kafka-instance" {
  boot_disk {
    auto_delete = true
    device_name = "kafka-instance"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-12-bookworm-v20241112"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  machine_type = "e2-medium"
  name         = "kafka-instance"

  network_interface {
    access_config {
      nat_ip       = "35.240.239.52"
      network_tier = "PREMIUM"
    }

    queue_count = 0
    stack_type  = "IPV4_ONLY"
    subnetwork  = "projects/totemic-program-442307-i9/regions/asia-southeast1/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = "bq-gcs-admin@totemic-program-442307-i9.iam.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  zone = "asia-southeast1-a"
}

resource "google_dataproc_cluster" "dataproc-cluster" {
  name   = "bigdata-cluster"
  region = var.region
  zone   = var.zone

  cluster_config {
    gce_cluster_config {
        network = var.network
        zone = var.zone

        shielded_instance_config {
            enable_secure_boot = true
        }
    }
    master_config {
      machine_type = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 100
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 100
      }
    }

    software_config {
      image_version = "2.2-debian12"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }

    initialization_action {
      executable_file = "gs://uk-airline-big-data/scripts/initialization_actions.sh"
    }

    endpoint_config {
      enable_component_gateway = true
    }
  }

  network_config {
    network = "default"
  }

  storage_config {
    bucket = "dataproc-staging-asia-southeast1-190992537547-yuriiara"
  }

  lifecycle {
    prevent_destroy = false
  }
}