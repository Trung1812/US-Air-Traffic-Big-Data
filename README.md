# Big Data Project - US Air Traffic Data Analysis

![](docs/airplane.jpeg)


## 1. Introduction
As one of the largest and busiest airspaces in the world, the United States experiences a massive volume of air traffic, with thousands of flights taking off and landing each day across the country. This constant flow of air travel generates an immense amount of data, ranging from flight schedules and delays to passenger numbers and aircraft performance. In fact, the volume of data is so vast that it spans millions of records annually, creating a rich dataset for analysis.

The objective of this project is to build an automated data pipeline that collects, transforms, and visualizes US air traffic data for analytical purposes. Prefect is used to orchestrate the pipeline, which pulls real-time data from external APIs, such as aviationstack, and uploads it to Google Cloud Storage (GCS) and Google BigQuery. In BigQuery, the data undergoes cleaning and transformation using Spark, creating a refined dataset for further analysis. Finally, the results are presented through dynamic dashboards built with Looker Studio, enabling users to gain insights into air traffic patterns, delays, and trends. Additionally, the team simulates real-time data in a streaming format using Kafka to process and analyze incoming flight information in near real-time.

## 2. Dataset

- Data is collected from [US Bureau of Transportation Website](https://www.transtats.bts.gov/) and from [Aviation Stack API](https://aviationstack.com). In this project, we analyze US air traffic data from 1987 to 2020 and realtime data from API calls.
- Dataset size: over 80GB with approximate 200 million records.
- These are some of the fields in the dataset:


| Field | Description |
| --- | --- |
| Year | Year of the flight. Helps in identifying long-term trends or seasonal patterns. |
| Quater | Quarter of the year (1 to 4). Useful for analyzing seasonal variations. |
| Month | Month & Month of the flight. Allows for monthly breakdown of data. |
| DayofMonth | Day of the month when the flight occurred. Useful for precise date-specific analysis. |
| DayOfWeek | Day of the week (1 for Monday, 7 for Sunday). Important for identifying weekly trends. |
| FlightDate | Exact date of the flight. A critical field for time-series analysis. |
| Reporting Airline | Unique carrier code for the reporting airline. Helps distinguish between airlines. |
| Tail Number | Unique aircraft tail number. Useful for tracking performance by aircraft. |
| Flight Number | Reporting Flight number reported by the airline. Enables tracking individual flights. |
| OriginAirportID | Unique ID of the origin airport. Essential for identifying departure locations. |
| OriginCityName | City name of the origin airport. Useful for grouping and summarizing data by city. |
| DestAirportID | Unique ID of the destination airport. Important for analyzing arrival locations. |
| DestCityName | City name of the destination airport. Enables grouping data by destination city. |
| ArrDelay | Arrival delay in minutes. A critical performance metric. |

## 3. Technology and System Architecture

- Docker: Package code and necessary libraries to run the pipeline.
- Prefect: Schedule and manage workflows.
- Google Cloud Platform (GCP):
   - Google Cloud Storage (GCS): Data lake containing raw data.
   - Google BigQuery: Data warehouse containing cleaned and transformed data.
   - Looker Studio: Data visualization.
   - Cloud Run: Run the pipeline automatically.
- dbt: Clean, transform, and prepare data for analysis.
- Spark: Similar to dbt.
- Terraform: Deploy the system to GCP.

![](docs/architecture.png)


## 4. Implementation Details

 - For implementation details, please check out [docs](./reproduce.md)

## 5. Results

- [Link to dashboard](https://lookerstudio.google.com/reporting/b43aba67-94ae-482a-8801-44c0b2340140)

![](docs/overview.png)
