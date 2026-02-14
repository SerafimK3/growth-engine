-- models/marts/fct_conversions.sql
{{ config(materialized='table') }}

with events as (
    select * from {{ ref('stg_events') }}
),

user_journey as (
    select
        user_id,
        -- ADD THIS LINE HERE:
        count(*) as total_events, 
        
        max(case when event_name = 'user_signed_up' then 1 else 0 end) as has_signed_up,
        max(case when event_name = 'paywall_viewed' then 1 else 0 end) as has_viewed_paywall,
        max(case when event_name = 'subscription_started' then 1 else 0 end) as has_subscribed,
        sum(revenue_amount) as total_revenue,
        min(event_at) as first_touch_at,
        max(event_at) as last_touch_at
    from events
    group by 1
)

select 
    *,
    case 
        when has_subscribed = 1 then 'Paid Customer'
        when has_viewed_paywall = 1 then 'Lead (Paywall Hit)'
        else 'Free User'
    end as user_segment
from user_journey