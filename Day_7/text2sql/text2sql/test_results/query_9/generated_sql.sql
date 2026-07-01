SELECT 
  dropoff_location_id, 
  AVG(tip_amount / fare_amount * 100) AS avg_tip_percentage
FROM 
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
WHERE 
  fare_amount > 5
GROUP BY 
  dropoff_location_id
ORDER BY 
  avg_tip_percentage DESC
LIMIT 
  10