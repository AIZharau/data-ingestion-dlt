{{
  config(
    schema='silver',
    order_by='tripid',
    engine='ReplacingMergeTree',
    materialized='incremental'
  )
}}


WITH tripdata AS 
(
  SELECT *,
    row_number() OVER (PARTITION BY vendorid, tpep_pickup_datetime) AS rn
  FROM {{ source('bronze', 'yellow_taxi') }}
  WHERE vendor_id IS NOT NULL
)
SELECT
    -- identifiers
    {{ dbt_utils.generate_surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} AS tripid,
    CAST(vendor_id AS Nullable(Int32)) AS vendorid,
    CAST(ratecode_id AS Nullable(Int32)) AS ratecodeid,
    CAST(pu_location_id AS Nullable(Int32)) AS pickup_locationid,
    CAST(do_location_id AS Nullable(Int32)) AS dropoff_locationid,
    
    -- timestamps
    parseDateTimeBestEffort(lpep_pickup_datetime) AS pickup_datetime,
    parseDateTimeBestEffort(lpep_dropoff_datetime) AS dropoff_datetime,
    
    -- travel info
    store_and_fwd_flag,
    CAST(passenger_count AS Nullable(Int32)) AS passenger_count,
    CAST(trip_distance AS Float64) AS trip_distance,
    -- yellow cabs are always street-hail
    1 AS trip_type,

    -- payment info
    CAST(fare_amount AS Float64) AS fare_amount,
    CAST(extra AS Float64) AS extra,
    CAST(mta_tax AS Float64) AS mta_tax,
    CAST(tip_amount AS Float64) AS tip_amount,
    CAST(tolls_amount AS Float64) AS tolls_amount,
    CAST(0 AS Float64) AS ehail_fee,
    CAST(improvement_surcharge AS Float64) AS improvement_surcharge,
    CAST(total_amount AS Float64) AS total_amount,
    coalesce({{ dbt.safe_cast("payment_type", api.Column.translate_type("integer")) }}, 0) AS payment_type,
    {{ get_payment_type_description("payment_type") }} AS payment_type_description
    custom_date
FROM tripdata
WHERE rn = 1
{% if is_incremental() %}
   and custom_date >= (select coalesce(max(custom_date), '1900-01-01') from {{ this }} )
{% endif %}