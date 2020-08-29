

# Bot Follower Notes

> just using ACLU as an example screen name, not saying they're a bot or anything

## BQ Exploratory Queries

```sql
SELECT
   UPPER('ACLU') as bot_id
  ,user_id as follower_id
  ,UPPER(screen_name) as follower_screen_name
FROM impeachment_production.user_friends
CROSS JOIN UNNEST(friend_names) as friend_name WHERE UPPER(friend_name) = UPPER('ACLU')
```

```sql
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
  FROM impeachment_production.daily_bot_probabilities bp
  WHERE bp.bot_probability >= 0.8
) b
LEFT JOIN impeachment_production.user_screen_names u ON CAST(u.user_id as int64) = b.user_id
WHERE u.screen_name is NULL
-- no rows. that means we can join these tables without dropping data
```

Filtering out user friends where there are no friend names:

```sql
select count(distinct user_id) as user_count
from impeachment_production.user_friends -- 3,600,545
-- where friend_count = 0
where ARRAY_LENGTH(friend_names) = 0
--> 283,559 records
```

## PG Exploratory Queries

### Filtering Arrays

```sql
SELECT
   user_id
   ,screen_name
   ,friend_count
   ,friend_names
   ,'ACLU' = ANY (friend_names)
FROM user_friends
WHERE 'ACLU' = ANY (friend_names)
LIMIT 5
```

```sql
SELECT
 ,'bot1' = any('{freind1, bot1, bot10}'::text[]) as r1 -- TRUE
 ,'bot' = any('{freind1, bot1, bot10}'::text[]) as r2 -- FALSE
 ,'bot' like any('{freind1, bot1, bot10}'::text[]) as r2 -- FALSE
 ,'bot' like any('{freind1, bot1, bot10, BOT}'::text[]) as r2 -- FALSE
 ,'bot' ilike any('{freind1, bot1, bot10, BOT}'::text[]) as r2 -- TRUE
 ,'bot' ilike any('{freind1, bot1, bot10}'::text[]) as r2 -- FALSE

```

```sql
SELECT
 'ACLU' as screen_name

 ,'ACLU' ilike any('{user1, aclu}'::text[]) as r2 -- TRUE
 ,'ACLU' ilike any('{user1, ACLU}'::text[]) as r2 -- TRUE
 ,'ACLU' ilike any('{user1, acLu}'::text[]) as r2 -- TRUE

 ,'ACLU' ilike any('{user1, user2}'::text[]) as r1 -- FALSE
 ,'ACLU' ilike any('{user1, acluser1}'::text[]) as r3 -- FALSE
 ,'ACLU' ilike any('{user1, aclu_ser1}'::text[]) as r3 -- FALSE
 ,'ACLU' ilike any('{user1, aclu ser1}'::text[]) as r3 -- FALSE
```

```sql
SELECT
 'ACLU' as bot_screen_name
 ,user_id as follower_id
 ,screen_name as follower_screen_name
from user_friends
where 'ACLU' ilike any(friend_names)
limit 500
```

### Exploratory Migrations

Export the "user_screen_names" and "daily_bot_probabilities" tables from BigQuery to CSV. Then import these into PG.

```sql
-- ALTER TABLE user_screen_names ADD PRIMARY KEY (screen_name);
CREATE INDEX usn_index_sn ON user_screen_names (screen_name);
CREATE INDEX usn_index_uid ON user_screen_names (user_id);
```

```sql
CREATE INDEX bf80_bid ON bot_followers_above_80 (bot_id);
CREATE INDEX bf80_fid ON bot_followers_above_80 (follower_user_id);
```
