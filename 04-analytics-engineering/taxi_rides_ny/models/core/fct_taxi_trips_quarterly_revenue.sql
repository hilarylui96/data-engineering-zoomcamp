WITH quarterly_ AS (
SELECT 
  DISTINCT
  service_type,
  extract(year from pickup_datetime) as year,
  extract(quarter from pickup_datetime) as quarter,
  sum(total_amount) as quarterly_revenue
FROM {{ ref('fact_trips') }}
WHERE extract(year from pickup_datetime) in (2019,2020)
GROUP BY 1, 2, 3 ),

last_quarter AS (
SELECT 
  service_type,
  year,
  quarter,
  quarterly_revenue,
  lag(year) OVER (partition by service_type,quarter order by year) as last_year,
  lag(quarter) OVER (partition by service_type,quarter order by year) last_quarter,
  lag(quarterly_revenue) OVER (partition by service_type,quarter order by year) as last_year_quarterly_revenue
FROM quarterly_)

SELECT 
  *,
  safe_divide((quarterly_revenue-last_year_quarterly_revenue),last_year_quarterly_revenue) as yoy_growth
FROM last_quarter
ORDER BY service_type, year, quarter