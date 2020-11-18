# Friend / Follower Networks


## User Friends v2

```sql
SELECT
  count(distinct uff.friend_name) as friend_names -- 2,972,316
  ,count(distinct usn.user_id) as friend_id_matches -- 2,971,946
FROM impeachment_production.active_user_friends_flat uff
LEFT JOIN impeachment_production.user_screen_names usn ON usn.screen_name = uff.friend_name

```

... 99.99% id match rate. amazing. this should be good then.


```sql
DROP TABLE IF EXISTS impeachment_production.active_user_friends_flat_v2;
CREATE TABLE IF NOT EXISTS impeachment_production.active_user_friends_flat_v2 as (
SELECT
  cast(uff.user_id as int64) as user_id
  ,uff.screen_name
  ,cast(usn.user_id as int64) as friend_id
  ,uff.friend_name
FROM impeachment_production.active_user_friends_flat uff
LEFT JOIN impeachment_production.user_screen_names usn ON usn.screen_name = uff.friend_name
--LIMIT 10
)
```




## Active Friend BH

```sql
DROP TABLE IF EXISTS impeachment_production.active_user_friends_bh_v2;
CREATE TABLE IF NOT EXISTS impeachment_production.active_user_friends_bh_v2 as (
  SELECT
     user_id
    ,count(distinct friend_id) as friend_count
    ,count(distinct case when friend_is_bot = true then friend_id end) as friend_count_b
    ,count(distinct case when friend_is_bot = false then friend_id end) as friend_count_h
    ,array_agg(distinct case when friend_is_bot = true then friend_id end) as friend_ids_b
    ,array_agg(distinct case when friend_is_bot = false then friend_id end) as friend_ids_h
  FROM (
    SELECT
      uff.user_id
      ,uff.screen_name
      ,uff.friend_id
      ,uff.friend_name
      ,CASE WHEN fbu.user_id IS NOT NULL THEN true ELSE false END friend_is_bot
    FROM impeachment_production.active_user_friends_flat_v2 uff
    LEFT JOIN impeachment_production.bots_above_80_v2 fbu ON fbu.user_id = uff.follower_id
    WHERE uff.friend_id is not null
    --LIMIT 10
  ) zz
  GROUP BY 1
  --LIMIT 10
)
```




## F/F Networks

For active users only, with flags for bot, opinion community, q, etc.

```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v6;
CREATE TABLE IF NOT EXISTS impeachment_production.user_details_v6 as (
SELECT
  ud.user_id
  ,extract(date from ud.user_created_at) as created_on
  ,ud.screen_name_count
  ,ud.screen_names

  ,ud.is_bot
  ,ud.community_id as bot_rt_network

  ,case when q.q_status_count > 0 then true else false end is_q
  ,q.q_status_count

  ,ud.status_count
  ,ud.rt_count

  ,ud.avg_score_lr
  ,ud.avg_score_nb
  ,ud.avg_score_bert
  ,cast(round(coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr)) as int64) as opinion_community

  ,ufl.follower_count
  ,ufl.follower_count_b --,ufl.follower_ids_b
  ,ufl.follower_count_h --,ufl.follower_ids_h

  ,ufr.friend_count
  ,ufr.friend_count_b --,ufr.friend_ids_b
  ,ufr.friend_count_h --,ufr.friend_ids_b

FROM impeachment_production.user_details_v4 ud
LEFT JOIN impeachment_production.q_users_v2 q ON q.user_id = ud.user_id
LEFT JOIN impeachment_production.active_followers_bh_v2 ufl ON ud.user_id = ufl.user_id
LEFT JOIN impeachment_production.active_user_friends_bh_v2 ufr ON ud.user_id = ufr.user_id
--WHERE coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) <> 0.5
--LIMIT 10
)

```


```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v6_full;
CREATE TABLE IF NOT EXISTS impeachment_production.user_details_v6_full as (
SELECT
  ud.user_id
  ,extract(date from ud.user_created_at) as created_on
  ,ud.screen_name_count
  ,ud.screen_names

  ,ud.is_bot
  ,ud.community_id as bot_rt_network

  ,case when q.q_status_count > 0 then true else false end is_q
  ,q.q_status_count

  ,ud.status_count
  ,ud.rt_count

  ,ud.avg_score_lr
  ,ud.avg_score_nb
  ,ud.avg_score_bert
  ,cast(round(coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr)) as int64) as opinion_community

  ,ufl.follower_count
  ,ufl.follower_count_b
  ,ufl.follower_count_h
  ,ufl.follower_ids_b
  ,ufl.follower_ids_h

  ,ufr.friend_count
  ,ufr.friend_count_b
  ,ufr.friend_count_h
  ,ufr.friend_ids_b
  ,ufr.friend_ids_h

FROM impeachment_production.user_details_v4 ud
LEFT JOIN impeachment_production.q_users_v2 q ON q.user_id = ud.user_id
LEFT JOIN impeachment_production.active_followers_bh_v2 ufl ON ud.user_id = ufl.user_id
LEFT JOIN impeachment_production.active_user_friends_bh_v2 ufr ON ud.user_id = ufr.user_id
--WHERE coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) <> 0.5
--LIMIT 10
)
```
