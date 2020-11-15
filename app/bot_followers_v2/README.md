# Bot Followers v2

For the bots, how many (active) followers does each have, and who are they?


```sql
DROP TABLE IF EXISTS impeachment_production.user_followers_v2;
CREATE TABLE impeachment_production.user_followers_v2 as (
  SELECT
    cast(sn.user_id as int64) as user_id
    ,sn.screen_name
    ,cast(auff.user_id as int64) as follower_id
    ,auff.screen_name as follower_name
  FROM impeachment_production.user_screen_names sn
  JOIN impeachment_production.active_user_friends_flat auff ON upper(sn.screen_name) = upper(auff.friend_name)
  --WHERE sn.screen_name = "ACLU"
  --LIMIT 100
)
```
