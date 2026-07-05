SELECT 
  DATE(pickup_datetime) AS date,
  RANK() OVER (ORDER BY COUNT(*) DESC) AS rank
FROM 
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
GROUP BY 
  DATE(pickup_datetime)
ORDER BY 
  rank
LIMIT 
  100;