SELECT COUNT(*) AS total_trips 
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015` 
WHERE EXTRACT(YEAR FROM pickup_datetime) = 2015 
LIMIT 100;