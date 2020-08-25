





some BQ queries. how to filter records where a given screen name is in a an array.

```sql
/*
SELECT DISTINCT bp.user_id
FROM `{self.dataset_address}.daily_bot_probabilities_temp` bp
WHERE bp.bot_probability >= {float(bot_min)}
*/



-- 3600545
select
  user_id
  ,screen_name
  ,friend_count
  --,ARRAY_LENGTH(friend_names) as friend_names_count
  -- ,friend_names

  ,ARRAY_TO_STRING(friend_names, " | ") as friend_namestr

  --,upper(ARRAY_TO_STRING(friend_names, " | ")) as friend_names_str
  --, upper(ARRAY_TO_STRING(friend_names, " | ")) like '% ACLU %' as is_follower -- doesn't work for first or last items in the list

  --,UPPER(ARRAY_TO_STRING(friend_names, " | "))

  --, SPLIT(UPPER(ARRAY_TO_STRING(friend_names, " | ")), "|")


   -- ,'280LMTD' in UNNEST(SPLIT(UPPER(ARRAY_TO_STRING(friend_names, " | ")), "|") ) -- true

from impeachment_production.user_friends
CROSS JOIN UNNEST(friend_names) as friend_name WHERE upper(friend_name) = 'ACLU'

--where user_id = '10335822'
-- where UPPER(ARRAY_TO_STRING(friend_names, " ")) like '%  %'

-- limit 10




```


More succinct:

```sql
-- just using ACLU as an example screen name, not saying they're a bot or anything
SELECT
   UPPER('ACLU') as bot_id
  ,user_id as follower_id
  ,UPPER(screen_name) as follower_screen_name
FROM impeachment_production.user_friends
CROSS JOIN UNNEST(friend_names) as friend_name WHERE UPPER(friend_name) = UPPER('ACLU')
```

```sql
-- just using ACLU as an example screen name, not saying they're a bot or anything
SELECT
    u.user_id
    ,u.screen_name
    ,subq.bot_screen_name
    ,subq.follower_id
    ,subq.follower_screen_name
FROM (
    SELECT
        UPPER('ACLU') as bot_screen_name
        ,user_id as follower_id
        ,UPPER(screen_name) as follower_screen_name
    FROM impeachment_production.user_friends
    CROSS JOIN UNNEST(friend_names) as friend_name WHERE UPPER(friend_name) = UPPER('ACLU')
) subq
LEFT JOIN impeachment_production.user_screen_names u ON u.screen_name = subq.bot_screen_name
WHERE  u.user_id is null
limit 10
```

Cross-checking bot user screen name lookups:

```sql
SELECT
  b.user_id as bot_id
  ,u.user_id
  ,u.screen_name as bot_screen_name
FROM (
  SELECT DISTINCT user_id
  FROM impeachment_production.daily_bot_probabilities_temp bp
  WHERE bp.bot_probability >= 0.8
) b
LEFT JOIN impeachment_production.user_screen_names u ON CAST(u.user_id as int64) = b.user_id
WHERE u.screen_name is NULL
-- no rows. that means we can join these tables without dropping data
```
