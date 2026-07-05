SELECT 
  date,
  AVG(trip_count) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_average
FROM 
  (SELECT 
     DATE(pickup_datetime) AS date,
     COUNT(*) AS trip_count
   FROM 
     `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
   WHERE 
     EXTRACT(MONTH FROM pickup_datetime) = 3
   GROUP BY 
     DATE(pickup_datetime)
  ) 
LIMIT 100