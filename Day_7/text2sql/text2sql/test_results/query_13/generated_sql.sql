SELECT 
  pickup_location_id, 
  COUNTIF(tip_amount > fare_amount * 0.2) / COUNT(*) AS tip_percentage
FROM 
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
GROUP BY 
  pickup_location_id
HAVING 
  COUNT(*) > 100
ORDER BY 
  tip_percentage DESC
LIMIT 
  10