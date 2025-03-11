WITH quarterly_ AS (
SELECT 
  DISTINCT
  service_type,
  extract(year from pickup_datetime) as pickup_year,
  CASE
    WHEN extract(month from pickup_datetime) in (1,2,3) THEN 'Q1'
    WHEN extract(month from pickup_datetime) in (4,5,6) THEN 'Q2'
    WHEN extract(month from pickup_datetime) in (7,8,9) THEN 'Q3'
    WHEN extract(month from pickup_datetime) in (10,11,12) THEN 'Q4'
  END AS pickup_quarter,
  sum(total_amount) as quarterly_revenue
FROM {{ ref('fact_trips') }}
GROUP BY 1, 2, 3 ),

last_quarter AS (
SELECT 
  service_type,
  CONCAT(pickup_year,"-", pickup_quarter) as quarter, 
  quarterly_revenue, 
  concat(
  lag(pickup_year) OVER (partition by service_type,pickup_quarter order by pickup_year),'-',
  lag(pickup_quarter) OVER (partition by service_type,pickup_quarter order by pickup_year)) last_year,
  lag(quarterly_revenue) OVER (partition by service_type,pickup_quarter order by pickup_year) as last_year_quarterly_revenue
FROM quarterly_)

SELECT 
  *,
  safe_divide((quarterly_revenue-last_year_quarterly_revenue),last_year_quarterly_revenue) as revenue_yoy
FROM last_quarter
ORDER BY service_type, quarter