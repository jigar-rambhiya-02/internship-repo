SELECT 
  EXTRACT(MONTH FROM pickup_datetime) AS month_number,
  COUNT(*) AS trip_count
FROM 
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
GROUP BY 
  EXTRACT(MONTH FROM pickup_datetime)
ORDER BY 
  month_number
LIMIT 
  100