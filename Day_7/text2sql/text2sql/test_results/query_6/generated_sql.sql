SELECT pickup_location_id, SUM(fare_amount) AS total_fare_amount
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
WHERE EXTRACT(MONTH FROM pickup_datetime) = 1 AND EXTRACT(YEAR FROM pickup_datetime) = 2015
GROUP BY pickup_location_id
ORDER BY total_fare_amount DESC
LIMIT 5