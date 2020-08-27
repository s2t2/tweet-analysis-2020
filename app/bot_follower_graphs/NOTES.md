

How to filter records where a given screen name is in case-insensitively in an array of screen_names?

## BQ Queries



```sql
/*
SELECT DISTINCT bp.user_id
FROM `{self.dataset_address}.daily_bot_probabilities` bp
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
  FROM impeachment_production.daily_bot_probabilities bp
  WHERE bp.bot_probability >= 0.8
) b
LEFT JOIN impeachment_production.user_screen_names u ON CAST(u.user_id as int64) = b.user_id
WHERE u.screen_name is NULL
-- no rows. that means we can join these tables without dropping data
```


Filtering out user friends where there are no friend names (doesn't make sense to process them during follower graph compiltion):

```sql
select count(distinct user_id) as user_count
from impeachment_production.user_friends -- 3,600,545
-- where friend_count = 0
where ARRAY_LENGTH(friend_names) = 0
--> 283,559 records
```




Hmm these are a thorn:

```sql
select
  screen_name
, count(distinct user_id) as id_count
, array_agg(distinct user_id) as idlist
from impeachment_production.user_screen_names
group by 1
having id_count > 1
order by 2 desc

-- 3653102
-- 3653102
```



## PG Queries

### Filtering arrays

```sql
SELECT
   user_id
   ,screen_name
   ,friend_count
   ,friend_names
   ,'ACLU' = ANY (friend_names)
FROM user_friends
-- where 'ACLU' in friend_names
WHERE 'ACLU' = ANY (friend_names)
LIMIT 5
```

```sql
SELECT
 '{freind1, bot1, bot10}'::text[] as friend_names


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
select

 'ACLU' as bot_screen_name
 ,user_id as follower_id
 ,screen_name as follower_screen_name
 --,friend_count
 --,friend_names
from user_friends
where 'ACLU' ilike any(friend_names)
limit 500
```

## Pg Migrations

Export the "user_screen_names" and "daily_bot_probabilities" tables from BigQuery to CSV. Then import these into PG. (TODO: automate via pg pipeline)

```sql
-- ALTER TABLE user_screen_names ADD PRIMARY KEY (screen_name);
CREATE INDEX usn_index_sn ON user_screen_names (screen_name);
CREATE INDEX usn_index_uid ON user_screen_names (user_id);

```

Fixing...

```sql
/*
SELECT user_id, screen_name
from user_screen_names
limit 10
*/

select screen_name, idlist
from (
	select
	  	screen_name
		,count(distinct user_id) as id_count
		,array_agg(distinct user_id) as idlist
	from user_screen_names
	group by 1
	having count(distinct user_id) > 1
	order by 2 desc

) subq
where 549677007 = any(idlist)


```

```sql
CREATE TABLE IF NOT EXISTS screen_name_id_lookups as (

	SELECT
	  	screen_name
		,count(distinct user_id) as id_count
		,array_agg(distinct user_id) as idlist
	FROM user_screen_names
	group by 1
	-- having count(distinct user_id) > 1
	-- order by 2 desc

)
ALTER TABLE screen_name_id_lookups ADD PRIMARY KEY (screen_name);

```

Try something different:

```sql
SELECT
  b.user_id
  ,sn.screen_name
  ,count(distinct uf.user_id) as follower_count
  ,array_agg(distinct uf.user_id) as follower_ids
FROM (
	select user_id, count(start_date) as day_count
	from daily_bot_probabilities
	where bot_probability >= 0.8
	group by 1
	order by 2 desc
) b -- 24,150
LEFT JOIN user_screen_names sn on sn.user_id = b.user_id -- 24,150
LEFT JOIN user_friends uf on sn.screen_name ilike any(uf.friend_names)
GROUP BY 1,2
-- ORDER BY 2 desc
```
