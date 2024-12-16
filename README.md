# Big Data Project - US Air Traffic Data Analysis

![](docs/yellow-cab.png)


## 1. Introduction




## 2. Dataset

- Data is collected from [website-quản-lý-của-thành-phố](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page 
). Ở trong project này, dữ liệu được phân tích là dữ liệu từ 01/2019 - 07/2021 của các loại taxi: yellow taxi, green taxi, for-hire vehicles (FHV), for-hire vehicles high volume (FHVHV). 
- Kích thước dữ liệu: hơn 80GB với hơn 100 triệu bản ghi.
- Dưới đây là một số trường trong bộ dữ liệu


| Field | Description |
| --- | --- |
| Year | Year of the flight. Helps in identifying long-term trends or seasonal
patterns. |
| Quater | Quarter of the year (1 to 4). Useful for analyzing seasonal varia-
tions. |
| Month | Month & Month of the flight. Allows for monthly breakdown of data. |
| DayofMonth | Day of the month when the flight occurred. Useful for precise
date-specific analysis. |
| DayOfWeek | Day of the week (1 for Monday, 7 for Sunday). Important for identifying weekly trends. |
|  |  |
| FlightDate | Exact date of the flight. A critical field for time-series analysis. |
| Reporting Airline | Unique carrier code for the reporting airline. Helps distinguish
between airlines. |
| Tail Number | Unique aircraft tail number. Useful for tracking performance by
aircraft. |
| Flight Number | Reporting Flight number reported by the airline. Enables tracking individual flights. |
| OriginAirportID | Unique ID of the origin airport. Essential for identifying departure
locations. |
| OriginCityName | City name of the origin airport. Useful for grouping and summa-
rizing data by city. |
| DestAirportID | Unique ID of the destination airport. Important for analyzing
arrival locations. |
| DestCityName City name of the destination airport. Enables grouping data by
destination city. |
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


## 4. Các bước thực hiện

 - For implementation details, please check out [docs](./reproduce.md)

## 5. Kết quả

- [Link to dashboard](https://lookerstudio.google.com/reporting/7f728ad5-637e-4796-b240-aa1b7c6b77ce)

![](docs/overview.png)