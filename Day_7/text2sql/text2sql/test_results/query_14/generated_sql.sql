WITH hourly_fares AS (
  SELECT 
    EXTRACT(HOUR FROM pickup_datetime) AS hour_of_day,
    AVG(fare_amount) AS avg_fare
  FROM 
    `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
  GROUP BY 
    hour_of_day
),
ranked_fares AS (
  SELECT 
    hour_of_day,
    avg_fare,
    RANK() OVER (ORDER BY avg_fare DESC) AS rank_desc,
    RANK() OVER (ORDER BY avg_fare ASC) AS rank_asc
  FROM 
    hourly_fares
)
SELECT 
  hour_of_day,
  avg_fare,
  CASE 
    WHEN rank_desc <= 3 THEN 'top'
    WHEN rank_asc <= 3 THEN 'bottom'
    ELSE 'middle'
  END AS label
FROM 
  ranked_fares
ORDER BY 
  hour_of_day
LIMIT 
  24