SELECT passenger_count, AVG(trip_distance) AS average_distance 
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015` 
GROUP BY passenger_count 
ORDER BY passenger_count 
LIMIT 100