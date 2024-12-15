# Define the source and destination buckets
$sourceBucket = "gs://bk9999airline/dims"
$destinationBucket = "gs://bk9999airline/dims_table"

# List of dimension tables
$dimensions = @("dim_time", "dim_airport", "dim_airline", "dim_delay", "dim_cancel")

# Loop through each dimension
foreach ($dim in $dimensions) {
    # List the files in the dimension's folder
    $fileList = gsutil ls "$sourceBucket/$dim.parquet/" 2>&1

    # Check for the _SUCCESS file
    if ($fileList -match "_SUCCESS") {
        # Find the Parquet file
        $parquetFile = $fileList -split "`n" | Where-Object { $_ -match "part-.*\.parquet$" }
        
        if ($parquetFile) {
            # Copy the Parquet file to the destination with the correct name
            Write-Host "Copying $parquetFile to $destinationBucket/$dim.parquet"
            gsutil cp $parquetFile "$destinationBucket/$dim.parquet"
        } else {
            Write-Host "No Parquet file found for $dim in $sourceBucket/$dim.parquet/"
        }
    } else {
        Write-Host "No _SUCCESS file found for $dim in $sourceBucket/$dim.parquet/"
    }
}
