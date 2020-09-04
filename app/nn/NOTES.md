
# Notes

## Summary

For each user, we examined their profiles to see if any of the community tags appear in their user names or descriptions. Of the original 3.6M users, 138,001 had community tag matches. Of the 138,001 users, 541 (0.4%) had tags from more than one community, and were excluded. The distribution of the remaining 137,460 users is below:

community_id	| user_count	| community_score
---             | ---           | ---
0	            | 59792	        | 90645
1	            | 77668	        | 166383

For training the model, we will pick a random sample of equal size from each of these groups.




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
            ,STRING_AGG(DISTINCT upper(t.user_screen_name) IGNORE NULLS) as screen_names
            ,STRING_AGG(DISTINCT upper(t.user_name) IGNORE NULLS) as user_names
            ,STRING_AGG(DISTINCT upper(t.user_description) IGNORE NULLS) as user_descriptions
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
        cast(t.user_id as int64) as user_id
        ,min(t.user_created_at) as user_created_at
        ,count(distinct t.status_id) as tweet_count
        ,count(distinct t.user_screen_name) as screen_name_count
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_screen_name), ' | ') , "")   as screen_names
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_name), ' | ')        , "")   as user_names
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_description), ' | ') , "")   as user_descriptions
    FROM impeachment_production.tweets t
    GROUP BY 1

)
```

## Seeding

Add mutually exclusive hashtags used by members of each community.

```csv
community_id,hashtag,description
0, #LEFTTAG,
0, #LEFTTAG2,
1, #RIGHTTAG, It means this
1, #RIGHTTAG2
```

Upload the CSV to BigQuery as the "2_community_tags" table, where "2" is the number of communities you're using.

## Queries and Migrations (Exploration)

Labeling tweets...

```sql

-- select split('HI #VOTEBLUE2020', ' ')

select hashtag, description, community_id, t.status_text
from impeachment_production.2_community_tags as tags
--JOIN impeachment_production.tweets t ON tags.hashtag in unnest(split(t.status_text, ' '))
JOIN impeachment_production.tweets t ON '#VOTEBLUE' in unnest(split(t.status_text, ' '))
-- where t.status_text LIKE '%#VOTEBLUE2020%'
order by 1
limit 10
```

```sql
select
  hashtag
  --, description
  , community_id
  ,t.status_id
  , t.user_id
  , t.status_text
from impeachment_production.2_community_tags as tags
JOIN impeachment_production.tweets t ON tags.hashtag in unnest(split(t.status_text, ' '))
-- JOIN impeachment_production.tweets t ON '#VOTEBLUE' in unnest(split(t.status_text, ' '))
order by 1
limit 10
```

```sql
-- user community labels
SELECT
   u.user_id
   --,u.user_created_at as created_at
   --,u.tweet_count
   ,u.screen_names
  ,u.user_descriptions as descriptions
  ,tg.hashtag
  ,tg.community_id
FROM impeachment_production.user_details_v3 u
JOIN impeachment_production.2_community_tags tg ON tg.hashtag in unnest(split(u.user_descriptions, ' '))
-- WHERE 'VOTEBLUE2020' in unnest(split(tg.status_text, ' '))
order by 1
limit 10
```

```sql

select user_id, user_names, user_descriptions
 ,split(user_names, ' ') as name_tokens
 ,split(user_descriptions, ' ') as description_tokens
from impeachment_production.user_details_v3
limit 10


```

```sql

select
  user_id ,user_names ,user_descriptions
  ,community_id
  ,hashtag
FROM (
  SELECT
        user_id , screen_names , user_names, user_descriptions
        ,split(user_names, ' ') as name_tokens
        ,split(user_descriptions, ' ') as description_tokens
  FROM impeachment_production.user_details_v3
  -- LIMIT 10
) tk
JOIN impeachment_production.2_community_tags tg ON tg.hashtag in unnest(tk.description_tokens) -- or tg.hashtag in unnest(tk.name_tokens))
ORDER BY 1
LIMIT 10
```


```sql
select
  user_id -- ,user_names ,user_descriptions
  ,community_id
  ,count(distinct hashtag) as community_score
FROM (
  SELECT
        user_id -- , screen_names , user_names, user_descriptions
        ,split(user_names, ' ') as name_tokens
        ,split(user_descriptions, ' ') as description_tokens
  FROM impeachment_production.user_details_v3
  -- LIMIT 10
) tk
JOIN impeachment_production.2_community_tags tg ON tg.hashtag in unnest(tk.description_tokens) -- or tg.hashtag in unnest(tk.name_tokens))
GROUP BY 1,2
ORDER BY 1
LIMIT 10
```

```sql
DROP TABLE IF EXISTS impeachment_production.user_community_scores;
CREATE TABLE impeachment_production.user_community_scores as (
  SELECT
    user_id -- ,user_names ,user_descriptions
    ,community_id
    ,count(distinct hashtag) as community_score
  FROM (
    SELECT
          user_id -- , screen_names , user_names, user_descriptions
          ,split(user_names, ' ') as name_tokens
          ,split(user_descriptions, ' ') as description_tokens
    FROM impeachment_production.user_details_v3
    -- LIMIT 10
  ) tk
  JOIN impeachment_production.2_community_tags tg ON tg.hashtag in unnest(tk.description_tokens) -- or tg.hashtag in unnest(tk.name_tokens))
  GROUP BY 1,2
  ORDER BY 1
  --LIMIT 10
);
```

```sql
SELECT user_id, count(distinct community_id) as community_count --, any_value(user_descriptions)
FROM impeachment_production.user_community_scores
GROUP BY 1
-- HAVING count(distinct community_id) > 1 -- 541
HAVING count(distinct community_id) = 1 -- 137,460
```

There are 541 users (0.4%) who have at least one tag from more than one community. We could calculate a red/blue score between 0 and 1. But let's just exclude them for now. We can mix them back in later if desired.


```sql
DROP TABLE IF EXISTS impeachment_production.user_2_community_assignments;
CREATE TABLE impeachment_production.user_2_community_assignments as (
  -- users who are in only one community
  SELECT
    ucs.user_id, ucs.community_id , ucs.community_score
  FROM impeachment_production.user_community_scores ucs
  JOIN (
    SELECT user_id
    FROM impeachment_production.user_community_scores
    GROUP BY 1
    HAVING count(distinct community_id) = 1 -- 137,460
  ) polar_users ON polar_users.user_id = ucs.user_id
)
```

```sql
SELECT community_id ,count(distinct user_id) as user_count, sum(community_score) as community_score
FROM impeachment_production.user_2_community_assignments
GROUP BY 1
```



```sql
SELECT u.* ,l.community_id ,l.community_score
FROM impeachment_production.user_details_v3 u
JOIN impeachment_production.user_2_community_assignments l ON l.user_id = u.user_id
-- downloading as CSV, and charting the distributions in tableau
```
