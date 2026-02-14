{{ config(materialized='table') }}

with source as (
    select * from {{ source('posthog', 'events') }}
),

cleaned as (
    select
        -- IDs
        uuid as event_id,
        distinct_id as user_id,
        event as event_name,

        -- Timestamps
        timestamp as event_at,
        
        -- The JSON Extraction (The "Senior Engineer" part)
        -- We extract the specific properties you need for the dashboard
        properties->>'plan' as plan_type,
        properties->>'trigger' as paywall_trigger,
        
        -- Safe Cast to Number for Revenue
        cast(nullif(properties->>'value', '') as numeric) as revenue_amount

    from source
    -- Filter out system noise
    where event not in ('$feature_flag_called', '$groupidentify')
)

select * from cleaned