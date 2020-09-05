# Summary

For each user, we examined their profiles to see if any of the community tags appear in their user names or descriptions. Of the original 3.6M users, 138,001 had community tag matches. Of the 138,001 users, 541 (0.4%) had tags from more than one community, and were excluded. The distribution of the remaining 137,460 users is below:

community_id	| user_count	| community_score
---             | ---           | ---
0	            | 59792	        | 90645
1	            | 77668	        | 166383

For training the model, we will pick a random sample of equal size from each of these groups.

# Notes

## Dataset Labeling

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


Add mutually exclusive hashtags used by members of each community.

```csv
community_id,hashtag,description
0, #LEFTTAG,
0, #LEFTTAG2,
1, #RIGHTTAG, It means this
1, #RIGHTTAG2
```

Upload the CSV to BigQuery as the "2_community_tags" table, where "2" is the number of communities you're using.


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



## Stratified Random Sampling

```sql
-- h/t: https://calogica.com/sql/2018/07/21/random-sampling-within-groups-snowflake-sql.html
SELECT
  community_id,
  user_id,
  row_number() OVER (
    PARTITION BY community_id
    ORDER BY RAND()
   ) as random_sort
FROM impeachment_production.user_2_community_assignments
order by 3,1
```

```sql
SELECT
  community_id
  ,sort_order
  ,user_id
FROM (
  SELECT
    community_id,
    user_id,
    row_number() OVER (
      PARTITION BY community_id
      ORDER BY RAND()
     ) as sort_order
  FROM impeachment_production.user_2_community_assignments
)
WHERE sort_order <= 3
ORDER BY 2,1
```


community_id	| sort_order |	user_id
--- | --- | ---
0	| 1	| userA
1	| 1	| userB
0	| 2	| userC
1	| 2	| userD
0	| 3	| userE
1	| 3	| userF


Now we're going to get a stratified random sample of their tweets...

```sql
SELECT l.community_id ,count(distinct l.user_id) as user_count, sum(l.community_score) as profile_tag_count
  ,count(distinct t.status_id) as tweet_count
FROM impeachment_production.user_2_community_assignments l
JOIN impeachment_production.tweets t ON cast(t.user_id as int64) = l.user_id
GROUP BY 1
```

```sql
SELECT
  ul.user_id
  ,ul.community_id
  --,ul.community_score
  ,t.status_id
  ,t.status_text
  ,t.created_at
FROM impeachment_production.user_2_community_assignments ul
JOIN impeachment_production.tweets t ON cast(t.user_id as int64) = ul.user_id
WHERE ul.community_id = 1 -- 0
LIMIT 10
-- post to sheets
```

```sql
DROP TABLE IF EXISTS impeachment_production.2_community_labeled_tweets;
CREATE TABLE impeachment_production.2_community_labeled_tweets as (
  SELECT
    ul.user_id
    ,ul.community_id
    ,ul.community_score
    ,t.status_id
    ,t.status_text
    ,t.created_at
  FROM impeachment_production.user_2_community_assignments ul
  JOIN impeachment_production.tweets t ON cast(t.user_id as int64) = ul.user_id
);
```


```sql
SELECT
  community_id
  ,sort_order
  ,user_id
  ,status_id
  ,status_text
FROM (
  SELECT
    community_id
    ,user_id
    ,status_id
    ,status_text
    ,row_number() OVER (
      PARTITION BY community_id -- and day of status created_at
      ORDER BY RAND()
    ) as sort_order
  FROM impeachment_production.2_community_labeled_tweets
)
WHERE sort_order <= 3
-- ORDER BY 2,1

-- Resources exceeded during query execution: The query could not be executed in the allotted memory. Peak usage: 129% of limit. Top memory consumer(s): sort operations used for analytic OVER() clauses: 98% other/unattributed: 2%
```

Hmm OK. We can partition them in Python. Should be able to hold all in memory.
