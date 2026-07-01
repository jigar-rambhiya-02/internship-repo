SELECT 
  date,
  SUM(daily_fare) OVER (ORDER BY date) AS cumulative_total_fare,
  (SUM(daily_fare) OVER (ORDER BY date) / SUM(daily_fare) OVER ()) * 100 AS percentage_of_month_total
FROM 
  (
    SELECT 
      DATE(pickup_datetime) AS date,
      SUM(fare_amount) AS daily_fare
    FROM 
      `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
    WHERE 
      EXTRACT(MONTH FROM pickup_datetime) = 1 AND EXTRACT(YEAR FROM pickup_datetime) = 2015
    GROUP BY 
      DATE(pickup_datetime)
  )
ORDER BY 
  date
LIMIT 
  100