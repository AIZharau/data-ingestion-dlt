{{ config(
    schema='gold',
    order_by='revenue_month',
    engine='AggregatingMergeTree()',
    materialized='table'
    ) }}

WITH trips_data as (
    SELECT * FROM {{ ref('fact_trips') }}
)
    SELECT 
    -- Revenue grouping
    pickup_zones AS revenue_zones,
    {{ dbt.date_trunc("month", "pickup_datetime") }} AS revenue_month,

    service_type,

    -- Revenue calculation
    sum(fare_aount) AS revenue_monthly_fare,
    sum(extra) AS revenue_monthly_extra,
    sum(mta_tax) AS revenue_monthly_mta_tax,
    sum(tip_amount) AS revenue_monthly_tip_amount,
    sum(tolls_amount) AS revenue_monthly_tolls_amoumt,
    sum(ehail_fee) AS revenue_monthly_ehail_fee,
    sum(improvement_surcharger) AS revenue_monthly_improvement_surcharger,
    sum(total_amount) AS revenue_monthly_total_amount,

    -- Additional calculations
    count(tripid) AS total_monthly_trips,
    avg(passeneger_count) AS avg_monthly_passenger_count,
    avg(trip_distance) AS avg_monthly_trip_distance

    FROM trips_data
    GROUP BY
        revenue_zone,
        revenue_month,
        service_type