
# Notes

## Queries

```sql
SELECT status_id, user_id, status_text, created_at
FROM impeachment_production.partitioned_statuses
WHERE partition_val BETWEEN 0.7 and 0.8
LIMIT 10
```

```sql
SELECT
     cast(t.user_id as int64) as user_id
     ,min(t.user_created_at) as user_created_at
    ,count(distinct t.status_id) as tweet_count
    ,ARRAY_AGG(DISTINCT upper(t.user_screen_name)) as screen_names
    ,ARRAY_AGG(DISTINCT upper(t.user_name)) as user_names
    ,ARRAY_AGG(DISTINCT upper(t.user_description)) as user_descriptions
FROM impeachment_production.tweets t
GROUP BY 1
--ORDER BY 1
limit 10
```

## Migrations

```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v3;
CREATE TABLE impeachment_production.user_details_v3 as (
    SELECT
        user_id
        ,user_created_at
        ,tweet_count
        ,ARRAY_LENGTH(user_descriptions) as screen_name_count
        ,ARRAY_LENGTH(user_descriptions) as user_name_count
        ,ARRAY_LENGTH(user_descriptions) as user_description_count
        ,screen_names
        ,user_names
        ,user_descriptions
    FROM (
        SELECT
            cast(t.user_id as int64) as user_id
            ,min(t.user_created_at) as user_created_at
            ,count(distinct t.status_id) as tweet_count
            ,ARRAY_AGG(DISTINCT upper(t.user_screen_name) IGNORE NULLS) as screen_names
            ,ARRAY_AGG(DISTINCT upper(t.user_name) IGNORE NULLS) as user_names
            ,ARRAY_AGG(DISTINCT upper(t.user_description) IGNORE NULLS) as user_descriptions
        FROM impeachment_production.tweets t
        GROUP BY 1
        --ORDER BY 1
        -- limit 10
    )
)
```


```sql
select count(distinct user_id) as user_id_count
FROM impeachment_production.user_details_v3;
-- 3600545
```

```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v3;
CREATE TABLE impeachment_production.user_details_v3 as (
    SELECT
        user_id
        ,user_created_at
        ,tweet_count
        ,ARRAY_LENGTH(user_descriptions) as screen_name_count
        ,ARRAY_LENGTH(user_descriptions) as user_name_count
        ,ARRAY_LENGTH(user_descriptions) as user_description_count
        ,screen_names
        ,user_names
        ,user_descriptions
    FROM (
        SELECT
            cast(t.user_id as int64) as user_id
            ,min(t.user_created_at) as user_created_at
            ,count(distinct t.status_id) as tweet_count
            ,ARRAY_AGG(DISTINCT upper(t.user_screen_name) IGNORE NULLS) as screen_names_d
            ,ARRAY_AGG(DISTINCT upper(t.user_name) IGNORE NULLS) as user_names_d
            ,ARRAY_AGG(DISTINCT upper(t.user_description) IGNORE NULLS) as user_descriptions_d
            ,ARRAY_AGG(DISTINCT upper(t.user_screen_name) IGNORE NULLS) as screen_names_d
            ,ARRAY_AGG(DISTINCT upper(t.user_name) IGNORE NULLS) as user_names_d
            ,ARRAY_AGG(DISTINCT upper(t.user_description) IGNORE NULLS) as user_descriptions_d
        FROM impeachment_production.tweets t
        GROUP BY 1
        --ORDER BY 1
        -- limit 10
    )
)
```

## Seeding

```csv
community_id,hashtag,description
0, #LEFTTAG,
0, #LEFTTAG2,
1, #RIGHTTAG, It means this
1, #RIGHTTAG2
```
