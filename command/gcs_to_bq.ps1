# Define the source and destination buckets
$sourceBucket = "gs://bk9999airline"
$destinationBucket = "gs://bk9999airline/dims_table"

# List of dimension tables
$dimensions = @("dim-time", "dim-airport", "dim-airline", "dim-delay", "dim-cancel")
$facts = @("fact-table")


# Loop through each dimension
foreach ($dim in $dimensions) {
    # List the files in the dimension's folder
    $fileList = gsutil ls "$sourceBucket/dims/$dim.parquet/" 2>&1

    # Check for the _SUCCESS file
    if ($fileList -match "_SUCCESS") {
        # Find the Parquet file
        $parquetFile = $fileList -split "`n" | Where-Object { $_ -match "part-.*\.parquet$" }
        
        if ($parquetFile) {
            # Copy the Parquet file to the destination with the correct name
            Write-Host "Copying $parquetFile to $destinationBucket/$dim.parquet"
            gsutil cp $parquetFile "$destinationBucket/$dim.parquet"

            # Load the Parquet file into BigQuery
            Write-Host "Loading $parquetFile into BigQuery table flightdata.$dim"
            bq load --source_format=PARQUET --autodetect flightdata.$dim $destinationBucket/$dim.parquet
        } else {
            Write-Host "No Parquet file found for $dim in $sourceBucket/$dim.parquet/"
        }
    } else {
        Write-Host "No _SUCCESS file found for $dim in $sourceBucket/$dim.parquet/"
    }
}



$destinationBucket = "gs://bk9999airline/facts_table"

foreach ($fact in $facts) {
    # List the files in the dimension's folder
    $fileList = gsutil ls "$sourceBucket/fact/$fact.parquet/" 2>&1

    # Check for the _SUCCESS file
    if ($fileList -match "_SUCCESS") {
        # Find the Parquet file
        $parquetFile = $fileList -split "`n" | Where-Object { $_ -match "part-.*\.parquet$" }
        
        if ($parquetFile) {
            # Copy the Parquet file to the destination with the correct name
            Write-Host "Copying $parquetFile to $destinationBucket/$fact.parquet"
            gsutil cp $parquetFile "$destinationBucket/$fact.parquet"

            # Load the Parquet file into BigQuery
            Write-Host "Loading $parquetFile into BigQuery table flightdata.$fact"
            bq load --source_format=PARQUET --autodetect flightdata.$fact $destinationBucket/$fact.parquet
        } else {
            Write-Host "No Parquet file found for $fact in $sourceBucket/$fact.parquet/"
        }
    } else {
        Write-Host "No _SUCCESS file found for $fact in $sourceBucket/$fact.parquet/"
    }
}
