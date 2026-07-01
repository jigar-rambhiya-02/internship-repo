SELECT 
  EXTRACT(DAYOFWEEK FROM pickup_datetime) AS day_of_week,
  COUNT(*) AS total_trips,
  AVG(fare_amount) AS average_fare_amount
FROM 
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
WHERE 
  EXTRACT(YEAR FROM pickup_datetime) = 2015
GROUP BY 
  day_of_week
ORDER BY 
  day_of_week
LIMIT 
  100;